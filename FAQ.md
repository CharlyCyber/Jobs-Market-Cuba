# ❓ Preguntas Frecuentes (FAQ)

## General

### ¿Qué es este bot?

Es un bot de Telegram que automáticamente busca ofertas laborales en plataformas cubanas y las filtra según categorías específicas: Inteligencia Artificial, Diseño, Redacción y Automatizaciones.

### ¿Es gratis?

Sí, el código es open source y gratuito. Solo necesitas un servidor donde ejecutarlo.

### ¿Qué plataformas consulta?

- Revolico (categoría empleos)
- Cubisima (marketing, diseño, IT)
- CuCoders (desarrollo)

### ¿Con qué frecuencia busca ofertas?

El bot busca ofertas cada vez que un usuario escribe "Ofertas". No hace búsquedas automáticas programadas (pero puedes agregar esta funcionalidad).

## Instalación

### ¿Qué necesito para ejecutar el bot?

- Python 3.8 o superior
- Un token de Telegram Bot (gratis desde @BotFather)
- Conexión a internet
- Un servidor o tu computadora (para desarrollo)

### ¿Cómo obtengo un token de Telegram?

1. Abre Telegram
2. Busca @BotFather
3. Envía `/newbot`
4. Sigue las instrucciones
5. Copia el token que te dan

### ¿Funciona en Windows?

Sí, el bot funciona en Windows, Linux y Mac. Las instrucciones son similares para todos los sistemas operativos.

### Error: "Module not found"

Asegúrate de haber instalado todas las dependencias:
```bash
pip install -r requirements.txt
```

### Error: "TELEGRAM_BOT_TOKEN is required"

Crea un archivo `.env` en la raíz del proyecto con tu token:
```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
```

## Uso

### ¿Cómo uso el bot?

1. Busca tu bot en Telegram
2. Envía `/start`
3. Envía `Ofertas` (la palabra, no el comando /ofertas)
4. Espera unos segundos

### ¿Puedo cambiar las palabras clave de búsqueda?

Sí, edita el archivo `.env` y modifica `FILTER_KEYWORDS`:
```env
FILTER_KEYWORDS=tus,palabras,clave,aquí
```

### ¿Puedo agregar más plataformas?

Sí, el código es modular. Sigue la guía en [CONTRIBUTING.md](CONTRIBUTING.md) para agregar nuevos scrapers.

### El bot es muy lento

Puedes ajustar el timeout en `.env`:
```env
REQUEST_TIMEOUT=60
REQUEST_DELAY=1
```

### ¿Puedo usar el bot sin Telegram?

El código de scraping es independiente. Puedes ejecutar:
```bash
python test_scraping.py
```

Esto guardará los resultados en un archivo HTML.

## Técnico

### ¿Qué tecnologías usa?

- Python 3.8+
- python-telegram-bot (async)
- BeautifulSoup4 (parsing HTML)
- httpx/requests (HTTP requests)
- Selenium (opcional, para JS)

### ¿Cómo funciona el scraping?

1. El bot hace requests HTTP a las plataformas
2. Parsea el HTML con BeautifulSoup
3. Extrae información de las ofertas
4. Filtra por palabras clave
5. Formatea en HTML
6. Envía por Telegram

### ¿Es legal hacer scraping?

El scraping de información pública generalmente es legal, pero debes:
- Respetar los términos de servicio
- No sobrecargar los servidores
- Usar delays entre requests
- No usar la información comercialmente sin permiso

### ¿Puedo modificar el código?

Sí, es open source bajo licencia MIT. Puedes:
- Modificarlo
- Distribuirlo
- Usarlo comercialmente
- Pero debes mantener la licencia y créditos

### ¿Cómo contribuyo?

Lee [CONTRIBUTING.md](CONTRIBUTING.md) para guías detalladas.

## Errores Comunes

### Error 403 (Forbidden)

Algunos sitios bloquean el scraping. Soluciones:
- Aumenta `REQUEST_DELAY` en `.env`
- Usa proxies
- El bot ya rota User-Agents automáticamente

### Error 429 (Too Many Requests)

Estás haciendo demasiados requests. Solución:
```env
REQUEST_DELAY=5
MAX_RETRIES=2
```

### Timeout errors

- Aumenta `REQUEST_TIMEOUT` en `.env`
- Verifica tu conexión a internet
- El sitio puede estar caído

### Bot no responde en Telegram

1. Verifica que el script está corriendo
2. Verifica los logs para errores
3. Asegúrate de escribir "Ofertas" exactamente
4. El token debe ser correcto

### No encuentra ninguna oferta

