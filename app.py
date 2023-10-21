from flask import Flask, request, make_response
import xml.etree.cElementTree as ET
import yaml
import logging
import json
from weworkapi_python.callback.WXBizMsgCrypt3 import WXBizMsgCrypt
from easy_wework import get_messages, send_text, load_config

# 设置日志格式
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# 从config.yaml加载配置
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    sToken = config['token']
    sEncodingAESKey = config['encoding_aes_key']
    sCorpID = config['corpid']
    sSecret = config['secret']

load_config('config.yaml')

wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)

@app.route('/verify_url', methods=['GET'])
def verify_url():
    sVerifyMsgSig = request.args.get('msg_signature')
    sVerifyTimeStamp = request.args.get('timestamp')
    sVerifyNonce = request.args.get('nonce')
    sVerifyEchoStr = request.args.get('echostr')

    ret, sEchoStr = wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp, sVerifyNonce, sVerifyEchoStr)
    if ret != 0:
        logging.error(f"Failed in VerifyURL, error code: {ret}")
        return "ERROR", 403
    return sEchoStr


cursor = None
@app.route('/verify_url', methods=['POST'])
def weixin():
    global cursor
    sReqMsgSig = request.args.get('msg_signature')
    sReqTimeStamp = request.args.get('timestamp')
    sReqNonce = request.args.get('nonce')
    sReqData = request.data

    ret, sMsg = wxcpt.DecryptMsg(sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
    if ret != 0:
        logging.error(f"Failed in DecryptMsg, error code: {ret}")
        return "ERROR", 403

    xml_tree = ET.fromstring(sMsg)
    req = {
        "ToUserName": xml_tree.find("ToUserName").text,
        "CreateTime": xml_tree.find("CreateTime").text,
        "MsgType": xml_tree.find("MsgType").text,
        "Event": xml_tree.find("Event").text,
        "Token": xml_tree.find("Token").text,
        "OpenKfId": xml_tree.find("OpenKfId").text
    }

    messages = get_messages(req['Token'], cursor)
    cursor = messages['next_cursor']
    for message in messages['msg_list']:
        try:
            send_text(message['external_userid'], message['open_kfid'], message['text']['content'])
        except Exception as e:
            message_str = json.dumps(message, indent=4)
            logging.error(f"Failed in send_text: {message_str}")
            
    return ''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8899)
