import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.config import Config
from bot.handlers import BotHandlers
from bot.utils.logger import setup_logger

logger = setup_logger(__name__)


class TelegramBot:
    
    def __init__(self):
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            sys.exit(1)
        
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.handlers = BotHandlers()
        self.application = None
        logger.info("TelegramBot initialized successfully")
    
    def setup_handlers(self):
        # Debug handler - log all text messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.debug_message))
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handlers.start_command))
        self.application.add_handler(CommandHandler("help", self.handlers.help_command))
        
        # Main search handler
        ofertas_filter = filters.TEXT & filters.Regex(r'(?i)^\s*ofertas\s*$')
        self.application.add_handler(MessageHandler(ofertas_filter, self.handlers.ofertas_handler))
        
        # Unknown command handler
        self.application.add_handler(
            MessageHandler(filters.COMMAND, self.handlers.unknown_command)
        )
        
        # Error handler
        self.application.add_error_handler(self.handlers.error_handler)
        
        logger.info("All handlers registered successfully")
    
    async def post_init(self, application: Application):
        logger.info("Bot is starting up...")
        bot_info = await application.bot.get_me()
        logger.info(f"Bot @{bot_info.username} is ready to receive messages")
    
    async def post_shutdown(self, application: Application):
        logger.info("Bot is shutting down...")
    
    def run(self):
        logger.info("Building application...")
        
        self.application = (
            Application.builder()
            .token(self.token)
            .post_init(self.post_init)
            .post_shutdown(self.post_shutdown)
            .build()
        )
        
        self.setup_handlers()
        
        logger.info("Starting bot polling...")
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )


def main():
    logger.info("=" * 50)
    logger.info("Starting Cuba Jobs Telegram Bot")
    logger.info("=" * 50)
    
    bot = TelegramBot()
    bot.run()


if __name__ == "__main__":
    main()
