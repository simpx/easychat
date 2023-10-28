import json
from easychat import Bot, Session
bot = Bot("echo")

@bot.on_chat(["wkhGrzVQAAMX3qxA6IUkn7CVZc3DkHPQ"])
def handle_chat(request, session: Session):
    histroy = json.dumps(session.messages, indent=4, ensure_ascii=False)
    result = request["content"]
    return f"histroy: {histroy}\ncurrent: {result}"
