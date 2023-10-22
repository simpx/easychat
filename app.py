from flask import Flask, request, make_response
import yaml
import logging
import json
import openai
from easy_wework import get_messages, send_text, load_config, send_menu
import easy_wework

# 设置日志格式
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# 从config.yaml加载配置
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    sApikey = config['api_key']

load_config('config.yaml')
openai.api_key = sApikey


@app.route('/verify_url', methods=['GET'])
def verify_url():
    sVerifyMsgSig = request.args.get('msg_signature')
    sVerifyTimeStamp = request.args.get('timestamp')
    sVerifyNonce = request.args.get('nonce')
    sVerifyEchoStr = request.args.get('echostr')

    ret, sEchoStr = easy_wework.verify_url(sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)
    if ret != 0:
        logging.error(f"Failed in VerifyURL, error code: {ret}")
        return "ERROR", 403
    return sEchoStr

def ask_gpt(txt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "你是一个专业、精准、简洁的助手"},
                  {"role": "user", "content": f"{txt}\n"}],
        max_tokens=500,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content']

with open('cursor', 'r') as f:
    cursor = f.read().strip()

@app.route('/verify_url', methods=['POST'])
def weixin():
    global cursor
    sReqMsgSig = request.args.get('msg_signature')
    sReqTimeStamp = request.args.get('timestamp')
    sReqNonce = request.args.get('nonce')
    sReqData = request.data

    ret, req = easy_wework.decrypt_msg(sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
    if ret != 0:
        logging.error(f"Failed in DecryptMsg, error code: {ret}")
        return "ERROR", 403

    messages = get_messages(req['Token'], cursor)
    cursor = messages['next_cursor']
    logging.info(f"cursor is: {cursor}")
    with open('cursor', 'w+') as f:
        f.write(cursor)
    for message in messages['msg_list']:
        if message['msgtype'] != 'text' or "menu_id" in message['text']:
            message_str = json.dumps(message, indent=4)
            logging.info(f"Skip message : {message_str}")
            continue
        try:
            answer = ask_gpt(message['text']['content'])
            if len(answer) < 255:
                send_menu(message['external_userid'], message['open_kfid'], answer)
            else:
                send_text(message['external_userid'], message['open_kfid'], answer)
                send_menu(message['external_userid'], message['open_kfid'], "点击")
            message_str = json.dumps(message, indent=4)
            logging.info(f"Success in : {message_str}")
        except Exception as e:
            message_str = json.dumps(message, indent=4)
            logging.exception(f"Failed in send_text: {message_str}")
            
    return ''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8899)
