"""Report formatting for profiler output."""

import json
from typing import Dict, Any, List
from datetime import datetime


class ReportFormatter:
    """Format profiling results in different output formats."""
    
    def __init__(self, summary: Dict[str, Any]):
        """Initialize formatter with profiling summary."""
        self.summary = summary
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def format(self, output_format: str) -> str:
        """
        Format the summary in the requested format.
        
        Args:
            output_format: 'table', 'html', or 'json'
        
        Returns:
            Formatted report as string
        """
        if output_format == 'table':
            return self._format_table()
        elif output_format == 'html':
            return self._format_html()
        elif output_format == 'json':
            return self._format_json()
        else:
            raise ValueError(f"Unknown format: {output_format}")
    
    def _format_table(self) -> str:
        """Format as human-readable table for console."""
        lines = []
        
        # Header
        lines.append("=" * 100)
        lines.append("CSV DATA PROFILE REPORT")
        lines.append("=" * 100)
        lines.append(f"\nFile: {self.summary['file']}")
        lines.append(f"Generated: {self.timestamp}")
        lines.append(f"Total Rows: {self.summary['total_rows']}")
        lines.append(f"Total Columns: {self.summary['total_columns']}\n")
        
        # Column details
        for col in self.summary['columns']:
            lines.append("-" * 100)
            lines.append(f"Column: {col['name']} | Type: {col['data_type']}")
            lines.append("-" * 100)
            
            # Basic metrics
            lines.append(f"  Total Rows:        {col['total_rows']}")
            lines.append(f"  Null Count:        {col['null_count']} ({col['null_percentage']}%)")
            lines.append(f"  Distinct Values:   {col['distinct_values']}")
            lines.append(f"  Duplicate Rows:    {col['duplicate_rows']}")
            
            # Numeric metrics
            if col['mean'] is not None:
                lines.append(f"\n  Numeric Statistics:")
                lines.append(f"    Min:             {col['min_value']}")
                lines.append(f"    Max:             {col['max_value']}")
                lines.append(f"    Mean:            {col['mean']}")
                lines.append(f"    Median:          {col['median']}")
                lines.append(f"    Std Dev:         {col['std_dev']}")
            
            # Most frequent values
            if col['most_frequent']:
                lines.append(f"\n  Most Frequent Values:")
                for idx, (value, count) in enumerate(col['most_frequent'], 1):
                    percentage = (count / col['total_rows'] * 100) if col['total_rows'] > 0 else 0
                    lines.append(f"    {idx}. {value!r:<40} (count: {count}, {percentage:.2f}%)")
            
            lines.append("")
        
        lines.append("=" * 100)
        
        return "\n".join(lines)
    
    def _format_html(self) -> str:
        """Format as standalone HTML report."""
        html_parts = []
        
        # HTML Header
        html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Profile Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .metadata {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .metadata-item {
            text-align: center;
        }
        
        .metadata-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }
        
        .metadata-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }
        
        .columns-section {
            padding: 30px;
        }
        
        .column-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        
        .column-header {
            background: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 2px solid #667eea;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .column-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }
        
        .column-type {
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }
        
        .column-content {
            padding: 20px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .metric {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.85em;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-value {
            font-size: 1.4em;
            font-weight: bold;
            color: #333;
        }
        
        .numeric-section {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }
        
        .numeric-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .numeric-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }
        
        .numeric-metric {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 4px;
            border-left: 3px solid #2196F3;
        }
        
        .numeric-metric-label {
            color: #1565c0;
            font-size: 0.8em;
            text-transform: uppercase;
            margin-bottom: 3px;
        }
        
        .numeric-metric-value {
            font-weight: bold;
            color: #0d47a1;
        }
        
        .frequent-section {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }
        
        .frequent-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        
        .frequent-list {
            list-style: none;
        }
        
        .frequent-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
            background: #fafafa;
            padding: 10px;
            margin-bottom: 5px;
            border-radius: 4px;
        }
        
        .frequent-value {
            font-family: 'Courier New', monospace;
            flex: 1;
            word-break: break-all;
        }
        
        .frequent-stats {
            margin-left: 10px;
            text-align: right;
            white-space: nowrap;
        }
        
        .frequent-count {
            color: #666;
            font-size: 0.9em;
        }
        
        .frequent-percent {
            color: #999;
            font-size: 0.8em;
        }
        
        .footer {
            padding: 20px 30px;
            background: #f8f9fa;
            text-align: center;
            color: #999;
            font-size: 0.9em;
        }
        
        .no-data {
            color: #999;
            font-style: italic;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Data Profile Report</h1>
        </div>""")
        
        # Metadata section
        html_parts.append(f"""
        <div class="metadata">
            <div class="metadata-item">
                <div class="metadata-label">File</div>
                <div class="metadata-value">{self.summary['file'].split('/')[-1]}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Total Rows</div>
                <div class="metadata-value">{self.summary['total_rows']:,}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Total Columns</div>
                <div class="metadata-value">{self.summary['total_columns']}</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Generated</div>
                <div class="metadata-value">{self.timestamp}</div>
            </div>
        </div>""")
        
        # Columns section
        html_parts.append("\n        <div class=\"columns-section\">")
        
        for col in self.summary['columns']:
            html_parts.append(f"""
            <div class="column-card">
                <div class="column-header">
                    <span class="column-name">{col['name']}</span>
                    <span class="column-type">{col['data_type']}</span>
                </div>
                <div class="column-content">
                    <div class="metrics-grid">
                        <div class="metric">
                            <div class="metric-label">Total Rows</div>
                            <div class="metric-value">{col['total_rows']:,}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Null Count</div>
                            <div class="metric-value">{col['null_count']} ({col['null_percentage']}%)</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Distinct Values</div>
                            <div class="metric-value">{col['distinct_values']:,}</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Duplicate Rows</div>
                            <div class="metric-value">{col['duplicate_rows']:,}</div>
                        </div>
                    </div>""")
            
            # Numeric statistics
            if col['mean'] is not None:
                html_parts.append(f"""
                    <div class="numeric-section">
                        <div class="numeric-title">Numeric Statistics</div>
                        <div class="numeric-metrics">
                            <div class="numeric-metric">
                                <div class="numeric-metric-label">Min</div>
                                <div class="numeric-metric-value">{col['min_value']}</div>
                            </div>
                            <div class="numeric-metric">
                                <div class="numeric-metric-label">Max</div>
                                <div class="numeric-metric-value">{col['max_value']}</div>
                            </div>
                            <div class="numeric-metric">
                                <div class="numeric-metric-label">Mean</div>
                                <div class="numeric-metric-value">{col['mean']}</div>
                            </div>
                            <div class="numeric-metric">
                                <div class="numeric-metric-label">Median</div>
                                <div class="numeric-metric-value">{col['median']}</div>
                            </div>
                            <div class="numeric-metric">
                                <div class="numeric-metric-label">Std Dev</div>
                                <div class="numeric-metric-value">{col['std_dev']}</div>
                            </div>
                        </div>
                    </div>""")
            
            # Most frequent values
            if col['most_frequent']:
                html_parts.append("""
                    <div class="frequent-section">
                        <div class="frequent-title">Most Frequent Values</div>
                        <ul class="frequent-list">""")
                
                for value, count in col['most_frequent']:
                    percentage = (count / col['total_rows'] * 100) if col['total_rows'] > 0 else 0
                    html_parts.append(f"""
                            <li class="frequent-item">
                                <span class="frequent-value"><code>{value}</code></span>
                                <span class="frequent-stats">
                                    <div class="frequent-count">Count: {count}</div>
                                    <div class="frequent-percent">{percentage:.2f}%</div>
                                </span>
                            </li>""")
                
                html_parts.append("""
                        </ul>
                    </div>""")
            else:
                html_parts.append('<div class="no-data">No data to display</div>')
            
            html_parts.append("""
                </div>
            </div>""")
        
        html_parts.append("""
        </div>""")
        
        # Footer
        html_parts.append(f"""
        <div class="footer">
            Generated by CSV Data Profiler on {self.timestamp}
        </div>
    </div>
</body>
</html>""")
        
        return "\n".join(html_parts)
    
    def _format_json(self) -> str:
        """Format as JSON."""
        return json.dumps(self.summary, indent=2)
