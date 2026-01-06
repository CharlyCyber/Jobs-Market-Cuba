# 🤖 Bot de Telegram - Ofertas Laborales Cuba

Bot de Telegram automatizado que busca y filtra ofertas laborales en Cuba de múltiples plataformas, especializado en **Inteligencia Artificial**, **Diseño**, **Redacción** y **Automatizaciones**.

## 📋 Características

- ✅ **Scraping automático** de 5 plataformas laborales cubanas
- ✅ **Filtrado inteligente** por categorías específicas
- ✅ **Respuesta en HTML** estructurado y legible
- ✅ **Protección anti-bot** con rotación de User-Agent y delays
- ✅ **Arquitectura modular** y mantenible
- ✅ **Manejo robusto de errores** y timeouts
- ✅ **Logging completo** para debugging
- ✅ **Scraping paralelo** para mayor velocidad

## 🌐 Plataformas Soportadas

1. **Revolico** - Ofertas de empleo
2. **Cubisima** - Marketing, Diseño, IT/Cibernética
3. **CuCoders** - Ofertas de desarrollo

## 🛠️ Stack Tecnológico

- **Python 3.8+**
- **python-telegram-bot 20** (async)
- **BeautifulSoup4** - Parsing HTML
- **httpx & requests** - HTTP requests
- **Selenium** - Para sitios con JavaScript (opcional)
- **fake-useragent** - Rotación de User-Agent
- **python-dotenv** - Gestión de variables de entorno

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd Jobs-Market-Cuba
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita el archivo `.env` y configura tu token de Telegram:

```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
```

## 🚀 Uso

### Ejecutar el bot

```bash
python run.py
```

O directamente:

```bash
python -m bot.main
```

### Comandos del bot en Telegram

- `/start` - Inicia el bot y muestra el mensaje de bienvenida
- `/help` - Muestra la ayuda
- `Ofertas` - Busca ofertas laborales actuales (palabra clave)

## 📁 Estructura del Proyecto

```
Jobs-Market-Cuba/
├── bot/
│   ├── __init__.py
│   ├── main.py                 # Entry point del bot
│   ├── handlers.py             # Handlers de Telegram
│   ├── config.py               # Configuración
│   └── utils/
│       ├── __init__.py
│       ├── formatter.py        # Formateador HTML
│       └── logger.py           # Setup de logging
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py         # Clase base para scrapers
│   ├── revolico_scraper.py     # Scraper de Revolico
│   ├── cubisima_scraper.py     # Scraper de Cubisima
│   ├── cucoders_scraper.py     # Scraper de CuCoders
│   └── scraper_manager.py      # Orquestador de scrapers
├── filters/
│   ├── __init__.py
│   └── job_filter.py           # Filtrado de ofertas
├── tests/
│   ├── __init__.py
│   ├── test_filters.py         # Tests de filtros
│   └── test_scrapers.py        # Tests de scrapers
├── .env.example                # Ejemplo de configuración
├── .gitignore
├── requirements.txt
├── run.py                      # Script de ejecución
└── README.md
```

## ⚙️ Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | Requerido |
| `REQUEST_TIMEOUT` | Timeout para requests HTTP (segundos) | 30 |
| `REQUEST_DELAY` | Delay entre requests (segundos) | 2 |
| `MAX_RETRIES` | Número máximo de reintentos | 3 |
| `USE_SELENIUM` | Usar Selenium para sitios con JS | false |
| `LOG_LEVEL` | Nivel de logging (DEBUG, INFO, WARNING, ERROR) | INFO |
| `HTTP_PROXY` | Proxy HTTP (opcional) | - |
| `HTTPS_PROXY` | Proxy HTTPS (opcional) | - |
| `FILTER_KEYWORDS` | Keywords para filtrado (separadas por comas) | Ver .env.example |

### Personalizar Keywords de Filtrado

Edita `FILTER_KEYWORDS` en el archivo `.env`:

```env
FILTER_KEYWORDS=inteligencia artificial,ia,ai,machine learning,diseño,design,redacción,writer,automatización,automation,bot
```

## 🧪 Testing

Ejecutar todos los tests:

```bash
pytest
```

Ejecutar tests con verbose:

```bash
pytest -v
```

Ejecutar tests con cobertura:

```bash
pytest --cov=. --cov-report=html
```

## 🔧 Desarrollo

### Agregar un nuevo scraper

1. Crea un nuevo archivo en `scrapers/` (ej: `nuevo_scraper.py`)
2. Hereda de `BaseScraper`
3. Implementa el método `scrape()`
4. Agrega el scraper a `ScraperManager`

Ejemplo:

```python
from scrapers.base_scraper import BaseScraper
from typing import List, Dict

class NuevoScraper(BaseScraper):
    
    def __init__(self):
        super().__init__("NuevoSitio")
        self.url = "https://ejemplo.com/empleos"
    
    def scrape(self) -> List[Dict[str, str]]:
        response = self._make_request(self.url)
        if not response:
            return []
        
        # Tu lógica de parsing aquí
        offers = []
        # ...
        return offers
```

### Agregar nuevas keywords de filtrado

Edita el archivo `.env` o modifica directamente en `bot/config.py`.

## 📊 Logging

Los logs se muestran en stdout con el siguiente formato:

```
2024-01-06 10:30:45 - bot.main - INFO - Starting Cuba Jobs Telegram Bot
2024-01-06 10:30:46 - scrapers.revolico_scraper - INFO - Starting scraping from Revolico
```

Niveles de log disponibles:
- `DEBUG` - Información detallada para debugging
- `INFO` - Información general del flujo
- `WARNING` - Advertencias que no detienen la ejecución
- `ERROR` - Errores que afectan funcionalidad

## 🐛 Troubleshooting

### Error: "TELEGRAM_BOT_TOKEN is required"

Asegúrate de haber creado el archivo `.env` y configurado el token correctamente.

### El bot no responde a "Ofertas"

- Verifica que el bot esté en ejecución
- Revisa los logs para errores
- Asegúrate de escribir exactamente "Ofertas" (mayúsculas/minúsculas no importan)

### Errores de scraping (403, 429)

- Aumenta `REQUEST_DELAY` en `.env`
- Configura proxies si es necesario
- Algunos sitios pueden tener protección anti-bot más agresiva

### Timeouts frecuentes

- Aumenta `REQUEST_TIMEOUT` en `.env`
- Verifica tu conexión a internet
- Considera usar `USE_SELENIUM=true` para sitios problemáticos

## 📝 Crear un Bot de Telegram

1. Habla con [@BotFather](https://t.me/botfather) en Telegram
2. Envía `/newbot`
3. Sigue las instrucciones para elegir nombre y username
4. Copia el token que te proporciona
5. Pégalo en tu archivo `.env`

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👨‍💻 Autor

Desarrollado para automatizar la búsqueda de ofertas laborales en Cuba.

## 🙏 Agradecimientos

- Comunidad de Python
- python-telegram-bot
- BeautifulSoup4
- Todas las plataformas laborales cubanas que hacen posible este proyecto

---

**Nota**: Este bot está diseñado con fines educativos y de automatización personal. Respeta los términos de servicio de las plataformas que scrapeamos.
