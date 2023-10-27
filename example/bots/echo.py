from easychat import Bot, Session
bot = Bot("echo")

@bot.on_chat(["wkhGrzVQAAMX3qxA6IUkn7CVZc3DkHPQ"])
def handle_chat(request, session: Session):
    return request["content"]
