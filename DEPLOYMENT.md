# 🚀 Guía de Despliegue

Esta guía cubre diferentes opciones para desplegar el bot en producción.

## 📋 Pre-requisitos

- Servidor con acceso a internet
- Docker (recomendado) o Python 3.8+
- Token de Telegram Bot
- Acceso SSH al servidor (si es remoto)

## 🐳 Opción 1: Docker (Recomendado)

### Ventajas
- ✅ Aislamiento completo
- ✅ Fácil de mantener
- ✅ Reproducible
- ✅ Rollback fácil

### Pasos

1. **Instalar Docker**

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

2. **Clonar el repositorio**

```bash
git clone <repository-url>
cd Jobs-Market-Cuba
```

3. **Configurar variables de entorno**

```bash
cp .env.example .env
nano .env  # Edita y agrega tu TELEGRAM_BOT_TOKEN
```

4. **Construir y ejecutar**

```bash
docker-compose up -d
```

5. **Verificar logs**

```bash
docker-compose logs -f
```

6. **Comandos útiles**

```bash
# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Ver status
docker-compose ps

# Actualizar
git pull
docker-compose up -d --build
```

## 🖥️ Opción 2: Systemd Service (Linux)

### Ventajas
- ✅ Inicio automático en boot
- ✅ Auto-reinicio en crashes
- ✅ Logs centralizados
- ✅ Gestión nativa del OS

### Pasos

1. **Preparar el entorno**

```bash
cd /opt
sudo git clone <repository-url> cuba-jobs-bot
cd cuba-jobs-bot
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
```

2. **Configurar .env**

```bash
sudo cp .env.example .env
sudo nano .env  # Agregar token
```

3. **Crear service file**

```bash
sudo nano /etc/systemd/system/cuba-jobs-bot.service
```

Contenido:

```ini
[Unit]
Description=Cuba Jobs Telegram Bot
After=network.target

[Service]
Type=simple
User=YOUR_USER
WorkingDirectory=/opt/cuba-jobs-bot
Environment="PATH=/opt/cuba-jobs-bot/venv/bin"
ExecStart=/opt/cuba-jobs-bot/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **Activar y ejecutar**

```bash
sudo systemctl daemon-reload
sudo systemctl enable cuba-jobs-bot
sudo systemctl start cuba-jobs-bot
```

5. **Verificar status**

```bash
sudo systemctl status cuba-jobs-bot
sudo journalctl -u cuba-jobs-bot -f
```

## 📱 Opción 3: Screen/tmux (Desarrollo)

### Solo para desarrollo o testing

```bash
# Con screen
screen -S telegram-bot
cd Jobs-Market-Cuba
source venv/bin/activate
python run.py
# Ctrl+A, D para detach

# Para reconectar
screen -r telegram-bot

# Con tmux
tmux new -s telegram-bot
cd Jobs-Market-Cuba
source venv/bin/activate
python run.py
# Ctrl+B, D para detach

# Para reconectar
tmux attach -t telegram-bot
```

## ☁️ Opción 4: Cloud Platforms

### Railway.app

1. Fork el repositorio en GitHub
2. Conecta Railway con tu cuenta de GitHub
3. Crea un nuevo proyecto desde el repositorio
4. Agrega variable de entorno `TELEGRAM_BOT_TOKEN`
5. Deploy automático

### Heroku

```bash
# Instalar Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Crear app
heroku create cuba-jobs-bot

# Configurar token
heroku config:set TELEGRAM_BOT_TOKEN=tu_token

# Deploy
git push heroku main
```

Crear `Procfile`:
```
worker: python run.py
```

### Google Cloud Run

```bash
# Construir imagen
gcloud builds submit --tag gcr.io/PROJECT-ID/cuba-jobs-bot

# Deploy
gcloud run deploy cuba-jobs-bot \
  --image gcr.io/PROJECT-ID/cuba-jobs-bot \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_BOT_TOKEN=tu_token