Posibles causas:
- Las plataformas cambiaron su estructura HTML
- No hay ofertas que coincidan con los filtros
- Errores de scraping (revisa logs)

## Despliegue

### ¿Dónde puedo hospearlo gratis?

Opciones gratuitas:
- Railway.app (500 horas/mes)
- Render.com (free tier)
- Fly.io (free tier)
- Tu computadora (para desarrollo)

### ¿Necesito un servidor 24/7?

Solo si quieres que el bot esté disponible 24/7. Para desarrollo, puedes ejecutarlo en tu computadora.

### ¿Cómo lo mantengo corriendo?

Opciones:
- Docker Compose
- Systemd service (Linux)
- Screen/tmux (desarrollo)
- Cloud platforms

Ver [DEPLOYMENT.md](DEPLOYMENT.md) para detalles.

### ¿Consume muchos recursos?

No, el bot es ligero:
- ~50-100 MB RAM
- Minimal CPU
- Network: depende de la frecuencia de uso

## Personalización

### ¿Puedo cambiar el formato del mensaje?

Sí, edita `bot/utils/formatter.py` para cambiar el formato HTML.

### ¿Puedo agregar comandos?

Sí, agrega handlers en `bot/handlers.py`.

### ¿Puedo hacer búsquedas automáticas?

Sí, puedes agregar un scheduler. Ejemplo con APScheduler:
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(search_jobs, 'interval', hours=6)
scheduler.start()
```

### ¿Puedo notificar a múltiples usuarios?

Sí, necesitarás:
1. Almacenar IDs de usuarios (database)
2. Implementar suscripciones
3. Enviar mensajes broadcast

### ¿Puedo agregar filtros personalizados por usuario?

Sí, necesitarás:
1. Una base de datos (SQLite, PostgreSQL, etc.)
2. Almacenar preferencias de usuario
3. Filtrar según preferencias

## Seguridad

### ¿Es seguro mi token?

Tu token es sensible. Protégelo:
- No lo compartas
- No lo subas a GitHub
- Usa variables de entorno
- Regenera si se compromete

### ¿Debo usar HTTPS?

Telegram maneja la encriptación. Tu bot se comunica con Telegram API via HTTPS automáticamente.

### ¿Puedo limitar quién usa el bot?

Sí, puedes agregar una whitelist en los handlers:
```python
ALLOWED_USERS = [123456789, 987654321]

if update.effective_user.id not in ALLOWED_USERS:
    await update.message.reply_text("No autorizado")
    return
```

## Performance

### ¿Cómo hago el bot más rápido?

- El scraping ya es paralelo
- Reduce `REQUEST_DELAY` (con cuidado)
- Usa caché para resultados recientes
- Optimiza los selectores CSS

### ¿Puedo cachear resultados?

Sí, puedes implementar caché con Redis o simplemente en memoria:
```python
from datetime import datetime, timedelta

cache = {}
CACHE_DURATION = timedelta(minutes=30)

def get_cached_results():
    if 'results' in cache:
        if datetime.now() - cache['timestamp'] < CACHE_DURATION:
            return cache['results']
    return None
```

### Múltiples usuarios al mismo tiempo

El bot maneja múltiples usuarios automáticamente gracias a python-telegram-bot async.

## Mantenimiento

### ¿Qué pasa si una plataforma cambia su estructura?

Deberás actualizar el scraper correspondiente. Los scrapers están en `scrapers/`.

### ¿Con qué frecuencia debo actualizar?

- Dependencias: mensualmente
- Código: cuando agregues features
- Scrapers: cuando fallen

### ¿Cómo monitoreo el bot?

- Revisa los logs
- Configura alertas (email, Slack, etc.)
- Usa servicios de uptime monitoring

### ¿Cómo hago backup?

```bash
# Backup de configuración
tar -czf backup.tar.gz .env bot/ scrapers/ filters/

# Backup de base de datos (si la usas)
cp database.db database.backup.db
```

## Soporte

### ¿Dónde reporto bugs?

Abre un issue en GitHub con:
- Descripción del bug
- Pasos para reproducir
- Logs de error
- Tu entorno (OS, Python version)

### ¿Dónde pido ayuda?

1. Lee esta FAQ
2. Lee README.md y SETUP.md
3. Busca en GitHub Issues
4. Crea un nuevo issue

### ¿Hay una comunidad?

Puedes contribuir al proyecto en GitHub. Pull requests son bienvenidos!

### ¿Puedo contratar soporte?

Este es un proyecto open source comunitario. Para soporte comercial, contacta a los mantenedores.

---

## ¿No encontraste tu pregunta?

Abre un issue en GitHub con la etiqueta `question` o contribuye a esta FAQ!
