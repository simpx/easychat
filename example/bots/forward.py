from easychat import Bot, Session
import openai
import yaml
import json
import logging

bot = Bot("forward")

with open('../../config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    openai.api_key = config['api_key']

def ask_gpt(txt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "你是一个专业、精准、简洁的助手"},
                  {"role": "user", "content": f"{txt}\n"}],
        max_tokens=1024,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content']


@bot.on_chat(["wkhGrzVQAAZ3gXdLV_HJM1V00Y_4QjiA"])
def handle_chat(request, session: Session):
    r_str = json.dumps(request, indent=4)
    logging.info(f"request in : {r_str}")
    session.send_message("思考中...")
    try:
        result = ask_gpt(request["content"])
    except Exception as e:
        result = "出错了，请重试"
        logging.exception(f"Failed in ask_gpt")
    return result