```

### AWS EC2

1. Lanzar instancia EC2 (Ubuntu)
2. SSH a la instancia
3. Instalar dependencias:
```bash
sudo apt update
sudo apt install python3 python3-pip git -y
```
4. Clonar repositorio y configurar
5. Usar systemd service (ver Opción 2)

### DigitalOcean Droplet

Similar a AWS EC2:
1. Crear Droplet (Ubuntu)
2. SSH al droplet
3. Seguir pasos de instalación manual
4. Configurar systemd service

## 🔐 Seguridad

### 1. Variables de Entorno

Nunca commitear `.env`:
```bash
# Verificar que .env está en .gitignore
grep .env .gitignore
```

### 2. Permisos de Archivos

```bash
chmod 600 .env
chmod 700 run.py
```

### 3. Actualizaciones

Mantener dependencias actualizadas:
```bash
pip list --outdated
pip install --upgrade -r requirements.txt
```

### 4. Firewall

```bash
# Ubuntu/Debian
sudo ufw allow ssh
sudo ufw enable
```

### 5. Usuario No-Root

```bash
# Crear usuario para el bot
sudo useradd -m -s /bin/bash botuser
sudo su - botuser
```

## 📊 Monitoreo

### 1. Logs

```bash
# Docker
docker-compose logs -f --tail=100

# Systemd
sudo journalctl -u cuba-jobs-bot -f

# Archivo
tail -f bot.log
```

### 2. Health Checks

Crear script `healthcheck.sh`:
```bash
#!/bin/bash
if ! pgrep -f "python.*run.py" > /dev/null; then
    echo "Bot not running!"
    systemctl restart cuba-jobs-bot
fi
```

Agregar a crontab:
```bash
crontab -e
# Agregar:
*/5 * * * * /path/to/healthcheck.sh
```

### 3. Alertas

Configurar alertas por email:
```bash
# Instalar mailutils
sudo apt install mailutils -y

# Script de alerta
if ! systemctl is-active --quiet cuba-jobs-bot; then
    echo "Bot down!" | mail -s "Bot Alert" tu@email.com
fi
```

## 🔄 CI/CD

### GitHub Actions

Crear `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /opt/cuba-jobs-bot
            git pull
            docker-compose up -d --build
```

## 🆘 Troubleshooting

### Bot no inicia

```bash
# Verificar logs
docker-compose logs
# o
sudo journalctl -u cuba-jobs-bot -n 50

# Verificar token
grep TELEGRAM_BOT_TOKEN .env

# Test manual
python run.py
```

### Memoria alta

```bash
# Verificar uso
docker stats
# o
top -p $(pgrep -f "python.*run.py")

# Reiniciar
docker-compose restart
```

### Errores de red

```bash
# Test conectividad
curl -I https://api.telegram.org

# Test DNS
nslookup api.telegram.org

# Verificar firewall
sudo ufw status
```

## 📈 Escalamiento

### Múltiples Instancias

Para alto tráfico:

```yaml
# docker-compose.yml
services:
  bot1:
    build: .
    container_name: bot-1
  
  bot2:
    build: .
    container_name: bot-2
  
  bot3:
    build: .
    container_name: bot-3
```

### Load Balancing

Usar Telegram Webhook con Nginx como proxy.

## 🔧 Mantenimiento

### Backup

```bash
# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz .env bot/ scrapers/ filters/

# Restore
tar -xzf backup-20240106.tar.gz
```

### Actualización

```bash
# Con Docker
cd /path/to/cuba-jobs-bot
git pull
docker-compose up -d --build

# Con Systemd
sudo systemctl stop cuba-jobs-bot
cd /opt/cuba-jobs-bot
sudo git pull
sudo venv/bin/pip install -r requirements.txt
sudo systemctl start cuba-jobs-bot
```

---

¡Tu bot está listo para producción! 🚀
