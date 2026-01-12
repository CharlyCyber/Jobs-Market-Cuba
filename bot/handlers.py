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
    
    async def debug_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Debug handler to log all text messages for troubleshooting"""
        logger.info(f"DEBUG - Received message: '{update.message.text}' from user {update.effective_user.id} ({update.effective_user.username})")
        logger.info(f"DEBUG - Chat ID: {update.effective_chat.id} | Is command? {update.message.text.startswith('/')}")
    
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
            
            await searching_msg.edit_text(
                result_html,
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
