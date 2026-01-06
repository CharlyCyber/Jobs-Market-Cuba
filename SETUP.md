# 🚀 Guía de Setup - Bot de Ofertas Laborales Cuba

Esta guía te ayudará a configurar y ejecutar el bot paso a paso.

## 📋 Pre-requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Una cuenta de Telegram
- Conexión a internet

## 🔧 Instalación Paso a Paso

### 1. Verificar Python

```bash
python3 --version
```

Deberías ver algo como `Python 3.8.x` o superior.

### 2. Crear Bot de Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía el comando `/newbot`
3. Sigue las instrucciones:
   - Elige un nombre para tu bot (ej: "Cuba Jobs Bot")
   - Elige un username único que termine en "bot" (ej: "cuba_jobs_finder_bot")
4. BotFather te dará un **token** como este:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
5. **Guarda este token**, lo necesitarás más adelante

### 3. Clonar el Repositorio

```bash
git clone <repository-url>
cd Jobs-Market-Cuba
```

### 4. Crear Entorno Virtual

**En Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

Verás `(venv)` al inicio de tu línea de comando cuando el entorno esté activado.

### 5. Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Esto puede tomar unos minutos. Espera a que termine completamente.

### 6. Configurar Variables de Entorno

```bash
cp .env.example .env
```

Ahora edita el archivo `.env` con tu editor favorito:

**En Linux/Mac:**
```bash
nano .env
```

**En Windows:**
```bash
notepad .env
```

Reemplaza `your_bot_token_here` con el token que obtuviste de BotFather:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

Guarda el archivo (Ctrl+O, Enter, Ctrl+X en nano).

### 7. Ejecutar el Bot

```bash
python run.py
```

Deberías ver algo como:

```
2024-01-06 10:30:45 - bot.main - INFO - Starting Cuba Jobs Telegram Bot
2024-01-06 10:30:46 - bot.main - INFO - Bot @cuba_jobs_finder_bot is ready to receive messages
```

¡Felicidades! Tu bot está corriendo. 🎉

### 8. Probar el Bot

1. Abre Telegram
2. Busca tu bot por el username que elegiste
3. Envía `/start`
4. Envía `Ofertas`
5. Espera unos segundos mientras el bot busca ofertas

## 🐛 Solución de Problemas

### Error: "No module named 'telegram'"

**Solución:**
```bash
pip install python-telegram-bot==20.8
```

### Error: "TELEGRAM_BOT_TOKEN is required"

**Solución:**
- Verifica que el archivo `.env` existe en la raíz del proyecto
- Verifica que el token está correctamente copiado (sin espacios extra)

### Error: "Unauthorized"

**Solución:**
- El token es incorrecto o inválido
- Genera un nuevo token con BotFather usando `/newbot` de nuevo

### El bot no responde

**Solución:**
1. Verifica que el script `run.py` está corriendo (no debe haber errores en la consola)
2. Busca el bot en Telegram usando el username exacto
3. Envía `/start` primero

### Errors de conexión / Timeout

**Solución:**
- Verifica tu conexión a internet
- Aumenta el timeout en `.env`:
  ```env
  REQUEST_TIMEOUT=60
  ```

## 🔄 Actualizar el Bot

Si hay nuevos cambios en el repositorio:

```bash
git pull
pip install -r requirements.txt --upgrade
```

## 🛑 Detener el Bot

Presiona `Ctrl+C` en la terminal donde está corriendo el bot.

## 🔐 Seguridad

- **NUNCA** compartas tu token de Telegram
- **NUNCA** subas el archivo `.env` a GitHub
- El archivo `.gitignore` ya está configurado para ignorar `.env`

## 📱 Usar el Bot

Una vez que el bot esté corriendo:

### Comandos disponibles:

- `/start` - Ver mensaje de bienvenida
- `/help` - Ver ayuda
- `Ofertas` - Buscar ofertas laborales

### Flujo típico:

1. Usuario: `Ofertas`
2. Bot: "🔄 Buscando ofertas laborales..."
3. Bot: *Muestra lista de ofertas en HTML*

## 🚀 Despliegue en Producción

Para mantener el bot corriendo 24/7, considera:

### Opción 1: Screen (Linux)

```bash
screen -S telegram-bot
python run.py
# Presiona Ctrl+A, luego D para desconectar
# Para reconectar: screen -r telegram-bot
```

### Opción 2: Systemd Service (Linux)

Crea `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Cuba Jobs Telegram Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Jobs-Market-Cuba
Environment="PATH=/path/to/Jobs-Market-Cuba/venv/bin"
ExecStart=/path/to/Jobs-Market-Cuba/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Luego:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### Opción 3: Docker

Crea un `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
```

Construir y ejecutar:

```bash
docker build -t cuba-jobs-bot .
docker run -d --name cuba-jobs-bot --env-file .env cuba-jobs-bot
```

### Opción 4: Servicios Cloud

- **Heroku**: Free tier (con limitaciones)
- **Railway**: Free tier disponible
- **Render**: Free tier disponible
- **Google Cloud Run**: Pay-as-you-go
- **AWS EC2**: Free tier disponible

## 📊 Monitoreo

Ver logs en tiempo real:

```bash
python run.py
```

O redirigir a un archivo:

```bash
python run.py > bot.log 2>&1 &
tail -f bot.log
```

## 💡 Tips

1. **Prueba primero localmente** antes de desplegar
2. **Monitorea los logs** regularmente
3. **Actualiza las dependencias** periódicamente
4. **Configura alertas** si despliegas en producción
5. **Respeta los rate limits** de las plataformas que scrapeas

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs para errores específicos
2. Busca el error en GitHub Issues
3. Crea un nuevo issue con:
   - Descripción del problema
   - Logs de error
   - Pasos para reproducir
   - Tu entorno (OS, versión de Python)

---

¡Buena suerte con tu bot! 🚀🇨🇺
