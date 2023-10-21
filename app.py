from flask import Flask, request, make_response
import xml.etree.cElementTree as ET
import yaml
import logging
from weworkapi_python.callback.WXBizMsgCrypt3 import WXBizMsgCrypt
from easy_wework import get_access_token

# 设置日志格式
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# 从config.yaml加载配置
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    sToken = config['token']
    sEncodingAESKey = config['encoding_aes_key']
    sCorpID = config['corp_id']

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


@app.route('/verify_url', methods=['POST'])
def weixin():
    sReqMsgSig = request.args.get('msg_signature')
    sReqTimeStamp = request.args.get('timestamp')
    sReqNonce = request.args.get('nonce')
    sReqData = request.data

    ret, sMsg = wxcpt.DecryptMsg(sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
    if ret != 0:
        logging.error(f"Failed in DecryptMsg, error code: {ret}")
        return "ERROR", 403

    xml_tree = ET.fromstring(sMsg)
    for elem in xml_tree.iter():
        logging.info(f"Element: {elem.tag} - Text: {elem.text}")
    content = xml_tree.find("Content").text

    # 回复相同的消息内容
    response = """
    <xml>
    <ToUserName><![CDATA[{}]]></ToUserName>
    <FromUserName><![CDATA[{}]]></FromUserName>
    <CreateTime>{}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{}]]></Content>
    </xml>
    """.format(xml_tree.find("FromUserName").text, xml_tree.find("ToUserName").text, xml_tree.find("CreateTime").text, content)

    ret, sEncryptMsg = wxcpt.EncryptMsg(response, sReqNonce)
    if ret != 0:
        logging.error(f"Failed in EncryptMsg, error code: {ret}")
        return "ERROR", 403
    return sEncryptMsg

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8899)
