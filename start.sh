#!/bin/bash

set -e

echo "=== Checking Dependencies ==="

# Check if Django is installed
if ! python3 -c "import django; print(f'Django {django.VERSION[0]}.{django.VERSION[1]}')" 2>/dev/null; then
    echo "Installing dependencies from requirements.txt..."
    pip3 install -r requirements.txt
else
    echo "✓ All Python dependencies installed"
fi

# Get network IP addresses (excluding localhost and Docker)
echo ""
echo "=== Network Interfaces ==="
NETWORK_IPS=$(ip addr show | grep "inet " | awk '{print $2}' | cut -d'/' -f1 | grep -v "^127.0.0.1$" | grep -v "^172\.17\." || true)

if [ -z "$NETWORK_IPS" ]; then
    echo "No network interfaces found (excluding localhost)"
else
    echo "Available IPs:"
    echo "$NETWORK_IPS" | while read ip; do
        echo "  - $ip"
    done
fi

echo ""
echo "=== Starting Django Server ==="
echo "Server will be accessible at:"
echo "$NETWORK_IPS" | while read ip; do
    echo "  http://$ip:8020"
done
echo ""
echo "Press Ctrl+C to stop the server"
echo "---"

python3 manage.py runserver 0.0.0.0:8020
