from easychat import Bot, Session

bot = Bot(__name__)

@bot.on_chat(["wkhGrzVQAAsPPcLzR70ggqBkJ9NYwSDQ"])
def handle_chat(request, session: Session):
    return "hello from second_bot"
