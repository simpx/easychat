from easychat import EasyChat, Session
import json
import logging
import requests
import yaml
import openai

logging.basicConfig(level=logging.DEBUG)

app = EasyChat("/verify_url", "HHFq49uYHoiCuZRv9Skq")
app.load_config("config.yaml")

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    openai.api_key = config['api_key']

def ask_gpt(txt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "你是一个专业、精准、简洁的助手"},
                  {"role": "user", "content": f"{txt}\n"}],
        max_tokens=500,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content']

@app.on_chat([".*"])
def handle_chat(request, session: Session):
    r_str = json.dumps(request, indent=4)
    logging.info(f"request in : {r_str}")
    session.send_message("思考中...")
    return ask_gpt(request["content"])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8899)
