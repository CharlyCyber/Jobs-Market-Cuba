from datetime import datetime
from typing import List, Dict


class HTMLFormatter:
    
    @staticmethod
    def format_job_offers(offers: List[Dict[str, str]]) -> str:
        if not offers:
            return HTMLFormatter._format_no_offers()
        
        current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        html = f"""<b>🔍 Ofertas Laborales en Cuba</b>
📅 Fecha de búsqueda: {current_date}
📊 Total de ofertas encontradas: {len(offers)}

━━━━━━━━━━━━━━━━━━━━

"""
        
        for idx, offer in enumerate(offers, 1):
            title = offer.get('title', 'Sin título')
            company = offer.get('company', 'No especificada')
            description = offer.get('description', 'Sin descripción')
            link = offer.get('link', '#')
            source = offer.get('source', 'Fuente desconocida')
            
            description = HTMLFormatter._truncate_description(description, 150)
            
            html += f"""<b>{idx}. {title}</b>
🏢 Empresa: <i>{company}</i>
🌐 Fuente: {source}
📝 {description}
🔗 <a href="{link}">Ver oferta completa</a>

━━━━━━━━━━━━━━━━━━━━

"""
        
        html += "\n<i>✨ Filtrado por: IA, Diseño, Redacción, Automatizaciones</i>"
        
        return html
    
    @staticmethod
    def _format_no_offers() -> str:
        current_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        return f"""<b>🔍 Ofertas Laborales en Cuba</b>
📅 Fecha de búsqueda: {current_date}

❌ No se encontraron ofertas relacionadas con IA, Diseño, Redacción o Automatizaciones en este momento.

<i>Intenta nuevamente más tarde.</i>"""
    
    @staticmethod
    def _truncate_description(description: str, max_length: int = 150) -> str:
        if len(description) <= max_length:
            return description
        return description[:max_length].rsplit(' ', 1)[0] + '...'
    
    @staticmethod
    def format_error_message() -> str:
        return """<b>⚠️ Error al buscar ofertas</b>

Lo siento, ocurrió un error al intentar buscar ofertas laborales. Por favor, intenta nuevamente en unos minutos.

Si el problema persiste, contacta al administrador."""
    
    @staticmethod
    def format_searching_message() -> str:
        return """<b>🔄 Buscando ofertas laborales...</b>

Por favor espera mientras busco en múltiples plataformas:
• Revolico
• Cubisima
• CuCoders

<i>Este proceso puede tomar unos segundos...</i>"""
