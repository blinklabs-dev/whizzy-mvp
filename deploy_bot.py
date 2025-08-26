#!/usr/bin/env python3
"""
Whizzy Bot Deployment Script
Starts the bot for real testing with proper monitoring and error handling.
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from whizzy_bot import WhizzyBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"🛑 Received signal {signum}, shutting down deployment...")
    sys.exit(0)

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'SLACK_APP_TOKEN',
        'SLACK_BOT_TOKEN',
        'SALESFORCE_USERNAME',
        'SALESFORCE_PASSWORD',
        'SALESFORCE_SECURITY_TOKEN',
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file and ensure all variables are set.")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def main():
    """Main deployment function"""
    logger.info("🚀 Starting Whizzy Bot Deployment...")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check environment
    if not check_environment():
        logger.error("❌ Environment check failed. Exiting.")
        sys.exit(1)
    
    try:
        # Initialize and start the bot
        logger.info("🤖 Initializing Whizzy Bot...")
        bot = WhizzyBot()
        
        logger.info("✅ Bot initialized successfully!")
        logger.info("📱 Bot is now ready to receive requests!")
        logger.info("🛑 Press Ctrl+C to stop the bot")
        
        # Start the bot
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Error during bot deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
