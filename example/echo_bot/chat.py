from easychat import EasyChat, Session
import json
import logging
logging.basicConfig(level=logging.DEBUG)

app = EasyChat("/verify_url", "HHFq49uYHoiCuZRv9MtM")
app.load_config("config.yaml")

@app.on_chat([".*"])
def handle_chat(request, session: Session):
    r_str = json.dumps(request, indent=4)
    print(f"request: {r_str}")

    session.send_message(request["content"])
    return "Goodbye and take care!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8899)
