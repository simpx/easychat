import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from easychat import EasyChat, Session
import json
import logging
from second_bot import bot
logging.basicConfig(level=logging.DEBUG)

app = EasyChat("/verify_url", "HHFq49uYHoiCuZRv9Rqs")
app.load_config("config.yaml")

@app.on_chat(["wkhGrzVQAAZ3gXdLV_HJM1V00Y_4QjiA"])
def handle_chat(request, session: Session):
    r_str = json.dumps(request, indent=4)
    print(f"request: {r_str}")

    session.send_message(request["content"])
    return "Goodbye and take care!"

if __name__ == "__main__":
    app.serve(bot)
    app.run(host='0.0.0.0', port=8899)
