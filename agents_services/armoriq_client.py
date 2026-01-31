import os
import logging
from armoriq_sdk import ArmorIQClient

# Use provided API Key
API_KEY = os.getenv("ARMORIQ_API_KEY", "ak_live_9bede6a0b8d15422799b36d7806c895157455094c75a594af327138fd4c150f6")
USER_ID = os.getenv("ARMORIQ_USER_ID", "user_fair_hiring")
AGENT_ID = os.getenv("ARMORIQ_AGENT_ID", "agent_orchestrator")

_client = None
logger = logging.getLogger("armoriq_client")

def get_armoriq_client() -> ArmorIQClient:
    global _client
    if _client is None:
        try:
            logger.info(f"Initializing ArmorIQ Client with UserID: {USER_ID}")
            _client = ArmorIQClient(
                api_key=API_KEY,
                user_id=USER_ID,
                agent_id=AGENT_ID
            )
            logger.info("ArmorIQ Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ArmorIQ Client: {str(e)}")
            raise
    return _client
