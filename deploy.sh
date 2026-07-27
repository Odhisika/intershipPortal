#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

echo "==> Pulling latest changes from git..."
git pull

sudo chown -R lig:www-data /var/www/intern
sudo chmod -R 755 /var/www/intern


echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Applying database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running Django checks..."
python manage.py check

echo "==> Restarting Apache..."
sudo systemctl restart apache2

echo "==> Deployment complete!"
