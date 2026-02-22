"""CLI interface for CSV data profiler."""

import click
import sys
from pathlib import Path

# Support running as a module (package relative) and as a script (direct import)
try:
    from .profiler import DataProfiler
    from .reports import ReportFormatter
except Exception:
    from profiler import DataProfiler
    from reports import ReportFormatter
import json


@click.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option(
    '--output', '-o',
    type=click.Path(),
    default=None,
    help='Output file path (if not specified, prints to console for table format)'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['table', 'html', 'json']),
    default='table',
    help='Output format (default: table)'
)
@click.option(
    '--chunk-size',
    type=int,
    default=10000,
    help='Chunk size for reading large files (default: 10000)'
)
@click.option(
    '--schema', '-s',
    type=click.Path(exists=True),
    default=None,
    help='Path to expected schema JSON file for validation (optional)'
)
@click.option(
    '--validate',
    is_flag=True,
    default=False,
    help='Run schema validation mode (requires --schema)'
)
def profile(filepath: str, output: str, format: str, chunk_size: int, schema: str, validate: bool):
    """
    Generate a data profile report for a CSV file.
    
    FILEPATH: Path to the CSV file to profile
    
    Examples:
    
        # View table output in console
        python -m csv_profiler data.csv
        
        # Save HTML report
        python -m csv_profiler data.csv --format html --output report.html
        
        # Export as JSON
        python -m csv_profiler data.csv --format json --output report.json
    """
    try:
        click.echo(f"📊 Profiling: {filepath}", err=False)
        
        # Initialize profiler
        profiler = DataProfiler(filepath, chunk_size=chunk_size)
        
        # Generate profile
        profiles = profiler.profile()
        summary = profiler.get_summary()

        # If schema validation requested, attempt to validate
        if validate and schema:
            try:
                with open(schema, 'r', encoding='utf-8') as sf:
                    expected = json.load(sf)
                # expected is a mapping of column -> expected_type
                mismatches = []
                for col, expected_type in expected.items():
                    prof = profiles.get(col)
                    if prof is None:
                        mismatches.append(f"Missing column: {col}")
                    else:
                        if prof.data_type != expected_type:
                            mismatches.append(f"Column {col}: expected {expected_type}, got {prof.data_type}")
                summary['schema_validation'] = {'mismatches': mismatches, 'ok': len(mismatches) == 0}
            except Exception as e:
                summary['schema_validation'] = {'error': str(e)}
        
        # Format and output report
        formatter = ReportFormatter(summary)
        report = formatter.format(format)
        
        if output:
            # Write to file
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == 'html':
                output_path.write_text(report, encoding='utf-8')
            else:
                output_path.write_text(report, encoding='utf-8')
            
            click.echo(f"✅ Report saved to: {output_path.absolute()}", err=False)
        else:
            # Print to console
            if format == 'table':
                click.echo(report, err=False)
            else:
                click.echo(report, err=False)
    
    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    profile()
