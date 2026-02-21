import os
import requests
import logging

# Configure logging
logger = logging.getLogger("telegram_client")
logging.basicConfig(level=logging.INFO)

import config

def send_telegram_message(message: str):
    """
    Sends a text message to the configured Telegram chat.
    Raises Exception on failure to ensure strict task accounting.
    """
    # If credentials are missing in the running state, attempt a dynamic reload
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        logger.info("Credentials missing in current process. Attempting dynamic reload...")
        config.reload_config()

    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        err_msg = "Telegram credentials missing even after reload. Action aborted."
        logger.error(err_msg)
        raise ValueError(err_msg)

    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Telegram notification sent successfully.")
        return True
    except Exception as e:
        err_msg = f"Failed to send Telegram message: {e}"
        logger.error(err_msg)
        raise RuntimeError(err_msg)
