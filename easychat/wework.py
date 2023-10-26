import yaml
import requests
from datetime import datetime, timedelta
import xml.etree.cElementTree as ET
from .WXBizMsgCrypt3 import WXBizMsgCrypt

token = None
encoding_aes_key = None
corpid = None
secret = None

# 全局变量存储缓存的access_token和过期时间
access_token_cache = None
token_expire_time = None

wxcpt = None

def load_config(config_yaml):
    global token, encoding_aes_key, corpid, secret, wxcpt
    with open(config_yaml, 'r') as f:
        config = yaml.safe_load(f)
        token = config['token']
        encoding_aes_key = config['encoding_aes_key']
        corpid = config['corpid']
        secret = config['secret']
        wxcpt = WXBizMsgCrypt(token, encoding_aes_key, corpid)

def get_access_token(force_renew=False):
    global access_token_cache, token_expire_time

    # 如果有缓存的access_token并且它尚未过期，且没有强制刷新，直接返回缓存的token
    if access_token_cache and token_expire_time and datetime.now() < token_expire_time and not force_renew:
        return access_token_cache

    # 否则，请求新的access_token
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={secret}"
    response = requests.get(url)
    data = response.json()

    # 从API响应中提取access_token和expires_in，并设置过期时间
    if data.get("errcode") == 0 and "access_token" in data:
        access_token_cache = data["access_token"]
        expires_in = data["expires_in"]
        # 计算token的过期时间，并在实际过期前减少一分钟以确保安全
        token_expire_time = datetime.now() + timedelta(seconds=expires_in - 60)
        return access_token_cache
    else:
        # 如果出错，抛出异常
        raise Exception(f"Failed to get access_token: {data.get('errmsg')}")

def get_messages(token, cursor=None, limit=1000):
    access_token = get_access_token()
    # API endpoint
    url = f"https://qyapi.weixin.qq.com/cgi-bin/kf/sync_msg?access_token={access_token}"
    
    # Request payload
    payload = {
        "cursor": cursor if cursor else "",  # 如果cursor为None则使用空字符串
        "token": token, 
        "limit": limit,  # 默认和最大值
        "voice_format": 0,  # 默认值
        # "open_kfid": "wkxxxxxx"  # 如果需要指定客服账号则取消此行注释
    }

    # Make the POST request
    response = requests.post(url, json=payload)
    
    # Check the response status
    if response.status_code == 200:
        data = response.json()
        if data.get('errcode') == 0:
            return data  # 返回成功获取的数据
        else:
            raise Exception(f"Error from API: {data.get('errmsg')}")
    else:
        response.raise_for_status()

def send_text(touser, open_kfid, text):
    access_token = get_access_token()
    # API endpoint
    url = f"https://qyapi.weixin.qq.com/cgi-bin/kf/send_msg?access_token={access_token}"
    
    # Request payload
    payload = {
        "touser": touser,
        "open_kfid": open_kfid,
        # 如果有特定的msgid可以添加，但在这里我们允许微信系统自动生成
        "msgtype": "text",
        "text": {
            "content": text
        }
    }

    # Make the POST request
    response = requests.post(url, json=payload)
    
    # Check the response status
    if response.status_code == 200:
        data = response.json()
        if data.get('errcode') == 0:
            return data  # 返回成功的响应，包含msgid等信息
        else:
            raise Exception(f"Error from API: {data.get('errmsg')}")
    else:
        response.raise_for_status()

def send_menu(touser, open_kfid, text):
    access_token = get_access_token()
    # API endpoint
    url = f"https://qyapi.weixin.qq.com/cgi-bin/kf/send_msg?access_token={access_token}"

    # Request payload
    payload = {
        "touser": touser,
        "open_kfid": open_kfid,
        # 如果有特定的msgid可以添加，但在这里我们允许微信系统自动生成
        "msgtype": "msgmenu",
        "msgmenu": {
            "list": [
                {
                    "type": "text", 
                    "text": {
                        "content": f"{text}",
                        "no_newline": 0
                    }
                },
                {
                    "type": "click", 
                    "click": {
                        "id": "101", 
                        "content": "点此开启新会话"
                    }
                } 
                
            ], 
        }
    }

    # Make the POST request
    response = requests.post(url, json=payload)
    
    # Check the response status
    if response.status_code == 200:
        data = response.json()
        if data.get('errcode') == 0:
            return data  # 返回成功的响应，包含msgid等信息
        else:
            raise Exception(f"Error from API: {data.get('errmsg')}")
    else:
        response.raise_for_status()


def verify_url(msg_signature, timestamp, nonce, echostr):
    return wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)

def decrypt_msg(req_data, msg_signature, timestamp, nonce):
    ret, msg = wxcpt.DecryptMsg(req_data, msg_signature, timestamp, nonce)
    if ret != 0:
        return ret, msg
    else:
        xml_tree = ET.fromstring(msg)
        return ret, {
            "ToUserName": xml_tree.find("ToUserName").text,
            "CreateTime": xml_tree.find("CreateTime").text,
            "MsgType": xml_tree.find("MsgType").text,
            "Event": xml_tree.find("Event").text,
            "Token": xml_tree.find("Token").text,
            "OpenKfId": xml_tree.find("OpenKfId").text
        }

def get_conversation_status(open_kfid, external_userid):
    access_token = get_access_token()
    # API endpoint
    url = f"https://qyapi.weixin.qq.com/cgi-bin/kf/service_state/get?access_token={access_token}"
    
    # Request payload
    payload = {
        "open_kfid": open_kfid,
        "external_userid": external_userid
    }

    # Make the POST request
    response = requests.post(url, json=payload)
    
    # Check the response status
    if response.status_code == 200:
        data = response.json()
        if 'errcode' in data and data.get('errcode') == 0:
            return data  # 返回成功获取的数据
        else:
            raise Exception(f"Error from API: {data.get('errmsg', 'Unknown error')}")
    else:
        response.raise_for_status()
