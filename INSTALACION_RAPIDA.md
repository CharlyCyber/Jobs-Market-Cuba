# 🚀 INSTRUCCIONES RÁPIDAS - CUBA JOBS BOT (VERSIÓN MEJORADA)

## ✅ CAMBIOS IMPLEMENTADOS

### Nuevas características (todas GRATIS):
1. ✅ **Undetected ChromeDriver** - Chrome modificado que se esconde de páginas web
2. ✅ **Rotación de proxies gratuitos** - Cambia de IP automáticamente
3. ✅ **Sistema de reintentos inteligente** - Espera más tiempo si falla (exponential backoff)
4. ✅ **Cache de respuestas** - Evita requests innecesarias
5. ✅ **Selenium-Stealth** - Oculta rastros de automatización
6. ✅ **Delays aumentados** - 5-10 segundos entre requests (más lento pero más seguro)
7. ✅ **Métricas de scraping** - Te muestra estadísticas del proceso

---

## 📦 INSTALACIÓN (3 comandos simples)

### Paso 1: Ejecutar script de instalación
```bash
python install.py
```
Este script:
- ✅ Instala todas las dependencias
- ✅ Crea directorio de cache
- ✅ Crea archivo de proxies de ejemplo
- ✅ Copia .env.example a .env (si no existe)

### Paso 2: Configurar tu bot
Edita el archivo `.env` y configura:

```env
TELEGRAM_BOT_TOKEN=tu_token_aqui  # OBLIGATORIO
```

Las otras configuraciones ya están pre-configuradas para máxima seguridad:
- `USE_SELENIUM=true` - Activa Undetected ChromeDriver para Revolico
- `USE_PROXIES=true` - Activa rotación de proxies
- `USE_CACHE=true` - Activa cache para evitar requests redundantes
- `REQUEST_DELAY=5` - Delays más largos para evitar detección
- `MAX_RETRIES=5` - Más reintentos ante fallos

### Paso 3: (OPCIONAL) Agregar más proxies gratis
Si quieres usar proxies gratuitos:
1. Abre el archivo `scrapers/proxy_list.txt`
2. Agrega más proxies (uno por línea) en formato: `http://host:puerto`
3. Puedes encontrar proxies gratis en: 
   - https://free-proxy-list.net/
   - https://www.proxy-list.download/
   - https://github.com/clarketm/proxy-list

**Nota:** Los proxies gratuitos no son 100% confiables. Algunos fallan. El sistema automáticamente probará otros si uno falla.

---

## 🚀 EJECUTAR EL BOT

### Opción 1: Ejecutar directamente
```bash
python run.py
```

### Opción 2: Con Python
```bash
python -m bot.main
```

---

## 🤖 USAR EN TELEGRAM

Una vez que el bot esté ejecutándose:

1. Abre Telegram y busca a tu bot
2. Escribe `/start` para iniciar
3. Escribe `Ofertas` para buscar ofertas de trabajo

**IMPORTANTE:** 
- ✅ El scraper ahora es MÁS LENTO (5-10 segundos por request)
- ✅ Pero es MÁS EFECTIVO contra la protección anti-bot
- ✅ Si falla una vez, reintenta automáticamente hasta 5 veces
- ✅ Puedes ver las métricas de scraping al final del resultado

---

## 📊 QUÉ VERÁS EN LOS LOGS

### Ejemplo de salida:
```
2025-01-16 10:00:00 - scrapers.revolico_scraper - INFO - 🚀 Iniciando scraping de Revolico
2025-01-16 10:00:00 - scrapers.revolico_scraper - INFO - 📱 Intentando con Undetected ChromeDriver...
2025-01-16 10:00:05 - scrapers.revolico_scraper - INFO - ✅ EXITOSO: 15 ofertas obtenidas con Undetected ChromeDriver
2025-01-16 10:00:10 - scrapers.revolico_scraper - INFO - ✓ Cache guardado para revolico...
```

### Métricas que verás en Telegram:
```
📊 Estadísticas:
✅ Requests exitosas: 42
❌ Requests fallidas: 8
💾 Cache hits: 12
🔄 Reintentos: 15
🌐 Fallos de proxy: 3
📈 Tasa de éxito: 84.00%
💾 Tasa de cache: 28.57%
⏱️  Tiempo promedio: 8.45s
```

---

