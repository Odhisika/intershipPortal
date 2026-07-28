#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

echo "==> Pulling latest changes from git..."
git pull

echo "==> Fixing ownership and permissions..."
sudo chown -R lig:www-data /var/www/intern --exclude=venv --exclude=media 2>/dev/null || true
sudo find /var/www/intern -type d -not -path "*/media/*" -not -path "*/venv/*" -exec chmod 755 {} +
sudo find /var/www/intern -type f -not -path "*/media/*" -not -path "*/venv/*" -exec chmod 664 {} +

echo "==> Ensuring media directories exist and are writable..."
sudo mkdir -p /var/www/intern/media/attachment_letters
sudo chown -R www-data:www-data /var/www/intern/media
sudo find /var/www/intern/media -type d -exec chmod 775 {} +
sudo find /var/www/intern/media -type f -exec chmod 664 {} +

echo "==> Fixing SQLite database permissions..."
sudo chown lig:www-data /var/www/intern
sudo chmod 775 /var/www/intern
sudo touch /var/www/intern/db.sqlite3
sudo chown lig:www-data /var/www/intern/db.sqlite3
sudo chmod 664 /var/www/intern/db.sqlite3

echo "==> Adding safe directory for git..."
sudo git config --global --add safe.directory /var/www/intern


VENV_DIR="$REPO_DIR/venv"

echo "==> Ensuring venv executables are runnable..."
sudo chmod +x "$VENV_DIR"/bin/*

echo "==> Installing dependencies..."
"$VENV_DIR/bin/pip" install -r requirements.txt

echo "==> Applying database migrations..."
"$VENV_DIR/bin/python" manage.py migrate --noinput

echo "==> Collecting static files..."
"$VENV_DIR/bin/python" manage.py collectstatic --noinput

echo "==> Running Django checks..."
"$VENV_DIR/bin/python" manage.py check

echo "==> Restarting Apache..."
sudo systemctl restart apache2

echo "==> Deployment complete!"
