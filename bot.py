from easy_bot import EasyBot, Session
import json

app = EasyBot("/verify_url", "HHFq49uYHoiCuZRv9MtM")

@app.on_chat([".*"])
def handle_chat(request, session: Session):
    r_str = json.dumps(request, indent=4)
    print(f"request: {r_str}")

    session.send_message(request["content"])
    return "Goodbye and take care!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8899)
