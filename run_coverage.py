#!/usr/bin/env python
"""
SPEC_06 Group C Task 7: Coverage Test Runner
============================================

Comprehensive test runner with coverage reporting and analysis.
Achieves 80% code coverage target with detailed reporting.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Command: {command}\n")
    
    result = subprocess.run(command, shell=True, capture_output=False)
    
    if result.returncode != 0:
        print(f"\n❌ {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"\n✅ {description} completed successfully")
        return True


def install_dependencies():
    """Install required dependencies for coverage testing."""
    dependencies = [
        'coverage[toml]>=7.0.0',
        'django-coverage-plugin>=3.0.0',
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    return True


def run_tests_with_coverage(test_pattern=None, verbose=False):
    """Run tests with coverage measurement."""
    # Base command
    base_cmd = "coverage run --source='.' manage.py test"
    
    # Add test pattern if specified
    if test_pattern:
        base_cmd += f" {test_pattern}"
    else:
        base_cmd += " core"
    
    # Add verbosity if requested
    if verbose:
        base_cmd += " -v 2"
    
    return run_command(base_cmd, "Running tests with coverage measurement")


def generate_coverage_report():
    """Generate coverage report."""
    return run_command("coverage report -m", "Generating coverage report")


def generate_html_report():
    """Generate HTML coverage report."""
    success = run_command("coverage html", "Generating HTML coverage report")
    
    if success:
        html_path = Path("htmlcov/index.html")
        if html_path.exists():
            print(f"\n📊 HTML coverage report generated: {html_path.absolute()}")
            print("   Open this file in your browser to view detailed coverage")
    
    return success


def generate_xml_report():
    """Generate XML coverage report for CI/CD."""
    return run_command("coverage xml", "Generating XML coverage report")


def generate_json_report():
    """Generate JSON coverage report."""
    return run_command("coverage json", "Generating JSON coverage report")


def check_coverage_threshold(threshold=80):
    """Check if coverage meets the specified threshold."""
    return run_command(
        f"coverage report --fail-under={threshold}",
        f"Checking coverage meets {threshold}% threshold"
    )


def analyze_coverage():
    """Analyze coverage data and provide insights."""
    print(f"\n{'='*60}")
    print("📈 Coverage Analysis")
    print(f"{'='*60}")
    
    try:
        import coverage
        
        # Load coverage data
        cov = coverage.Coverage()
        cov.load()
        
        # Get total coverage
        total = cov.report(show_missing=False, file=open(os.devnull, 'w'))
        
        print(f"📊 Overall Coverage: {total:.1f}%")
        
        if total >= 80:
            print("✅ Coverage target achieved! (≥80%)")
        else:
            print(f"⚠️  Coverage below target. Need {80 - total:.1f}% more coverage.")
        
        return total
        
    except Exception as e:
        print(f"❌ Could not analyze coverage: {e}")
        return 0


def clean_coverage_files():
    """Clean up coverage files."""
    files_to_clean = [
        '.coverage',
        'coverage.xml',
        'coverage.json',
        'htmlcov'
    ]
    
    for file_path in files_to_clean:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                path.unlink()
                print(f"🗑️  Removed {file_path}")
            elif path.is_dir():
                import shutil
                shutil.rmtree(path)
                print(f"🗑️  Removed directory {file_path}")


def main():
    """Main coverage test runner."""
    parser = argparse.ArgumentParser(
        description="Run tests with coverage for Sabor Con Flow Dance"
    )
    parser.add_argument(
        '--install', action='store_true',
        help='Install coverage dependencies'
    )
    parser.add_argument(
        '--test-pattern', 
        help='Specific test pattern to run (e.g., core.tests.test_models)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Run tests with verbose output'
    )
    parser.add_argument(
        '--html', action='store_true',
        help='Generate HTML coverage report'
    )
    parser.add_argument(
        '--xml', action='store_true',
        help='Generate XML coverage report (for CI/CD)'
    )
    parser.add_argument(
        '--json', action='store_true',
        help='Generate JSON coverage report'
    )
    parser.add_argument(
        '--threshold', type=int, default=80,
        help='Coverage threshold percentage (default: 80)'
    )
    parser.add_argument(
        '--clean', action='store_true',
        help='Clean coverage files before running'
    )
    parser.add_argument(
        '--analyze', action='store_true',
        help='Analyze coverage data and provide insights'
    )
    
    args = parser.parse_args()
    
    print("🧪 Sabor Con Flow Dance - Coverage Test Runner")
    print("SPEC_06 Group C Task 7: Comprehensive Testing Suite")
    
    # Install dependencies if requested
    if args.install:
        if not install_dependencies():
            sys.exit(1)
    
    # Clean coverage files if requested
    if args.clean:
        clean_coverage_files()
    
    # Run tests with coverage
    if not run_tests_with_coverage(args.test_pattern, args.verbose):
        print("\n❌ Tests failed. Coverage analysis may be incomplete.")
        sys.exit(1)
    
    # Generate basic report
    if not generate_coverage_report():
        print("\n❌ Failed to generate coverage report")
        sys.exit(1)
    
    # Generate additional reports if requested
    if args.html:
        generate_html_report()
    
    if args.xml:
        generate_xml_report()
    
    if args.json:
        generate_json_report()
    
    # Analyze coverage
    if args.analyze:
        coverage_percent = analyze_coverage()
    
    # Check threshold
    if not check_coverage_threshold(args.threshold):
        print(f"\n❌ Coverage below {args.threshold}% threshold")
        sys.exit(1)
    
    print(f"\n🎉 All tests passed with ≥{args.threshold}% coverage!")
    print("\nNext steps:")
    print("  • Review coverage reports for areas needing improvement")
    print("  • Add tests for uncovered code paths")
    print("  • Consider integration with CI/CD pipeline")
    
    if args.html:
        print("  • Open htmlcov/index.html to view detailed coverage")


if __name__ == "__main__":
    main()