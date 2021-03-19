# styx-client-python

## Installing

```bash
$ git clone https://github.com/dataptive/styx-client-python.git
$ cd styx-client-python
$ python3 setup.py install
```

## Usage

Example producer

```python
import asyncio
from styx import Client

async def main():
	client = Client('localhost:7123')

	producer = await client.create_producer('test')
	for i in range(1000):
		await producer.write('Hello, Styx!')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

Example consumer

```python
import asyncio
from styx import Client

async def main():
    client = Client('localhost:7123')

    # whence can be 'start', 'end' or 'origin' and defines the basis for `position`
    # position can be negative when using whence='end'
    # follow determines if the consumer will wait for incoming records when it has reached the end of log
    consumer = await client.create_consumer('test', whence='start', position=0, follow=True)
    async for record in consumer:
        print(record)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

Managing logs

```python
import asyncio
from styx import Client

async def main():
    client = Client('localhost:7123')

    # Create a log
	result = await client.create_log('test')

	# List all logs
	result = await client.list_logs()

	# Fetch info for a particular log
	result = await client.get_log('test')

	# Delete a log
	result = await client.delete_log('test')

	# Truncate a log
	result = await client.truncate_log('test')

	# Backup a log
	with open('test.tar.gz', 'wb') as f:
		await client.backup_log('test', f)

	# Restore a log from backup
	with open('test.tar.gz', 'rb') as f:
		await client.restore_log('test-restore', f)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```
