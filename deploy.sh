#!/bin/bash
# =============================================================
# Megadominio - Script de deployment
# Uso: bash deploy.sh
# =============================================================

set -e

PROJECT_DIR="/var/www/Megadominio2026"
VENV="$PROJECT_DIR/venv/bin/activate"
BRANCH="master"

echo "========================================="
echo "  Megadominio - Deploy"
echo "========================================="

cd "$PROJECT_DIR"

# 1. Pull últimos cambios
echo ""
echo "[1/6] Pulling cambios de $BRANCH..."
git pull origin "$BRANCH"

# 2. Activar entorno virtual
echo ""
echo "[2/6] Activando entorno virtual..."
source "$VENV"

# 3. Instalar dependencias
echo ""
echo "[3/6] Instalando dependencias..."
pip install -r requirements.txt --quiet

# 4. Migraciones
echo ""
echo "[4/6] Ejecutando migraciones..."
python manage.py migrate --noinput

# 5. Collectstatic
echo ""
echo "[5/6] Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# 6. Reiniciar Gunicorn
echo ""
echo "[6/6] Reiniciando servicio..."
sudo systemctl restart megadominio

echo ""
echo "========================================="
echo "  Deploy completado exitosamente!"
echo "========================================="
