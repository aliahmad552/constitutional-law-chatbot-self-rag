from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.helper import rag_app
app = FastAPI()

@app.get('/helo')
def hello():
    return {'messages':'hello from backend'}

@app.websocket('/ws/chat')
async def websocket_chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            user_msg = await ws.receive_text()
            if user_msg == "__STOP__":
                continue

            initial_state = {"question": user_msg}

            async for event in rag_app.astream(
                initial_state,
                config={"recursion_limit": 50}
            ):

                print("EVENT:", event)  # debug first

                if isinstance(event, dict):
                    for key, value in event.items():
                        if isinstance(value, dict) and "answer" in value:
                            await ws.send_text(value["answer"])
                

            await ws.send_text("__END__")

    except WebSocketDisconnect:
        print("Client Disconnected")


        