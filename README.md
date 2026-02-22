# 📊 CSV Data Profiler

A Python CLI tool that generates comprehensive data profile reports for CSV files. Quickly analyze your data's structure, quality, and statistics without touching memory-intensive tools.

These are the two recommended ways to run the CSV Data Profiler: (A) directly from the repo (no installation) or (B) install the package (run from anywhere).

## ✨ Features

- **Automatic Type Detection**: Infers column data types (int, float, string, boolean, mixed)
- **Comprehensive Metrics**: For each column, generates:
  - Null count and percentage
  - Distinct value count
  - Duplicate row detection
  - Min/Max values (numeric columns)
  - Mean, Median, Standard Deviation (numeric columns)
  - Top 5 most frequent values with counts
- **Multiple Output Formats**:
  - **Table**: Pretty-printed console output
  - **HTML**: Beautiful standalone report with interactive styling
  - **JSON**: Machine-readable output for programmatic use
- **Memory Efficient**: Streams large files in chunks (default 10K rows)
- **Robust Error Handling**: Gracefully handles edge cases (empty files, all-null columns, mixed types)
- **No Configuration Required**: Works with any CSV file out of the box

## 📋 Requirements

- Python 3.7+
- Click (for CLI interface)

## 🚀 Quick Start (explicit step-by-step)

Below are two explicit, numbered workflows you can copy into docs or share with teammates. Pick A (run from the repo) if you want zero install friction; pick B (install) if you want a persistent, shareable command.

A) Run directly from the repository (no install)

1. Clone the repo and change into it:

```bash
git clone https://github.com/molly-scheitler/File-Profiler-Tool.git
cd File-Profiler-Tool
```

2. (Optional) Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
# Windows (cmd.exe)
.venv\Scripts\activate
# Windows PowerShell (may require changing execution policy):
.\.venv\Scripts\Activate.ps1
```

3. Run the profiler using Python's module mode (works from repo root):

```bash
# basic table output to terminal
python -m csv_profiler /absolute/path/to/your.csv

# write HTML report
python -m csv_profiler /absolute/path/to/your.csv --format html --output report.html

# write JSON summary
python -m csv_profiler /absolute/path/to/your.csv --format json --output summary.json
```

4. Inspect help and options:

```bash
python -m csv_profiler --help
```

Notes for this flow:
- Always run from the repository root (the folder that contains `csv_profiler/` and `README.md`).
- If your CSV path has spaces, quote the path.
- You can run on JSON or Parquet files too (Parquet requires optional `pandas` + `pyarrow`).

B) Install the package (run from anywhere)

2. (Optional but recommended) create & activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
# Windows (cmd.exe)
.venv\Scripts\activate
# Windows PowerShell (may require changing execution policy):
.\.venv\Scripts\Activate.ps1
```

2. Install runtime dependencies and the package (editable for development):

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

3. Run using the installed console script (or `python -m`):

```bash
# short console script (after install)
csv-profiler /absolute/path/to/your.csv --format table

# or equivalent module mode
python -m csv_profiler /absolute/path/to/your.csv --format html --output report.html
```

4. Validate against a schema (example):

```bash
csv-profiler /path/to/data.csv --schema schema.json --validate --format json --output schema_validation.json
```

Notes for this flow:
- If `csv-profiler` isn't found after install, make sure the virtualenv is active or your PATH includes the environment's `bin` directory.
- Editable installs (`-e`) are useful during development — changes in `csv_profiler/` are picked up without re-installing.

Common options and examples

```bash
# Format: table (default), json, html
--format table|json|html

# Output file (optional)
--output /path/to/result.html

# Schema validation (JSON file mapping column->type)
--schema schema.json --validate

# Chunk size for streaming large files
--chunk-size 50000
```

Quick copy-ready snippet for docs

```bash
# Run without installing (from repo root)
python -m csv_profiler /full/path/to/data.csv --format html --output report.html

# Or install and run from anywhere
python -m pip install -e .
csv-profiler /full/path/to/data.csv --format html --output report.html
```

## 💻 Usage

### View Results in Console (Table Format)

```bash
python -m csv_profiler customers.csv
```

### Save as HTML Report (Recommended for Sharing)

```bash
python -m csv_profiler customers.csv -f html -o report.html
open report.html  # macOS
# or: start report.html (Windows) / xdg-open report.html (Linux)
```

### Export as JSON (For Data Pipelines)

```bash
python -m csv_profiler customers.csv -f json -o report.json
```

### Handle Large Files (Custom Chunk Size)

```bash
python -m csv_profiler massive_dataset.csv --chunk-size 50000
```

## 📊 Output Formats

### Table Format (Console)

Perfect for quick analysis in the terminal:

