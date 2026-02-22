"""Core data profiling module for CSV files."""

import os
import csv
from typing import Dict, List, Any, Tuple, Optional
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
import re
import math


@dataclass
class ColumnProfile:
    """Data structure for a column's profile."""
    name: str
    data_type: str
    total_rows: int
    null_count: int
    null_percentage: float
    duplicate_rows: int
    distinct_values: int
    most_frequent: List[Tuple[str, int]]
    min_value: Optional[Any]
    max_value: Optional[Any]
    mean: Optional[float]
    median: Optional[float]
    std_dev: Optional[float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "name": self.name,
            "data_type": self.data_type,
            "total_rows": self.total_rows,
            "null_count": self.null_count,
            "null_percentage": round(self.null_percentage, 2),
            "duplicate_rows": self.duplicate_rows,
            "distinct_values": self.distinct_values,
            "most_frequent": self.most_frequent,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "mean": round(self.mean, 4) if self.mean is not None else None,
            "median": round(self.median, 4) if self.median is not None else None,
            "std_dev": round(self.std_dev, 4) if self.std_dev is not None else None,
        }


class DataProfiler:
    """Main profiler class for analyzing CSV files."""
    
    def __init__(self, filepath: str, chunk_size: int = 10000):
        """Initialize the profiler."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        if not filepath.lower().endswith('.csv'):
            raise ValueError("File must be a CSV file (.csv)")
        
        self.filepath = filepath
        self.chunk_size = chunk_size
        self.profiles: Dict[str, ColumnProfile] = {}
        self.total_rows = 0
        self.headers: List[str] = []
        self.pii_flags: Dict[str, List[str]] = defaultdict(list)
        self.correlation_matrix: Dict[Tuple[str, str], Optional[float]] = {}
    
    def _infer_type(self, value: str) -> str:
        """Infer the type of a value."""
        if value is None or value == "":
            return "null"
        
        value_stripped = str(value).strip()
        
        # Try integer
        try:
            int(value_stripped)
            return "int"
        except ValueError:
            pass
        
        # Try float
        try:
            float(value_stripped)
            return "float"
        except ValueError:
            pass
        
        # Try boolean
        if value_stripped.lower() in ("true", "false", "yes", "no", "1", "0"):
            return "bool"
        
        return "string"

    def _looks_like_ssn(self, s: str) -> bool:
        # U.S. SSN patterns: 123-45-6789 or 9 digits
        if not s:
            return False
        s = s.strip()
        return bool(re.fullmatch(r"\d{3}-\d{2}-\d{4}", s) or re.fullmatch(r"\d{9}", s))

    def _looks_like_npi(self, s: str) -> bool:
        # NPI is 10-digit numeric identifier
        if not s:
            return False
        return bool(re.fullmatch(r"\d{10}", s.strip()))

    def _looks_like_email(self, s: str) -> bool:
        if not s:
            return False
        return bool(re.search(r"[^@\s]+@[^@\s]+\.[^@\s]+", s))

    def _looks_like_phone(self, s: str) -> bool:
        if not s:
            return False
        # simple phone detection
        return bool(re.search(r"\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4}", s))
    
    def _is_numeric(self, inferred_type: str) -> bool:
        """Check if a type is numeric."""
        return inferred_type in ("int", "float")
    
    def _parse_value(self, value: str, value_type: str) -> Optional[float]:
        """Parse a value to its numeric representation."""
        if not value or value.strip() == "":
            return None
        
        if value_type == "int":
            try:
                return float(int(value))
            except ValueError:
                return None
        elif value_type == "float":
            try:
                return float(value)
            except ValueError:
                return None
        
        return None
    
    def profile(self) -> Dict[str, ColumnProfile]:
        """Generate a profile of the CSV file."""
        col_types: Dict[str, List[str]] = defaultdict(list)
        col_values: Dict[str, List[str]] = defaultdict(list)
        null_counts: Dict[str, int] = defaultdict(int)
        value_counts: Dict[str, Counter] = defaultdict(Counter)
        numeric_samples: Dict[str, List[float]] = defaultdict(list)
        
        try:
            ext = os.path.splitext(self.filepath)[1].lower()
            # Support CSV, JSON, newline-delimited JSON, and Parquet (optional)
            if ext == '.csv':
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)

                    if reader.fieldnames is None:
                        self.headers = []
                        return {}

                    self.headers = list(reader.fieldnames)

                    for header in self.headers:
                        col_types[header] = []
                        col_values[header] = []

                    row_count = 0
                    for row in reader:
                        row_count += 1

                        for header in self.headers:
                            value = row.get(header, "")

                            if value is None or value == "":
                                null_counts[header] += 1
                                col_types[header].append("null")
                            else:
                                inferred_type = self._infer_type(value)
                                col_types[header].append(inferred_type)
                                col_values[header].append(value)
                                value_counts[header][value] += 1
                                if self._is_numeric(inferred_type):
                                    parsed = self._parse_value(value, "float")
                                    if parsed is not None:
                                        numeric_samples[header].append(parsed)

                    self.total_rows = row_count

            elif ext == '.json':
                # support either a JSON array of objects or newline-delimited JSON
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    first = f.readline().strip()
                    f.seek(0)
                    data = None
                    if first.startswith('['):
                        data = json.load(f)
                    else:
                        # ndjson
                        data = [json.loads(line) for line in f if line.strip()]

                    if not data:
                        self.headers = []
                        return {}

                    self.headers = list(data[0].keys())
                    for header in self.headers:
                        col_types[header] = []
                        col_values[header] = []

                    row_count = 0
                    for row in data:
                        row_count += 1
                        for header in self.headers:
                            value = row.get(header, "")
                            if value is None or value == "":
                                null_counts[header] += 1
                                col_types[header].append("null")
                            else:
                                inferred_type = self._infer_type(str(value))
                                col_types[header].append(inferred_type)
                                col_values[header].append(str(value))
                                value_counts[header][str(value)] += 1
                                if self._is_numeric(inferred_type):
                                    parsed = self._parse_value(str(value), "float")
                                    if parsed is not None:
                                        numeric_samples[header].append(parsed)

                    self.total_rows = row_count

            elif ext in ('.parquet', '.pq'):
                # optional dependency
                try:
                    import pandas as _pd
                except Exception:
                    raise RuntimeError("Reading Parquet requires 'pandas' and optional 'pyarrow'. Please install them to proceed.")

                df = _pd.read_parquet(self.filepath)
                if df.empty:
                    self.headers = list(df.columns)
                    return {}

                self.headers = list(df.columns)
                for header in self.headers:
                    col_types[header] = []
                    col_values[header] = []

                row_count = 0
                for _, row in df.iterrows():
                    row_count += 1
                    for header in self.headers:
                        value = row.get(header, "")
                        if value is None or (isinstance(value, float) and math.isnan(value)) or value == "":
                            null_counts[header] += 1
                            col_types[header].append("null")
                        else:
                            inferred_type = self._infer_type(str(value))
                            col_types[header].append(inferred_type)
                            col_values[header].append(str(value))
                            value_counts[header][str(value)] += 1
                            if self._is_numeric(inferred_type):
                                parsed = self._parse_value(str(value), "float")
                                if parsed is not None:
                                    numeric_samples[header].append(parsed)

                self.total_rows = row_count
            else:
                raise ValueError("Unsupported file type. Supported: .csv, .json, .parquet")

        except Exception as e:
            raise RuntimeError(f"Error reading file: {str(e)}")
        
        if self.total_rows == 0:
            return self._create_empty_profiles()
        
        # Calculate statistics
        self.profiles = {}
        
        for header in self.headers:
            types = col_types[header]
            values = col_values[header]
            null_count = null_counts[header]
            
            # Determine primary data type
            non_null_types = [t for t in types if t != "null"]
            if not non_null_types:
                primary_type = "null"
            else:
                type_counts = Counter(non_null_types)
                numeric_types = [t for t in non_null_types if t in ("int", "float")]
                if len(numeric_types) == len(non_null_types) and numeric_types:
                    primary_type = "numeric"
                elif len(type_counts) > 1:
                    primary_type = "mixed"
                else:
                    primary_type = type_counts.most_common(1)[0][0]
            
            # Get most frequent values
            most_frequent = value_counts[header].most_common(5)
            
            # Calculate numeric statistics
            numeric_values = []
            if self._is_numeric(primary_type) or primary_type == "numeric":
                for value in values:
                    parsed = self._parse_value(value, "float")
                    if parsed is not None:
                        numeric_values.append(parsed)
            
            min_val = None
            max_val = None
            mean_val = None
            median_val = None
            std_dev_val = None
            
            if numeric_values:
                min_val = min(numeric_values)
                max_val = max(numeric_values)
                mean_val = statistics.mean(numeric_values)
                median_val = statistics.median(numeric_values)
                
                if len(numeric_values) > 1:
                    std_dev_val = statistics.stdev(numeric_values)
                else:
                    std_dev_val = 0.0
            
            # Count duplicate rows
            duplicate_rows = self.total_rows - len(set(values)) if values else 0
            
            null_pct = (null_count / self.total_rows * 100) if self.total_rows > 0 else 0
            
            profile = ColumnProfile(
                name=header,
                data_type=primary_type,
                total_rows=self.total_rows,
                null_count=null_count,
                null_percentage=null_pct,
                duplicate_rows=duplicate_rows,
                distinct_values=len(value_counts[header]),
                most_frequent=most_frequent,
                min_value=min_val,
                max_value=max_val,
                mean=mean_val,
                median=median_val,
                std_dev=std_dev_val,
            )
            
            self.profiles[header] = profile

            # PII detection heuristics (based on header name and sample values)
            flags = []
            lname = header.lower()
            if 'name' in lname or 'full_name' in lname or 'first' in lname or 'last' in lname:
                flags.append('possible_name')
            if 'ssn' in lname or any(self._looks_like_ssn(v) for v in col_values[header][:20]):
                flags.append('ssn')
            if 'npi' in lname or any(self._looks_like_npi(v) for v in col_values[header][:20]):
                flags.append('npi')
            if 'email' in lname or any(self._looks_like_email(v) for v in col_values[header][:20]):
                flags.append('email')
            if 'phone' in lname or any(self._looks_like_phone(v) for v in col_values[header][:20]):
                flags.append('phone')

            if flags:
                self.pii_flags[header] = flags

        # Compute correlation matrix for numeric columns
        numeric_cols = [h for h in self.headers if h in numeric_samples and len(numeric_samples[h]) > 1]
        for i, a in enumerate(numeric_cols):
            for j, b in enumerate(numeric_cols):
                if j <= i:
                    # symmetric
                    continue
                xa = numeric_samples[a]
                xb = numeric_samples[b]
                # align lengths by taking min length samples if they differ
                n = min(len(xa), len(xb))
                if n < 2:
                    corr = None
                else:
                    xa_s = xa[:n]
                    xb_s = xb[:n]
                    mean_x = statistics.mean(xa_s)
                    mean_y = statistics.mean(xb_s)
                    cov = sum((u - mean_x) * (v - mean_y) for u, v in zip(xa_s, xb_s)) / (n - 1)
                    stdev_x = statistics.stdev(xa_s)
                    stdev_y = statistics.stdev(xb_s)
                    corr = cov / (stdev_x * stdev_y) if stdev_x > 0 and stdev_y > 0 else None

                self.correlation_matrix[(a, b)] = corr
                self.correlation_matrix[(b, a)] = corr
        
        return self.profiles
    
    def _create_empty_profiles(self) -> Dict[str, ColumnProfile]:
        """Create empty profiles for headers in an empty file."""
        profiles = {}
        for header in self.headers:
            profiles[header] = ColumnProfile(
                name=header,
                data_type="unknown",
                total_rows=0,
                null_count=0,
                null_percentage=0.0,
                duplicate_rows=0,
                distinct_values=0,
                most_frequent=[],
                min_value=None,
                max_value=None,
                mean=None,
                median=None,
                std_dev=None,
            )
        return profiles
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the profiling results."""
        return {
            "file": self.filepath,
            "total_rows": self.total_rows,
            "total_columns": len(self.headers),
            "columns": [p.to_dict() for p in self.profiles.values()],
            "pii_flags": self.pii_flags,
            "correlation_matrix": {f"{a}__{b}": (None if v is None else round(v, 4)) for (a, b), v in self.correlation_matrix.items()},
        }