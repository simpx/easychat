import requests
from datetime import datetime, timedelta

# 全局变量存储缓存的access_token和过期时间
access_token_cache = None
token_expire_time = None

def get_access_token(corpid, secret, force_renew=False):
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

# 示例用法
# token = get_access_token(YOUR_CORPID, YOUR_SECRET)
