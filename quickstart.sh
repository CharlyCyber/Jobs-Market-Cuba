#!/bin/bash

echo "🤖 Cuba Jobs Telegram Bot - Quick Start"
echo "======================================"
echo ""

if [ ! -f ".env" ]; then
    echo "⚠️  Archivo .env no encontrado"
    echo "📋 Copiando .env.example a .env..."
    cp .env.example .env
    echo ""
    echo "✅ Archivo .env creado"
    echo "⚠️  IMPORTANTE: Edita el archivo .env y agrega tu TELEGRAM_BOT_TOKEN"
    echo ""
    echo "Para editar el archivo .env:"
    echo "  nano .env"
    echo "  o"
    echo "  vim .env"
    echo ""
    read -p "Presiona Enter cuando hayas configurado tu token..."
fi

if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
fi

echo "🔧 Activando entorno virtual..."
source venv/bin/activate

echo "📥 Instalando dependencias..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "✅ Setup completo!"
echo ""
echo "🚀 Iniciando bot..."
echo ""

python run.py