```
====================================================================================================
CSV DATA PROFILE REPORT
====================================================================================================

File: data.csv
Generated: 2025-02-18 10:23:45
Total Rows: 1000
Total Columns: 5

----------------------------------------------------------------------------------------------------
Column: name | Type: string
----------------------------------------------------------------------------------------------------
  Total Rows:        1000
  Null Count:        5 (0.5%)
  Distinct Values:   995
  Duplicate Rows:    0

  Most Frequent Values:
    1. 'Alice'                                  (count: 3, 0.30%)
    2. 'Bob'                                    (count: 2, 0.20%)
    ...
```

### HTML Format

Beautiful browser-friendly report with:
- Color-coded metrics
- Responsive grid layout
- Numeric statistics visualization
- Full most-frequent values list

Open the generated `.html` file in any browser.

### JSON Format

Perfect for programmatic processing:

```json
{
  "file": "/path/to/data.csv",
  "total_rows": 1000,
  "total_columns": 5,
  "columns": [
    {
      "name": "age",
      "data_type": "int",
      "total_rows": 1000,
      "null_count": 5,
      "null_percentage": 0.5,
      "duplicate_rows": 100,
      "distinct_values": 895,
      "most_frequent": [
        ["28", 45],
        ["30", 42]
      ],
      "min_value": 18,
      "max_value": 85,
      "mean": 42.5,
      "median": 43.0,
      "std_dev": 15.3
    },
    ...
  ]
}
```

## 🧪 Running Tests

Run the comprehensive test suite (23 test cases):

```bash
python -m pytest tests/test_profiler.py -v
```

Or using unittest:

```bash
python -m unittest tests.test_profiler -v
```

### Test Coverage

Tests cover:
- File validation and error handling
- Mixed data type detection
- Null value handling
- Empty files and all-null columns
- Distinct value counting
- Numeric statistics calculation
- Most frequent value extraction
- Large file handling (1000+ rows)
- Type inference (int, float, string, boolean)

## 📁 Project Structure

```
csv_profiler/
├── __init__.py              # Package initialization
├── __main__.py              # CLI entry point
├── cli.py                   # CLI interface with Click
├── profiler.py              # Core profiling logic
├── reports.py               # Output formatters (table, HTML, JSON)
├── tests/
│   ├── __init__.py
│   ├── test_profiler.py     # Unit tests (23 test cases)
│   ├── sample_data.csv      # Test fixture: normal CSV
│   ├── sample_empty.csv     # Test fixture: empty file
│   └── sample_all_nulls.csv # Test fixture: all-null column
└── README.md                # This file
```

## 🛠️ How It Works

1. **Initialization**: Validates CSV file exists and is readable
2. **Streaming Read**: Reads CSV in chunks to handle large files efficiently
3. **Type Inference**: For each value, infers its data type
4. **Statistics Calculation**: Computes all required metrics per column
5. **Report Generation**: Formats results according to chosen output format
6. **Output**: Displays or saves the report

### Type Detection Logic

- **Null**: Empty strings or missing values
- **Integer**: Values parseable as whole numbers
- **Float**: Values parseable as decimal numbers
- **Boolean**: `true`, `false`, `yes`, `no`, `1`, `0`
- **String**: Everything else
- **Mixed**: Columns with multiple non-null types

### Edge Case Handling

| Scenario | Behavior |
|----------|----------|
| Empty file (headers only) | All columns show 0 total_rows |
| All-null column | 100% null percentage, 0 distinct values |
| Mixed data types | Marked as "mixed" type, stats computed on numeric values only |
| Very large file | Streamed in configurable chunks, no full load into memory |
| Missing values | Counted as nulls, excluded from statistics |
| Division by zero | Safely handled (e.g., null% when 0 rows) |

## ⚡ Performance

- **Small files** (< 10MB): ~1-2 seconds
- **Medium files** (10-100MB): ~5-10 seconds
- **Large files** (> 100MB): Scales linearly with configurable chunk size
- **Memory usage**: O(chunk_size) instead of O(file_size)

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'csv_profiler'"

**Cause**: You're not in the repository root directory.

**Solution**: Navigate to the folder where `csv_profiler/` lives:
```bash
cd /path/to/File-Profiler-Tool
python -m csv_profiler your_file.csv
```

If you're inside the `csv_profiler/` folder, go up one level:
```bash
cd ..
python -m csv_profiler your_file.csv
```

### "Error: Invalid value for 'FILEPATH': Path 'file.csv' does not exist"

**Cause**: The file path is wrong or relative to the wrong directory.

**Solution**: Use an absolute path:
```bash
python -m csv_profiler /Users/yourname/Downloads/file.csv
python -m csv_profiler "C:\Users\yourname\Downloads\file.csv"  # Windows
```

Or navigate to the file's directory first:
```bash
cd /path/with/your/file
python -m csv_profiler file.csv
```

