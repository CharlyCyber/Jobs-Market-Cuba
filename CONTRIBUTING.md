# 🤝 Guía de Contribución

¡Gracias por tu interés en contribuir al Bot de Ofertas Laborales Cuba! 

## 🌟 Cómo Contribuir

### 1. Fork el Repositorio

Haz clic en el botón "Fork" en la parte superior derecha de la página del repositorio.

### 2. Clona tu Fork

```bash
git clone https://github.com/tu-usuario/Jobs-Market-Cuba.git
cd Jobs-Market-Cuba
```

### 3. Crea una Rama

```bash
git checkout -b feature/nombre-de-tu-feature
```

Tipos de ramas:
- `feature/` - Nueva funcionalidad
- `fix/` - Corrección de bug
- `docs/` - Documentación
- `refactor/` - Refactorización de código
- `test/` - Agregar o modificar tests

### 4. Configura el Entorno

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Realiza tus Cambios

- Sigue las convenciones de código del proyecto
- Escribe tests para tu código
- Asegúrate de que todos los tests pasen
- Actualiza la documentación si es necesario

### 6. Ejecuta los Tests

```bash
pytest
```

### 7. Commit tus Cambios

Usa mensajes de commit claros y descriptivos:

```bash
git add .
git commit -m "feat: agregar soporte para nueva plataforma XYZ"
```

Formato de mensajes de commit:
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Cambios en documentación
- `style:` - Formateo, sin cambios de código
- `refactor:` - Refactorización de código
- `test:` - Agregar o modificar tests
- `chore:` - Mantenimiento

### 8. Push a tu Fork

```bash
git push origin feature/nombre-de-tu-feature
```

### 9. Crea un Pull Request

1. Ve a tu fork en GitHub
2. Haz clic en "New Pull Request"
3. Selecciona la rama que creaste
4. Describe tus cambios en detalle
5. Envía el Pull Request

## 📝 Estándares de Código

### Python Style Guide

Seguimos PEP 8 con algunas excepciones:

- Longitud máxima de línea: 100 caracteres
- Usa 4 espacios para indentación
- Nombres de variables y funciones en snake_case
- Nombres de clases en PascalCase
- Constantes en UPPER_CASE

### Ejemplo de Código Bien Formateado

```python
from typing import List, Dict


class MiScraper:
    
    def __init__(self, url: str):
        self.url = url
        self.results = []
    
    def scrape(self) -> List[Dict[str, str]]:
        offers = self._fetch_offers()
        filtered_offers = self._filter_offers(offers)
        return filtered_offers
    
    def _fetch_offers(self) -> List[Dict[str, str]]:
        # Implementación
        pass
    
    def _filter_offers(self, offers: List[Dict[str, str]]) -> List[Dict[str, str]]:
        # Implementación
        pass
```

## 🧪 Tests

### Escribir Tests

Todos los nuevos features deben incluir tests:

```python
import pytest
from mi_modulo import MiClase


class TestMiClase:
    
    def setup_method(self):
        self.instance = MiClase()
    
    def test_funcionalidad_basica(self):
        result = self.instance.metodo()
        assert result == expected_value
    
    def test_manejo_de_errores(self):
        with pytest.raises(ValueError):
            self.instance.metodo_con_error()
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_scrapers.py

# Con cobertura
pytest --cov=.

# Verbose
pytest -v
```

## 🐛 Reportar Bugs

### Antes de Reportar

1. Busca si el bug ya fue reportado
2. Verifica que estés usando la última versión
3. Reproduce el bug de manera consistente

### Cómo Reportar

Crea un issue en GitHub con:

1. **Título descriptivo**
2. **Descripción del problema**
3. **Pasos para reproducir**
   ```
   1. Hacer X
   2. Hacer Y
   3. Ver error
   ```
4. **Comportamiento esperado**
5. **Comportamiento actual**
6. **Logs de error** (si aplica)
7. **Entorno**
   - OS: [ej. Ubuntu 22.04]
   - Python: [ej. 3.10.5]
   - Versión del bot: [ej. 1.0.0]

