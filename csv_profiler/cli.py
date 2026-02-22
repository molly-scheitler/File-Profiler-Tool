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
def profile(filepath: str, output: str, format: str, chunk_size: int):
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
