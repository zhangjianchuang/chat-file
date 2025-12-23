import json
import os
import logging

logger = logging.getLogger("app")
STATE_FILE = "data/session_state.json"

class CurrentFileState:
    def __init__(self):
        self.path: str = None
        self.file_type: str = None # 'rag' or 'pandas'

    def save(self):
        """Persist current state to disk."""
        data = {
            "path": self.path, 
            "file_type": self.file_type
        }
        try:
            # Ensure data dir exists
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            
            with open(STATE_FILE, "w") as f:
                json.dump(data, f)
            logger.info(f"💾 Session state saved: {self.path}")
        except Exception as e:
            logger.error(f"❌ Failed to save session state: {e}")

    def load(self):
        """Load state from disk."""
        if not os.path.exists(STATE_FILE):
            logger.info("No session state file found. Starting fresh.")
            return

        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                
            path = data.get("path")
            file_type = data.get("file_type")

            # Verify the file still exists on disk
            if path and os.path.exists(path):
                self.path = path
                self.file_type = file_type
                logger.info(f"♻️ Session state restored: {self.path} ({self.file_type})")
            else:
                logger.warning(f"⚠️ Saved file path {path} not found on disk. Resetting state.")
                self.path = None
                self.file_type = None
                
        except Exception as e:
            logger.error(f"❌ Failed to load session state: {e}")

# Singleton instance
current_file = CurrentFileState()