### "ModuleNotFoundError: No module named 'click'"

**Cause**: Click is not installed.

**Solution**: Install it:
```bash
pip install click
# or from requirements.txt
pip install -r requirements.txt
```

### On macOS/Linux: "command not found: python"

**Cause**: Python might be installed as `python3`.

**Solution**: Use `python3` explicitly:
```bash
python3 -m csv_profiler file.csv
```

## 💡 Example Workflow

### Analyzing Customer Data

```bash
# Quick preview in console
python -m csv_profiler customers.csv

# Generate HTML report for executives
python -m csv_profiler customers.csv -f html -o customer_analysis.html

# Export data quality metrics as JSON for your data warehouse
python -m csv_profiler customers.csv -f json -o metrics.json
```

### Data Quality Check

```bash
# Profile before importing to database
python -m csv_profiler sales_data.csv

# Look for:
# - High null percentages (data quality issues)
# - Mixed types in numeric columns (formatting issues)
# - Unexpected value distributions
```

## 📝 Sample Output

For `sample_data.csv`:
```
====================================================================================================
CSV DATA PROFILE REPORT
====================================================================================================

File: sample_data.csv
Generated: 2025-02-18 10:42:15
Total Rows: 10
Total Columns: 5

----------------------------------------------------------------------------------------------------
Column: name | Type: string
----------------------------------------------------------------------------------------------------
  Total Rows:        10
  Null Count:        1 (10.0%)
  Distinct Values:   9
  Duplicate Rows:    0

  Most Frequent Values:
    1. 'Alice'                                  (count: 1, 10.00%)
    2. 'Bob'                                    (count: 1, 10.00%)

----------------------------------------------------------------------------------------------------
Column: age | Type: int
----------------------------------------------------------------------------------------------------
  Total Rows:        10
  Null Count:        0 (0.0%)
  Distinct Values:   8
  Duplicate Rows:    2

  Numeric Statistics:
    Min:             28
    Max:             45
    Mean:            32.1
    Median:          31.0
    Std Dev:         5.32

  Most Frequent Values:
    1. '28'                                     (count: 2, 20.00%)
    2. '34'                                     (count: 2, 20.00%)
```

## � AI Development Notes: Copilot Assistance

**What GitHub Copilot Helped With:**
- Generated the complete project structure including all Python modules (cli.py, reports.py, __main__.py) with correct imports and function signatures
- Synthesized a comprehensive 390-line README with installation instructions, usage examples, troubleshooting, and edge case documentation
- Wrote beautiful, production-ready HTML report formatting with modern CSS styling (gradients, responsive grid, color schemes)
- Generated 20+ unit test cases covering normal flows, edge cases (empty files, all-null columns), and large file handling
- Provided JSON and table formatting logic that handles null values, type conversions, and numerical statistics correctly

**Where Copilot Fell Short:**
- Required manual debugging when Click dependency wasn't installed for the correct Python version (Copilot assumed it was pre-installed)
- Didn't catch that `python -m csv_profiler` wouldn't work without proper package structure until runtime testing
- HTML output required tuning and style adjustments for better visual hierarchy (Copilot generated working HTML but with less polish initially)
- Test file paths required adjustment (Copilot generated hardcoded paths that needed to be relative)
- Copilot didn't proactively suggest the Git setup, requirements.txt file, or assignment deliverable structure—these were added after the fact based on assignment requirements

**What Surprised Me:**
- I was surprised at how confidently Copilot generated large sections of the project—such as the initial CLI structure, HTML layout, and the detailed README text. It often produced results that were close to production‑ready on the first pass.
- It also surprised me how well Copilot could infer patterns from the existing code; for example, when I added a new feature, Copilot began suggesting consistent updates across related files without being explicitly told.
- I did not expect Copilot to create such thorough unit tests so quickly. Even though some needed adjustments (like fixing hardcoded paths), the coverage it generated on the first attempt was far broader than I anticipated.
- I also didn’t expect Copilot to generate such polished explanations and documentation for user‑facing sections (usage examples, help text, troubleshooting). This made writing the README significantly faster than normal.

**Overall**: Copilot was exceptional for code generation, boilerplate, and documentation. Manual testing and environment setup were necessary for production readiness. The tool went from concept to fully functional with 20 passing tests in a single session.

## �🤝 Contributing

Feel free to extend this tool! Some ideas:
- Add more output formats (PDF, Excel, Parquet)
- Implement data quality scoring
- Add correlation analysis between columns
- Support for compressed files (gzip, bzip2)
- Database export functionality

## 📄 License

MIT License - Feel free to use and modify

## 📧 Support

If you encounter issues or have questions:
1. Check the Troubleshooting section
2. Review test cases for usage examples
3. Examine sample CSV files in `tests/`

---

**Happy profiling! 📊**