## 💡 Sugerir Mejoras

### Ideas de Contribución

- Agregar nuevas plataformas de scraping
- Mejorar algoritmos de filtrado
- Optimizar rendimiento
- Agregar nuevas funcionalidades al bot
- Mejorar documentación
- Traducir a otros idiomas
- Agregar tests

### Cómo Sugerir

1. Abre un issue en GitHub
2. Usa el prefijo `[FEATURE]` o `[ENHANCEMENT]`
3. Describe la mejora en detalle
4. Explica por qué sería útil
5. Proporciona ejemplos si es posible

## 📚 Áreas de Contribución

### 1. Scrapers

Agregar soporte para nuevas plataformas:

```python
from scrapers.base_scraper import BaseScraper
from typing import List, Dict


class NuevoScraper(BaseScraper):
    
    def __init__(self):
        super().__init__("NombrePlataforma")
        self.url = "https://ejemplo.com/empleos"
    
    def scrape(self) -> List[Dict[str, str]]:
        # Tu implementación aquí
        pass
```

### 2. Filtros

Mejorar el sistema de filtrado:

- Algoritmos de ML para clasificación
- Análisis de sentimiento
- Detección de idioma
- Scoring de relevancia

### 3. Bot de Telegram

Nuevas funcionalidades:

- Notificaciones automáticas
- Suscripciones a categorías
- Guardado de ofertas favoritas
- Compartir ofertas
- Estadísticas de búsqueda

### 4. Documentación

- Tutoriales
- Ejemplos de uso
- Videos
- Traducciones
- FAQ

### 5. Testing

- Tests de integración
- Tests end-to-end
- Tests de rendimiento
- Tests de carga

## 🔍 Code Review

### Lo que Buscamos

- ✅ Código limpio y legible
- ✅ Tests que pasen
- ✅ Documentación actualizada
- ✅ Sigue las convenciones del proyecto
- ✅ Sin conflictos de merge
- ✅ Commits atómicos y bien descritos

### Lo que Evitamos

- ❌ Código sin tests
- ❌ Cambios no relacionados en el mismo PR
- ❌ Código comentado sin usar
- ❌ Prints para debugging
- ❌ Cambios de formateo masivos
- ❌ Dependencias innecesarias

## 📋 Checklist antes de PR

- [ ] Los tests pasan localmente
- [ ] Agregué tests para mi código
- [ ] Actualicé la documentación
- [ ] El código sigue el style guide
- [ ] Escribí mensajes de commit descriptivos
- [ ] Mi PR tiene un título descriptivo
- [ ] Describí los cambios en el PR
- [ ] No hay conflictos con la rama main

## 🎯 Prioridades Actuales

Ver el archivo [ROADMAP.md](ROADMAP.md) para las prioridades actuales del proyecto.

## 💬 Comunicación

- **Issues**: Para bugs y features
- **Pull Requests**: Para contribuciones de código
- **Discussions**: Para preguntas y discusiones generales

## 📜 Código de Conducta

### Nuestro Compromiso

Crear un ambiente inclusivo, acogedor y libre de acoso.

### Comportamiento Esperado

- Ser respetuoso con diferentes puntos de vista
- Aceptar críticas constructivas
- Enfocarse en lo mejor para la comunidad
- Mostrar empatía hacia otros miembros

### Comportamiento Inaceptable

- Lenguaje ofensivo o discriminatorio
- Ataques personales
- Acoso público o privado
- Compartir información privada sin permiso

## 🙏 Reconocimientos

Todos los contribuidores serán reconocidos en el archivo [CONTRIBUTORS.md](CONTRIBUTORS.md).

## ❓ Preguntas

Si tienes preguntas sobre cómo contribuir, no dudes en:

1. Abrir un issue con la etiqueta `question`
2. Iniciar una discusión en GitHub Discussions

---

¡Gracias por contribuir! 🚀🇨🇺
