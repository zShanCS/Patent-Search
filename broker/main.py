import asyncio
from datetime import datetime
import json
from math import ceil
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import os
import uvicorn

app = FastAPI()


if not os.path.exists('readme.txt'):
    dbdata = {'searches':[]}
    with open('db.json', 'w+') as f:
        json.dump(dbdata,f)

OWN_STATUS = "B"
PATIENCE = 3



class ConnectionManager:
    def __init__(self):
        self.all_active_resources: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.all_active_resources.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.all_active_resources.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.all_active_resources:
            await connection.send_text(message)


manager = ConnectionManager() 
   
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Patent Search</title>
    </head>
    <body>
        <h1>Broker's View of System</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                fetch('/search/'+input.value).then(r=>{
                    console.log(r)
                    return r.json()
                }).then(k=>{
                    console.log(k)
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(JSON.stringify(k))
                    message.appendChild(content)
                    messages.appendChild(message)
                })
                input.value = ''
                event.preventDefault()
            }
            ws.addEventListener('close',(e)=>{
                alert('connection lost. Please refresh')
            })
        </script>
    </body>
</html>
"""





@app.get("/")
async def get():
    return HTMLResponse(html)

@app.get('/search/')
async def search(q):
    query_id = str(datetime.now().microsecond)+str(datetime.now().microsecond)
    print(query_id)
    dbdata = None
    with open('db.json','r') as dbfile:
        dbdata = json.load(dbfile)
    
    print(dbdata)
    dbdata['searches'].append({'query_id':query_id,'query':q,'results':[]})
    with open('db.json', 'w') as dbfile:
        json.dump(dbdata,dbfile)
        
    send_data_to_resources = {
        'from':OWN_STATUS,
        'data':{
            'type':'USER_SEARCH',
            'search_id':query_id,
            'query':str(q),
            'limit':ceil(30/(len(manager.all_active_resources)+1))
        }
    }
    await manager.broadcast(json.dumps(send_data_to_resources))
    results = {'result':{}}
    # wait for 10 seconds for resources to reply
    await asyncio.sleep(PATIENCE)
    result_set = set()
    with open('db.json', 'r') as dbfile:
        dbdata = json.load(dbfile)
        for idx, search in enumerate(dbdata['searches']):
            cur_qid = dbdata['searches'][idx]['query_id']
            if dbdata['searches'][idx]['query_id'] == query_id:
                print('FOUNDDDD')
                for res in dbdata['searches'][idx]['results']:
                    for r in res['result']:
                        if r['docid'] in results['result'] and results["result"][r["docid"]]["score"] > r["score"]:
                            print(f'\n\n{r["docid"]} already in result with score {results["result"][r["docid"]]["score"]} compared to {r["score"]}')
                        else:
                            results['result'][r['docid']] = r
        
    print(results)
    vals = list(results['result'].values())
    return sorted(vals, key=lambda x:x['score'], reverse=True)

@app.websocket("/ws/{resource_id}")
async def websocket_endpoint(websocket: WebSocket, resource_id: int):
    await manager.connect(websocket)
    join_data = {'from':OWN_STATUS, 'data':{'type':'RESOURCE_JOINED', 'resource_id':resource_id}}
    print(join_data)
    await manager.broadcast(json.dumps(join_data))
    try:
        while True:
            data = await websocket.receive_text()
            print('recieved',data)
            send_data = {
                'from':resource_id,
                'data':{
                    'type':'RESOURCE_MESSAGE',
                    'message':data
                }
            }
            # await manager.send_personal_message(json.dumps(send_data), websocket)
            await manager.broadcast(json.dumps(send_data))

            resource_data = json.loads(data)
            print(resource_data)

            if resource_data['from'] == 'R':
                if resource_data['data']['type'] == 'QUERY_RESULT':
                    qid = resource_data['data']['query_id']
                    res = resource_data['data']['result']
                    dbdata = None
                    with open('db.json', 'r') as dbfile:
                        dbdata = json.load(dbfile)
                        for idx, search in enumerate(dbdata['searches']):
                            cur_qid = dbdata['searches'][idx]['query_id']
                            print(f'Searching {idx}: for [{qid},{cur_qid}]: ',dbdata['searches'][idx])
                            print(dbdata['searches'][idx]['query_id'], qid, dbdata['searches'][idx]['query_id'] == qid, cur_qid==qid)
                            if dbdata['searches'][idx]['query_id'] == qid:
                                print('query found, appending results',res)
                                dbdata['searches'][idx]['results'].append({
                                    'resource_id':resource_id,
                                    'result':res
                                })
                    print('after wriitng result', dbdata)
                    with open('db.json', 'w') as dbfile:
                        json.dump(dbdata, dbfile)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({'from':OWN_STATUS, 'data':{'type':'RESOURCE_LEFT', 'resource_id':resource_id}}))


if __name__ == '__main__':
    uvicorn.run(app=app, host="127.0.0.1", port=8000, log_level="info")