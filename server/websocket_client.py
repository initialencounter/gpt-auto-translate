import asyncio
import websockets

class Client:
    def __init__(self, uri):
        self.websocket = None
        self.uri = uri

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)

    async def send(self, message):
        if self.websocket is not None:
            await self.websocket.send(message)

    async def receive(self):
        if self.websocket is not None:
            while True:
                response = await self.websocket.recv()
                print(response)
                if response == "QUIT":  # 如果收到 "QUIT" 消息，则停止接收
                    break

    async def disconnect(self):
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None


async def main():
    client = Client("ws://121.37.247.122:8080")  # 请替换成你的WebSocket服务器的URL
    await client.connect()
    await client.send("Hello World")  # 发送数据
    await client.receive()  # 接收数据
    await client.disconnect()

asyncio.run(main())
