"""Unit tests for CSV Data Profiler."""

import unittest
import os
import tempfile
import csv
from pathlib import Path
import sys

# Add parent directory to path to import profiler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from profiler import DataProfiler, ColumnProfile


class TestDataProfiler(unittest.TestCase):
    """Test cases for DataProfiler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.sample_data_path = os.path.join(self.test_dir, 'sample_data.csv')
        self.sample_empty_path = os.path.join(self.test_dir, 'sample_empty.csv')
        self.sample_all_nulls_path = os.path.join(self.test_dir, 'sample_all_nulls.csv')
    
    def test_profiler_initialization(self):
        """Test that profiler initializes correctly with valid file."""
        profiler = DataProfiler(self.sample_data_path)
        self.assertEqual(profiler.filepath, self.sample_data_path)
        self.assertEqual(profiler.chunk_size, 10000)
    
    def test_profiler_file_not_found(self):
        """Test that profiler raises FileNotFoundError for non-existent file."""
        with self.assertRaises(FileNotFoundError):
            DataProfiler('/nonexistent/path/file.csv')
    
    def test_profiler_not_csv_file(self):
        """Test that profiler raises ValueError for non-CSV files."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_file = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                DataProfiler(temp_file)
            self.assertIn("CSV", str(context.exception))
        finally:
            os.unlink(temp_file)
    
    def test_profile_returns_dict(self):
        """Test that profile() returns a dictionary of ColumnProfile objects."""
        profiler = DataProfiler(self.sample_data_path)
        profiles = profiler.profile()
        
        self.assertIsInstance(profiles, dict)
        self.assertTrue(len(profiles) > 0)
        
        for col_name, profile in profiles.items():
            self.assertIsInstance(profile, ColumnProfile)
            self.assertEqual(profile.name, col_name)
    
    def test_profile_mixed_data_types(self):
        """Test profiling a file with mixed data types."""
        profiler = DataProfiler(self.sample_data_path)
        profiles = profiler.profile()
        
        # Check that age column is detected as numeric
        age_profile = profiles.get('age')
        self.assertIsNotNone(age_profile)
        self.assertIn(age_profile.data_type, ['int', 'numeric', 'float'])
        
        # Check that name column is detected as string
        name_profile = profiles.get('name')
        self.assertIsNotNone(name_profile)
        self.assertEqual(name_profile.data_type, 'string')
    
    def test_profile_null_handling(self):
        """Test that null values are correctly counted."""
        profiler = DataProfiler(self.sample_data_path)
        profiles = profiler.profile()
        
        # Should have at least one column with nulls
        null_columns = [p for p in profiles.values() if p.null_count > 0]
        self.assertTrue(len(null_columns) > 0, "Should have columns with null values")
        
        # Check null percentage calculation
        for profile in null_columns:
            expected_pct = (profile.null_count / profile.total_rows * 100) if profile.total_rows > 0 else 0
            self.assertAlmostEqual(profile.null_percentage, expected_pct, places=2)
    
    def test_profile_empty_file(self):
        """Test profiling an empty CSV file (headers only)."""
        profiler = DataProfiler(self.sample_empty_path)
        profiles = profiler.profile()
        summary = profiler.get_summary()
        
        self.assertEqual(summary['total_rows'], 0)
        # Headers should still be loaded
        self.assertGreater(summary['total_columns'], 0)
        
        # All columns should have total_rows = 0
        for col in profiles.values():
            self.assertEqual(col.total_rows, 0)
    
    def test_profile_all_null_column(self):
        """Test profiling a column with all null values."""
        profiler = DataProfiler(self.sample_all_nulls_path)
        profiles = profiler.profile()
        
        value_profile = profiles['value']
        # All values should be null
        self.assertEqual(value_profile.null_count, value_profile.total_rows)
        self.assertEqual(value_profile.null_percentage, 100.0)
        self.assertEqual(value_profile.distinct_values, 0)
    
    def test_profile_distinct_values(self):
        """Test that distinct values are correctly counted."""
        profiler = DataProfiler(self.sample_data_path)
        profiles = profiler.profile()
        
        name_profile = profiles['name']
        # Should have correct number of distinct values (excluding nulls)
        self.assertGreater(name_profile.distinct_values, 0)
        self.assertLessEqual(name_profile.distinct_values, name_profile.total_rows)
    
    def test_profile_most_frequent(self):
        """Test that most frequent values are correctly identified."""
        profiler = DataProfiler(self.sample_data_path)
        profiles = profiler.profile()
        
        salary_profile = profiles['salary']
        # Should have most frequent values
        if salary_profile.most_frequent:
            # Most frequent list should be sorted by frequency
            for i in range(len(salary_profile.most_frequent) - 1):
                self.assertGreaterEqual(
                    salary_profile.most_frequent[i][1],
                    salary_profile.most_frequent[i + 1][1]
                )
    
    def test_profile_numeric_statistics(self):
        """Test that numeric statistics are calculated correctly."""
        profiler = DataProfiler(self.sample_data_path)
        profiles = profiler.profile()
        
        age_profile = profiles['age']
        # Age should have numeric statistics
        if age_profile.data_type in ['int', 'numeric', 'float']:
            self.assertIsNotNone(age_profile.min_value)
            self.assertIsNotNone(age_profile.max_value)
            self.assertIsNotNone(age_profile.mean)
            self.assertIsNotNone(age_profile.median)
            
            # Min should be <= Max
            self.assertLessEqual(age_profile.min_value, age_profile.max_value)
    
    def test_profile_get_summary(self):
        """Test that get_summary returns expected structure."""
        profiler = DataProfiler(self.sample_data_path)
        profiles = profiler.profile()
        summary = profiler.get_summary()
        
        # Check summary structure
        self.assertIn('file', summary)
        self.assertIn('total_rows', summary)
        self.assertIn('total_columns', summary)
        self.assertIn('columns', summary)
        
        # Check that columns list matches profiles
        self.assertEqual(len(summary['columns']), len(profiles))
    
    def test_column_profile_to_dict(self):
        """Test ColumnProfile.to_dict() method."""
        profile = ColumnProfile(
            name='test',
            data_type='string',
            total_rows=100,
            null_count=5,
            null_percentage=5.0,
            duplicate_rows=10,
            distinct_values=85,
            most_frequent=[('value1', 20), ('value2', 15)],
            min_value=None,
            max_value=None,
            mean=None,
            median=None,
            std_dev=None
        )
        
        profile_dict = profile.to_dict()
        
        self.assertEqual(profile_dict['name'], 'test')
        self.assertEqual(profile_dict['data_type'], 'string')
        self.assertEqual(profile_dict['null_count'], 5)
        self.assertEqual(profile_dict['null_percentage'], 5.0)
    
    def test_infer_type_int(self):
        """Test type inference for integers."""
        profiler = DataProfiler(self.sample_data_path)
        self.assertEqual(profiler._infer_type('123'), 'int')
    
    def test_infer_type_float(self):
        """Test type inference for floats."""
        profiler = DataProfiler(self.sample_data_path)
        self.assertEqual(profiler._infer_type('123.45'), 'float')
    
    def test_infer_type_string(self):
        """Test type inference for strings."""
        profiler = DataProfiler(self.sample_data_path)
        self.assertEqual(profiler._infer_type('hello'), 'string')
    
    def test_infer_type_null(self):
        """Test type inference for null values."""
        profiler = DataProfiler(self.sample_data_path)
        self.assertEqual(profiler._infer_type(''), 'null')
        self.assertEqual(profiler._infer_type(None), 'null')
    
    def test_is_numeric(self):
        """Test numeric type detection."""
        profiler = DataProfiler(self.sample_data_path)
        self.assertTrue(profiler._is_numeric('int'))
        self.assertTrue(profiler._is_numeric('float'))
        self.assertFalse(profiler._is_numeric('string'))
        self.assertFalse(profiler._is_numeric('null'))


class TestLargeFile(unittest.TestCase):
    """Test handling of larger files."""
    
    def setUp(self):
        """Create a larger test CSV file."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_file_path = self.temp_file.name
        
        # Write header
        self.temp_file.write('id,value,category\n')
        
        # Write 1000 rows
        for i in range(1000):
            category = 'A' if i % 2 == 0 else 'B'
            self.temp_file.write(f'{i},{i * 10.5},{category}\n')
        
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up temporary file."""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_large_file_profiling(self):
        """Test that profiler can handle larger files efficiently."""
        profiler = DataProfiler(self.temp_file_path)
        profiles = profiler.profile()
        
        # Check that all rows were processed
        self.assertEqual(profiles['id'].total_rows, 1000)
        
        # Check distinct values
        id_profile = profiles['id']
        self.assertEqual(id_profile.distinct_values, 1000)
    
    def test_large_file_chunk_size(self):
        """Test that chunk size parameter works."""
        profiler = DataProfiler(self.temp_file_path, chunk_size=100)
        profiles = profiler.profile()
        
        self.assertEqual(profiles['id'].total_rows, 1000)


if __name__ == '__main__':
    unittest.main()
