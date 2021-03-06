from __future__ import absolute_import
import asyncio
from datetime import datetime

from random import randint, random
import websockets
import json


from Patent_Search_DC import main as patent_main

print(patent_main.get_rankings)

OWN_STATUS = 'R'
BROKER = '127.0.0.1:8000'
OWN_ID = str(datetime.now().microsecond)+str(datetime.now().microsecond)

def generate_results(query, k):
    r = patent_main.get_rankings(query,k)
    print(r)
    return r

async def receiver_messages():
    global BROKER
    uri = f"ws://{BROKER}/ws/{OWN_ID}"
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                broker_message = await websocket.recv()
                broker_message = json.loads(broker_message)
                print(broker_message)
                if broker_message['from'] == 'B':
                    if broker_message['data']['type'] == 'USER_SEARCH':
                        q = broker_message['data']['query']
                        limit = broker_message['data']['limit']
                        query_id = broker_message['data']['search_id']
                        result = generate_results(q,limit)
                        send_response = {
                            'from': OWN_STATUS,
                            'resource_id':OWN_ID,
                            'data':{
                                'type':'QUERY_RESULT',
                                'query_id':query_id,
                                'result':result
                            }
                        }
                        await websocket.send(json.dumps(send_response))
    except websockets.exceptions.ConnectionClosedError as conclose:
        print('Connection To Broker Lost Abnormally.')
        print(conclose)
        BROKER = input(f'Try Connextion Again? Enter Brokers Address. (or "." for default {BROKER}) Enter "n" or "N" To Cancel.')
        if BROKER.lower() == 'n':
            print('Exiting...')
        else:
            if BROKER == '.':
                BROKER = '127.0.0.1:8000'
            await receiver_messages()
    except Exception as conclose:
        print('Something Went wrong. Details:', str(conclose))
        BROKER = input(f'Try Connextion Again? Enter Brokers Address. (or "." for default {BROKER}) Enter "n" or "N" To Cancel.')
        if BROKER.lower() == 'n':
            print('Exiting...')
        else:
            if BROKER == '.':
                BROKER = '127.0.0.1:8000'
            await receiver_messages()


if __name__ == "__main__":
    asyncio.run(receiver_messages())