import asyncio
import websockets

async def test():
    uri = "ws://localhost:8000/ws/chat"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Power of President to promulgate Ordinances Constitution of Pakistan from the source given")
        
        while True:
            response = await websocket.recv()
            print("Received:", response)
            
            if response == "__END__":
                break

asyncio.run(test())