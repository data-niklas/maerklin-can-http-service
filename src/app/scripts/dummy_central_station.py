import asyncio

IP = "127.0.0.1"
PORT = 15731

writers = set()
queue = asyncio.Queue()

async def handle_client(reader, writer):
    writers.add(writer)
    async def client_loop(reader, writer):
        while True:
            data = await reader.read(13)
            if len(data) == 0:
                # connection was closed
                return
            queue.put_nowait(data)
    try:
        await client_loop(reader, writer)
    finally:
        writers.remove(writer)

async def run_server():
    server = await asyncio.start_server(handle_client, IP, PORT)
    async with server:
        await server.serve_forever()

async def run_broadcaster():
    while True:
        data = await queue.get()
        for writer in writers:
            try:
                writer.write(data)
            except:
                pass
        queue.task_done()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_broadcaster())
    loop.create_task(run_server())
    loop.run_forever()