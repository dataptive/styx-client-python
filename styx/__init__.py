"""
"""
from urllib.parse import urlencode
import aiohttp
import websockets

DEFAULT_CHUNK_SIZE = 1 << 20


class ClientError(Exception):

    def __init__(self, body, status_code=None):
        super().__init__(body['message'])

        self.status_code = status_code
        self.code = body['code']


class Producer:
    """
    """

    def __init__(self, host='localhost:7123'):
        self.host = host

    async def connect(self, name, **kwargs):
        url = f'ws://{self.host}/logs/{name}/records'
        headers = {
            'X-HTTP-Method-Override': 'POST'
        }
        self.websocket = await websockets.connect(url, extra_headers=headers)

    async def write(self, record):
        await self.websocket.send(record)

    async def flush(self):
        pass

    async def close(self):
        pass


class Consumer:
    """
    """

    def __init__(self, host='localhost:7123'):
        self.host = host

    async def connect(self, name, whence='end', position=0, count=-1, follow=True):
        params = {
            'whence': whence,
            'position': position,
            'count': count,
            'follow': 'true' if follow else 'false'
        }
        url = f'ws://{self.host}/logs/{name}/records?{urlencode(params)}'
        self.websocket = await websockets.connect(url)

    async def read(self):
        try:
            record = await self.websocket.recv()
        except websockets.exceptions.ConnectionClosedOK:
            return None

        return record

    async def close(self):
        pass

    def __aiter__(self):
        return self

    async def __anext__(self):
        record = await self.read()
        if record is None:
            raise StopAsyncIteration

        return record


class Client:
    """
    """

    def __init__(self, host='localhost:7123'):
        self.host = host

    async def list_logs(self):
        async with aiohttp.ClientSession() as session:
            response = await session.get(f'http://{self.host}/logs')
            if response.status != 200:
                error = await response.json()
                raise ClientError(error, status_code=response.status)
            return await response.json()

    async def get_log(self, name):
        async with aiohttp.ClientSession() as session:
            response = await session.get(f'http://{self.host}/logs/{name}')
            if response.status != 200:
                error = await response.json()
                raise ClientError(error, status_code=response.status)
            return await response.json()

    async def create_log(self, name, config={}):
        data = {
            'name': name
        }
        data.update(config)
        async with aiohttp.ClientSession() as session:
            response = await session.post(f'http://{self.host}/logs', data=data)
            if response.status != 200:
                error = await response.json()
                raise ClientError(error, status_code=response.status)
            return await response.json()

    async def delete_log(self, name):
        async with aiohttp.ClientSession() as session:
            response = await session.delete(f'http://{self.host}/logs/{name}')
            if response.status != 200:
                error = await response.json()
                raise ClientError(error, status_code=response.status)
            return

    async def truncate_log(self, name):
        async with aiohttp.ClientSession() as session:
            response = await session.post(f'http://{self.host}/logs/{name}/truncate')
            if response.status != 200:
                error = await response.json()
                raise ClientError(error, status_code=response.status)
            return

    async def backup_log(self, name, file, chunk_size=DEFAULT_CHUNK_SIZE):
        async with aiohttp.ClientSession() as session:
            response = await session.get(f'http://{self.host}/logs/{name}/backup')
            if response.status != 200:
                error = await response.json()
                raise ClientError(error, status_code=response.status)
            while True:
                chunk = await response.content.read(DEFAULT_CHUNK_SIZE)
                if not chunk:
                    break
                file.write(chunk)
            return

    async def restore_log(self, name, file, chunk_size=DEFAULT_CHUNK_SIZE):
        async with aiohttp.ClientSession() as session:
            response = await session.post(f'http://{self.host}/logs/restore?name={name}', data=file)
            if response.status != 200:
                error = await response.json()
                raise ClientError(error, status_code=response.status)
            return

    async def create_producer(self, name, **kwargs):
        producer = Producer(host=self.host)
        await producer.connect(name, **kwargs)
        return producer

    async def create_consumer(self, name, **kwargs):
        consumer = Consumer(host=self.host)
        await consumer.connect(name, **kwargs)
        return consumer

    async def produce(self, name, record):
        async with aiohttp.ClientSession() as session:
            response = await session.post(f'http://{self.host}/logs/{name}/records', data=record)
            if response.status != 200:
                error = await response.json()
                raise ClientError(error, status_code=response.status)
            return await response.json()

    async def consume(self, name, whence='end', position=-1):
        params = {
            'whence': whence,
            'position': position,
        }
        async with aiohttp.ClientSession() as session:
            response = await session.get(f'http://{self.host}/logs/{name}/records', params=params)
            if response.status != 200:
                error = await response.json()
                raise ClientError(error, status_code=response.status)
            return await response.read()
