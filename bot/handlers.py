from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from scrapers.scraper_manager import ScraperManager
from bot.utils.formatter import HTMLFormatter
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class BotHandlers:
    
    def __init__(self):
        self.scraper_manager = ScraperManager()
        self.formatter = HTMLFormatter()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        welcome_message = f"""<b>¡Hola {user.first_name}! 👋</b>

Soy tu asistente para buscar ofertas laborales en Cuba 🇨🇺

<b>¿Cómo usar el bot?</b>
Simplemente escribe: <code>Ofertas</code>

El bot buscará automáticamente en:
• Revolico
• Cubisima
• CuCoders

<b>Categorías de filtrado:</b>
✨ Inteligencia Artificial
🎨 Diseño
📝 Redacción
🤖 Automatizaciones

<i>¡Empieza ahora escribiendo "Ofertas"!</i>"""
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.HTML
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"User {update.effective_user.id} requested help")
        
        help_message = """<b>📖 Ayuda - Bot de Ofertas Laborales</b>

<b>Comandos disponibles:</b>
/start - Inicia el bot y muestra el mensaje de bienvenida
/help - Muestra este mensaje de ayuda
<code>Ofertas</code> - Busca ofertas laborales actuales

<b>¿Qué hace este bot?</b>
Busca ofertas de trabajo en múltiples plataformas cubanas y las filtra según tus intereses:
• Inteligencia Artificial y Machine Learning
• Diseño gráfico y UX/UI
• Redacción y contenido
• Automatizaciones y desarrollo

<b>Plataformas que consulta:</b>
• Revolico (empleos)
• Cubisima (marketing, diseño, IT)
• CuCoders (desarrollo)

<i>El proceso puede tomar unos segundos, ¡ten paciencia!</i>"""
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.HTML
        )
    
    async def ofertas_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) requested job offers")
        
        searching_msg = await update.message.reply_text(
            self.formatter.format_searching_message(),
            parse_mode=ParseMode.HTML
        )
        
        try:
            offers = await self.scraper_manager.scrape_all()
            
            result_html = self.formatter.format_job_offers(offers)
            
            # Agregar métricas al final (si están disponibles)
            metrics_summary = ""
            try:
                from scrapers.metrics import ScrapingMetrics
                # Obtener métricas de todos los scrapers
                total_metrics = ScrapingMetrics()
                for scraper in self.scraper_manager.scrapers:
                    if hasattr(scraper, 'metrics'):
                        # Merge métricas
                        total_metrics.total_requests += scraper.metrics.total_requests
                        total_metrics.successful_requests += scraper.metrics.successful_requests
                        total_metrics.failed_requests += scraper.metrics.failed_requests
                        total_metrics.cached_requests += scraper.metrics.cached_requests
                        total_metrics.retry_requests += scraper.metrics.retry_requests
                        total_metrics.proxy_failures += scraper.metrics.proxy_failures
                
                if total_metrics.total_requests > 0:
                    # Agregar summary pequeño al final del resultado
                    metrics_summary = f"\n\n📊 <b>Estadísticas:</b>\n"
                    metrics_summary += f"✅ Requests exitosas: {total_metrics.successful_requests}\n"
                    metrics_summary += f"❌ Requests fallidas: {total_metrics.failed_requests}\n"
                    metrics_summary += f"💾 Cache hits: {total_metrics.cached_requests}\n"
                    metrics_summary += f"🔄 Reintentos: {total_metrics.retry_requests}\n"
                    metrics_summary += f"🌐 Fallos de proxy: {total_metrics.proxy_failures}\n"
                    metrics_summary += f"📈 Tasa de éxito: {total_metrics.get_success_rate():.1f}%"
            except:
                pass
            
            full_message = result_html + metrics_summary
            
            # Telegram tiene un límite de 4096 caracteres por mensaje
            MAX_MESSAGE_LENGTH = 4000  # Dejamos margen de seguridad
            
            if len(full_message) <= MAX_MESSAGE_LENGTH:
                # El mensaje cabe en un solo envío
                await searching_msg.edit_text(
                    full_message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            else:
                # Dividir el mensaje en partes
                # Primero eliminamos el mensaje de "buscando..."
                await searching_msg.delete()
                
                # Dividir por ofertas individuales para no cortar a mitad de una oferta
                parts = self._split_message_by_offers(full_message, MAX_MESSAGE_LENGTH)
                
                for i, part in enumerate(parts):
                    if i == 0:
                        header = f"<b>📋 Ofertas de trabajo ({i+1}/{len(parts)})</b>\n\n"
                    else:
                        header = f"<b>📋 Continuación ({i+1}/{len(parts)})</b>\n\n"
                    
                    await update.message.reply_text(
                        header + part,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
            
            logger.info(f"Successfully sent {len(offers)} offers to user {user.id}")
        
        except Exception as e:
            logger.error(f"Error processing ofertas request: {str(e)}", exc_info=True)
            
            error_html = self.formatter.format_error_message()
            await searching_msg.edit_text(
                error_html,
                parse_mode=ParseMode.HTML
            )
    
    def _split_message_by_offers(self, message: str, max_length: int) -> list:
        """Divide el mensaje en partes respetando el límite de caracteres."""
        parts = []
        current_part = ""
        
        # Dividir por doble salto de línea (separador típico entre ofertas)
        sections = message.split("\n\n")
        
        for section in sections:
            # Si agregar esta sección excede el límite
            if len(current_part) + len(section) + 2 > max_length:
                if current_part:
                    parts.append(current_part.strip())
                current_part = section
            else:
                if current_part:
                    current_part += "\n\n" + section
                else:
                    current_part = section
        
        # Agregar la última parte
        if current_part:
            parts.append(current_part.strip())
        
        return parts if parts else [message[:max_length]]
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.debug(f"User {update.effective_user.id} sent unknown command: {update.message.text}")
        
        message = """<b>⚠️ Comando no reconocido</b>

Para buscar ofertas, escribe: <code>Ofertas</code>

Para ver los comandos disponibles: /help"""
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML
        )
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
        
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "Ha ocurrido un error inesperado. Por favor, intenta nuevamente.",
                parse_mode=ParseMode.HTML
            )
