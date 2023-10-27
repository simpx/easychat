import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from easychat import EasyChat, Session
import json
import logging
import requests
import yaml
import openai
logging.basicConfig(level=logging.DEBUG)

import echo
import forward

if __name__ == "__main__":
    app = EasyChat("/verify_url", "HHFq49uYHoiCuZRv9Viy")
    app.load_config("../../config.yaml")
    app.serve(echo.bot)
    app.serve(forward.bot)
    app.run(host='0.0.0.0', port=8899)
