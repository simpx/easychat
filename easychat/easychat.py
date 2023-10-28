import json
import logging
import re
import yaml
from flask import Flask, request, jsonify
from typing import Callable, List
from .wework import get_messages, send_text, load_config, send_menu, decrypt_msg

class Session:
    def __init__(self, user_id, bot_id, chat):
        self.user_id = user_id
        self.bot_id = bot_id
        self.messages = []
        self.chat = chat

    def send_message(self, message, skip_histroy=False):
        if not skip_histroy:
            self.messages.append({"role": "assistant", "id": self.bot_id, "content": message})
        return send_text(self.user_id, self.bot_id, message)

    def send_menu(self, menu_list=None):
        return send_menu(self.user_id, self.bot_id, menu_list)

    def destroy(self):
        del self.chat.sessions[(self.user_id, self.bot_id)]

class Bot:
    def __init__(self, name):
        self.name = name
        self.bot_callbacks = []
        self.command_callbacks = []
    def on_chat(self, bot_ids: List[str] = [".*"]):
        def decorator(callback: Callable):
            self.bot_callbacks.append((bot_ids, callback))
            return callback
        return decorator
    def on_command(self, bot_ids: List[str] = [".*"]):
        def decorator(callback: Callable):
            self.command_callbacks.append((bot_ids, callback))
            return callback
        return decorator

class EasyChat:
    def __init__(self, url, cursor = None):
        self.app = Flask("easychat")
        self.sessions = {}
        self.chat_callbacks = []
        self.command_callbacks = []
        self.event_callbacks = []
        self.url = url
        self.cursor = cursor if cursor else open("cursor", "r").read().strip()
        open("cursor", "w+").write(self.cursor)
        self.config = None
        self._setup_routes()

    def load_config(self, config):
        self.config = config
        load_config(config)

    def _setup_routes(self):
        @self.app.route(self.url, methods=["POST"])
        def chat_route():
            return self._handle_chat()

    def serve(self, bot):
        self.chat_callbacks.extend(bot.bot_callbacks)
        self.command_callbacks.extend(bot.command_callbacks)

    def on_chat(self, bot_ids: List[str] = [".*"]):
        def decorator(callback: Callable):
            self.chat_callbacks.append((bot_ids, callback))
            return callback
        return decorator

    def on_command(self, bot_ids: List[str] = [".*"]):
        def decorator(callback: Callable):
            self.command_callbacks.append((bot_ids, callback))
            return callback
        return decorator

    def run(self, host="127.0.0.1", port=5000):
        self.app.run(host=host, port=port)

    def _get_callback(self, bot_id, type_):
        if type_ == "chat":
            callback_list = self.chat_callbacks
        elif type_ == "command":
            callback_list = self.command_callbacks

        for ids, callback in callback_list:
            for id_pattern in ids:
                logging.info(f"id_pattern {id_pattern}, bot_id {bot_id}")
                if re.match(id_pattern, bot_id) or id_pattern == "*":
                    return callback
        return None

    def _handle_chat(self):
        sReqMsgSig = request.args.get('msg_signature')
        sReqTimeStamp = request.args.get('timestamp')
        sReqNonce = request.args.get('nonce')
        sReqData = request.data
        ret, req = decrypt_msg(sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
        if ret != 0:
            logging.error(f"Failed in DecryptMsg, error code: {ret}")
            return "ERROR", 403
        messages = get_messages(req['Token'], cursor = self.cursor)
        self.cursor = messages['next_cursor']
        open("cursor", "w+").write(self.cursor)
        logging.info(f"cursor is: {self.cursor}")
        for message in messages['msg_list']:
            message_str = json.dumps(message, indent=4)
            logging.info(f"processing message : {message_str}")
            user_id = message['external_userid']
            user_msg = message['text']['content']
            bot_id = message['open_kfid']
            if (user_id, bot_id) not in self.sessions:
                self.sessions[(user_id, bot_id)] = Session(user_id, bot_id, self)
                logging.info(f"new session: ({user_id}, {bot_id})")
            if message['msgtype'] == 'text':
                if "menu_id" in message['text']:
                    type_ = 'command'
                    r = {"type": type_, "user_id": user_id, "bot_id": bot_id, "command": message['text']['menu_id'], "content": user_msg}
                else:
                    type_ = 'chat'
                    self.sessions[(user_id, bot_id)].messages.append({"role": "user", "id": user_id, "content": user_msg})
                    r = {"type": type_, "user_id": user_id, "bot_id": bot_id, "content": user_msg}
            else:
                logging.info(f"Skip message")
                continue
            try:
                callback = self._get_callback(bot_id, type_)
                if not callback:
                    return "ERROR", 500
                response = callback(r, self.sessions[(user_id, bot_id)])
                if isinstance(response, str):
                    self.sessions[(user_id, bot_id)].send_message(response)
                logging.info(f"Success in : {message_str}")
            except Exception as e:
                message_str = json.dumps(message, indent=4)
                send_text(message['external_userid'], message['open_kfid'], "出错了，请重新提问")
                logging.exception(f"Failed in send_text: {message_str}")
        return ""
