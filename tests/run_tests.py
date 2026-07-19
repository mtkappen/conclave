#!/usr/bin/env python
"""
Test runner script for D&D Tabletop application.
Runs all tests with pytest and provides summary output.
"""
import os
import sys
import django

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnd_app.settings')
django.setup()

if __name__ == '__main__':
    # Import pytest
    try:
        import pytest
    except ImportError:
        print("Error: pytest is not installed.")
        print("Install it with: pip install pytest pytest-django pytest-cov")
        sys.exit(1)
    
    # Test configuration
    test_args = [
        'tests/',  # Run tests in the tests directory
        '-v',      # Verbose output
        '--tb=short',  # Short traceback format
    ]
    
    # Add coverage options if pytest-cov is available
    try:
        import pytest_cov
        test_args.extend([
            '--cov=campaigns',
            '--cov-report=term-missing',
            '--cov-report=html:tests/coverage_html',
        ])
    except ImportError:
        print("Note: Install pytest-cov for coverage reports:")
        print("  pip install pytest-cov")
    
    # Run tests
    exit_code = pytest.main(test_args)
    
    sys.exit(exit_code)
