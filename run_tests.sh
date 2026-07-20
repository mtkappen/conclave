#!/bin/bash

set -e

echo "=== Running Tests ==="

# Check if pytest-cov is installed (required by pytest.ini)
if ! python3 -c "import pytest_cov" 2>/dev/null; then
    echo "Installing pytest-cov..."
    pip3 install --break-system-packages pytest-cov
fi

# Run pytest with Django settings
python3 -m pytest tests/ "$@"
