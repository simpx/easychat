import re
from typing import Callable, List
from flask import Flask, request, jsonify

class Session:
    def __init__(self, user_id):
        self.user_id = user_id
        self.chat = []

    def send_message(self, message):
        # 这里只会更新session记录，并没有真正的发送机制，实际上可能需要接入微信API进行消息发送。
        self.chat.append({"bot": "SYSTEM", "message": message})

class EasyWeWork:
    def __init__(self):
        self.app = Flask("easy_wework")
        self.sessions = {}
        self.chat_callbacks = []
        self.event_callbacks = []
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/chat", methods=["POST"])
        def chat_route():
            return self._handle_chat()

        @self.app.route("/event", methods=["POST"])
        def event_route():
            return self._handle_event()

    def on_chat(self, bot_ids: List[str]):
        def decorator(callback: Callable):
            self.chat_callbacks.append((bot_ids, callback))
            return callback
        return decorator

    def on_event(self, bot_ids: List[str]):
        def decorator(callback: Callable):
            self.event_callbacks.append((bot_ids, callback))
            return callback
        return decorator

    def run(self, host="127.0.0.1", port=5000):
        self.app.run(host=host, port=port)

    def _get_callback(self, bot_id, callback_list):
        for ids, callback in callback_list:
            for id_pattern in ids:
                if re.match(id_pattern, bot_id) or id_pattern == "*":
                    return callback
        return None

    def _handle_chat(self):
        user_id = request.json["user_id"]
        message = request.json["message"]
        bot_id = request.json["bot_id"]

        if user_id not in self.sessions:
            self.sessions[user_id] = Session(user_id)

        self.sessions[user_id].chat.append({"user": user_id, "message": message})

        callback = self._get_callback(bot_id, self.chat_callbacks)
        if not callback:
            return jsonify({"error": "No callback registered for this bot_id."})

        response = callback(request, self.sessions[user_id])
        if isinstance(response, str):
            self.sessions[user_id].chat.append({"bot": bot_id, "message": response})
            return jsonify({"bot": bot_id, "message": response})

    def _handle_event(self):
        event_type = request.json["type"]
        user_id = request.json["user_id"]
        bot_id = request.json["bot_id"]

        if user_id not in self.sessions:
            self.sessions[user_id] = Session(user_id)

        callback = self._get_callback(bot_id, self.event_callbacks)
        if not callback:
            return jsonify({"error": "No callback registered for this bot_id."})

        callback(request, self.sessions[user_id])
        return jsonify({"status": "OK"})

