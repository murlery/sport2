#!/usr/bin/env bash
set -e

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies and build frontend
cd sport/client
npm install
npm run build
cd ../..

# Collect Django static files
python sport/manage.py collectstatic --no-input

# Run migrations
python sport/manage.py migrate
