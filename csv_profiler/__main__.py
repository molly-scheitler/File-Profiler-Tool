"""Entry point for running the CSV profiler as a module."""

# Use a package-relative import so `python -m csv_profiler` works
from .cli import profile


def main():
    """Main entry point for the CLI."""
    profile()


if __name__ == '__main__':
    main()