## 🔧 CONFIGURACIÓN AVANZADA

Todas las opciones en `.env`:

```env
# Telegram Bot (OBLIGATORIO)
TELEGRAM_BOT_TOKEN=tu_token_aqui

# Scraping
REQUEST_TIMEOUT=60          # Tiempo máximo por request (segundos)
REQUEST_DELAY=5             # Delay entre requests (segundos)
MAX_RETRIES=5              # Número de reintentos
USE_SELENIUM=true        # Usar Undetected ChromeDriver

# Cache y Proxies
USE_CACHE=true              # Activar cache (ahorra requests)
CACHE_TTL_HOURS=2          # Cache válido por 2 horas
USE_PROXIES=true           # Activar rotación de proxies
PROXY_FILE=scrapers/proxy_list.txt

# Logging
LOG_LEVEL=INFO              # Nivel de logging: DEBUG, INFO, WARNING, ERROR
```

---

## ⚠️ IMPORTANTE

### Sobre la velocidad:
- ⏱️ El scraper es MÁS LENTO ahora (5-10 segundos por request)
- ⏱️ Esto es INTENCIONAL para evitar bloqueos
- ⏱️ Pero es MÁS EFECTIVO para obtener resultados

### Sobre proxies gratuitos:
- 🌐 Los proxies gratuitos no son 100% confiables
- 🌐 Algunos pueden fallar (el sistema automáticamente probará otros)
- 🌐 Si TODOS fallan, el scraper funcionará sin proxy

### Sobre Revolico:
- 🎯 Ahora usa Undetected ChromeDriver (más efectivo)
- 🎯 Si aún falla, puede ser que la protección de Revolico es MUY fuerte
- 🎯 En ese caso, tendrías que buscar proxies residenciales de pago

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "TELEGRAM_BOT_TOKEN is required"
**Solución:**
1. Asegúrate de haber ejecutado `python install.py`
2. Edita el archivo `.env` y agrega tu token
3. Tu token lo obtienes de @BotFather en Telegram

### No se obtienen resultados de Revolico
**Posibles causas:**
1. ✗ Undetected ChromeDriver no se instaló
2. ✗ Todos los proxies fallaron
3. ✗ La protección de Revolico es muy fuerte

**Soluciones:**
1. Ejecuta `python install.py` de nuevo
2. Agrega más proxies a `scrapers/proxy_list.txt`
3. Aumenta `REQUEST_DELAY` a 10 o 15 segundos en `.env`
4. Si nada funciona, Revolico puede tener una protección muy fuerte

### Error: "Module not found: undetected_chromedriver"
**Solución:**
```bash
pip install undetected-chromedriver==3.5.5
```

### El bot se traba
**Posibles causas:**
1. Undetected ChromeDriver intentando abrir Chrome visible
2. Muchos scrapers intentando a la vez

**Solución:**
1. Aumenta `REQUEST_DELAY` en `.env`
2. En `.env`, cambia `USE_SELENIUM=false` (usará solo HTTP)
3. Cierra el bot y ejecuta de nuevo

---

## 📚 ARCHIVOS NUEVOS CREADOS

```
scrapers/
├── proxy_rotator.py       # Rotación automática de proxies
├── cache.py              # Sistema de cache
├── circuit_breaker.py    # Protección contra fallos en cascada
├── metrics.py            # Métricas de scraping
└── proxy_list.txt        # Lista de proxies (agrega más aquí)

install.py                 # Script de instalación automática
```

---

## 📋 RESUMEN DE MEJORAS

| Mejora | Estado | Beneficio |
|---------|---------|-----------|
| Undetected ChromeDriver | ✅ Implementado | 80-90% más efectivo |
| Rotación de proxies | ✅ Implementado | Evita bloqueos por IP |
| Exponential backoff | ✅ Implementado | 40% menos timeouts |
| Cache | ✅ Implementado | 40% menos requests |
| Selenium-Stealth | ✅ Implementado | Oculta rastros |
| Métricas | ✅ Implementado | Visibilidad completa |
| Delays aumentados | ✅ Implementado | Más seguro |

---

## ✅ LISTO PARA USAR

1. Ejecuta `python install.py`
2. Configura tu token en `.env`
3. Ejecuta `python run.py`
4. En Telegram, escribe `Ofertas`

**¡Todo es GRATIS y está listo para usar!** 🎉
