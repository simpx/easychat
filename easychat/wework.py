import os
import yaml
import requests
from datetime import datetime, timedelta
from mimetypes import guess_extension
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

def send_menu(touser, open_kfid, menu_list=None):
    access_token = get_access_token()

    # API endpoint
    url = f"https://qyapi.weixin.qq.com/cgi-bin/kf/send_msg?access_token={access_token}"

    # Request payload
    payload = {
        "touser": touser,
        "open_kfid": open_kfid,
        "msgtype": "msgmenu",
        "msgmenu": {
            "head_content": "ℹ️",
            "list": menu_list,
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

def get_bots():
    access_token = get_access_token()
    # API endpoint
    url = f"https://qyapi.weixin.qq.com/cgi-bin/kf/account/list?access_token={access_token}"
    
    # Request payload
    payload = {
        "offset": 0,
        "limit": 100
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

def guess_media_type(extension):
    if extension in ['.jpg', '.jpeg', '.png', '.gif']:
        return 'image'
    elif extension in ['.mp3', '.wav']:
        return 'voice'
    elif extension in ['.mp4']:
        return 'video'
    else:
        return 'file'

def get_media(media_id, directory=None):
    """
    获取微信临时素材。

    参数:
    - media_id (str): 要获取的媒体文件的ID。
    - directory (str, optional): 指定一个目录来保存媒体文件。如果此参数为空，则返回文件内容。

    返回:
    - tuple: (filepath, media_type, content)
      - filepath (str): 文件的绝对路径。如果没有指定directory，则为None。
      - media_type (str): 表示类型的字符串，可以是'image', 'voice', 'video', 或 'file'。
      - content (bytes): 文件内容。如果指定了directory，则为None。

    注意:
    - 如果在指定的directory目录下找到与media_id匹配的文件，函数将直接返回该文件，不会重新下载。
    - 断点续传是支持的。下载的文件先带有"_temp"后缀。下载完成后，该后缀将被移除，并根据文件类型添加适当的文件扩展名。
    """
    access_token = get_access_token()
    # API endpoint
    url = f"https://qyapi.weixin.qq.com/cgi-bin/media/get?access_token={access_token}&media_id={media_id}"
    headers = {}
    # 构造文件路径
    temp_filepath = os.path.join(directory, media_id + '_temp') if directory else None
    final_filepath = os.path.join(directory, media_id) if directroy else None
    # 检查文件是否已经存在
    if directory:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                raise ValueError(f"Failed to create directory: {directory}. Error: {e}")
        for file in os.listdir(directory):
            if file.startswith(media_id) and not file.endswith('_temp'):
                extension = os.path.splitext(file)[1]
                media_type = guess_media_type(extension)
                return os.path.join(directory, file), media_type, None

    # 断点续传
    if os.path.exists(temp_filepath):
        downloaded_size = os.path.getsize(temp_filepath)
        headers['Range'] = f"bytes={downloaded_size}-"
    else:
        downloaded_size = 0

    # 下载文件
    response = requests.get(url, headers=headers, stream=True)
    # 检查HTTP状态
    if response.status_code == 416:  # 请求范围不符合要求
        pass  # 不做任何操作，等待后续处理
    elif response.status_code != 200:
        response.raise_for_status()

    # 写入文件
    if directory:
        if response.status_code != 416:
            with open(temp_filepath, 'ab') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        # 检查文件完整性
        total_size = int(response.headers.get('Content-Length', 0))
        if os.path.getsize(temp_filepath) != (downloaded_size + total_size):
            raise ValueError("文件下载不完整")

        # 重新命名文件
        extension = guess_extension(response.headers.get('Content-Type'))
        final_filepath += extension
        os.rename(temp_filepath, final_filepath)
        
        media_type = guess_media_type(extension)
        return final_filepath, media_type, None

    else:
        content = response.content
        extension = guess_extension(response.headers.get('Content-Type'))
        media_type = guess_media_type(extension)
        return None, media_type, content

def put_media(filepath, filename=None):
    """
    上传文件到微信作为客服消息的媒体素材。

    参数:
    - filepath (str): 要上传的文件的绝对路径。
    - filename (str, optional): 上传时使用的文件名。如果此参数为空，将使用filepath中的文件名。

    返回:
    - tuple: (media_id, type)
      - media_id (str): 微信返回的媒体文件ID。
      - type (str): 媒体文件的类型，可以是'image', 'voice', 'video', 或 'file'。

    抛出:
    - ValueError: 如果文件大小不符合微信的要求或其他上传错误。

    注意:
    - 文件大小必须大于5字节。
    - 图片大小不能超过2MB，只支持JPG和PNG格式。
    - 语音大小不能超过2MB，播放长度不能超过60秒，只支持AMR格式。
    - 视频大小不能超过10MB，只支持MP4格式。
    - 普通文件大小不能超过20MB。
    """
    access_token = get_access_token()
    # API endpoint
    url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}"
    # 确定文件名
    if not filename:
        filename = os.path.basename(filepath)
    
    # 检查文件大小并确定类型
    file_size = os.path.getsize(filepath)
    mime_type, encoding = guess_type(filepath)
    media_type = guess_media_type(mime_type)

    if media_type == 'image' and (file_size > 2*1024*1024 or mime_type not in ['image/jpeg', 'image/png']):
        raise ValueError("图片大小超过2MB或格式不支持")
    elif media_type == 'voice' and (file_size > 2*1024*1024 or mime_type != 'audio/amr'):
        raise ValueError("语音大小超过2MB或格式不支持")
    elif media_type == 'video' and (file_size > 10*1024*1024 or mime_type != 'video/mp4'):
        raise ValueError("视频大小超过10MB或格式不支持")
    elif media_type == 'file' and file_size > 20*1024*1024:
        raise ValueError("文件大小超过20MB")
    elif file_size < 5:
        raise ValueError("文件大小必须大于5字节")

    # 上传文件
    data = {
        'type': media_type
    }
    files = {'media': (filename, open(filepath, 'rb'), mime_type)}

    response = requests.post(url, data=data, files=files)
    response_data = response.json()

    # 检查返回数据
    if 'media_id' in response_data and 'type' in response_data:
        return response_data['media_id'], response_data['type']
    else:
        raise ValueError(f"上传失败: {response_data.get('errmsg')}")
