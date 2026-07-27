#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

echo "==> Pulling latest changes from git..."
git pull

echo "==> Fixing ownership and permissions..."
sudo chown -R lig:www-data /var/www/intern
sudo find /var/www/intern -type d -exec chmod 755 {} +
sudo find /var/www/intern -type f -exec chmod 664 {} +

echo "==> Ensuring media directories exist..."
sudo mkdir -p /var/www/intern/media/attachment_letters
sudo chown -R www-data:www-data /var/www/intern/media
sudo chmod -R 775 /var/www/intern/media

echo "==> Fixing SQLite database permissions..."
sudo touch /var/www/intern/db.sqlite3
sudo chown lig:www-data /var/www/intern/db.sqlite3
sudo chmod 664 /var/www/intern/db.sqlite3

echo "==> Adding safe directory for git..."
sudo git config --global --add safe.directory /var/www/intern


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
