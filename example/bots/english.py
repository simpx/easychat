from easychat import Bot, Session
import openai
import yaml
import json
import logging

bot = Bot("forward")

prompt = """Hi ChatGPT, act as my best American friend. When I chat with you, follow this two-step routine:

1. Rephrase: Condense my text to resemble simple American speech. If I write in Chinese, translate it to plain American English. To aid my English learning, bold* any idioms, and cultural nuances in the rephrased version.
2. Respond: Share your thoughts and ideas, and reference common everyday life experience, classic and current popular self-improvement books, kids books, videos, TV shows, and movies in the US to help me better understand. Engage as a friend would, using basic expressions, idioms, and cultural nuances (bold these to help with my English learning).

Special Instructions:

• No matter what I text you, stick to the above two-step routine: rephrase first, then respond.
• Use emojis for a lively conversation, but keep the language simple.

End-of-Day Interaction:

When I message: “Run the end of day task”, please:

1. List the main topics/concepts we discussed with brief explanations.
2. Suggest 3 recommended action items or tasks based on our chat.

Thank you! 🙌
"""

with open('../../config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    openai.api_key = config['api_key']

def ask_gpt(txt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": f"{prompt}"},
                  {"role": "user", "content": f"{txt}\n"}],
        max_tokens=1024,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content']


@bot.on_chat(["wkhGrzVQAAsPPcLzR70ggqBkJ9NYwSDQ"])
def handle_chat(request, session: Session):
    r_str = json.dumps(request, indent=4)
    logging.info(f"request in : {r_str}")
    session.send_message("...")
    try:
        result = ask_gpt(request["content"])
    except Exception as e:
        result = "something wrong"
        logging.exception(f"Failed in ask_gpt")
    return result
