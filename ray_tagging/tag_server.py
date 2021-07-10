import asyncio
import websockets
import tagging
import queue
import _thread

taskQueue = queue.Queue()
sendQueue = queue.Queue()

#处理服务器发起的命令
def cmd_handler():

    cmd_text = str()
    if not taskQueue.empty():
        cmd_text = taskQueue.get()
    else:
        return

    result = ()

    #接收标签返回值
    tag_recv = ""

# try:
    cmd_dict = eval(cmd_text)


    if cmd_dict["type"] == "create":
        tag_recv = tagging.tagging(cmd_dict["path1"])
        result = ("create", tag_recv)

    elif cmd_dict["type"] == "move":
        result = ("move", cmd_dict["path1"] ,cmd_dict["path2"])

    elif cmd_dict["type"] == "delete":
        result = ("delete", cmd_dict["path1"])

    else:
        result = ("invalid",)

# except:
#     result = ("error",)

    #return str(result)
    sendQueue.put(str(result))


async def login():
    wsClient = await websockets.connect('ws://47.119.121.73:9090')
    #发送服务器姓名
    await wsClient.send("PYT_tag")
    print("Connected")
    return wsClient

# 向服务器端发送认证后的消息
async def recv_msg(websocket):
    while True:
        #接收命令
        recv_text = await websocket.recv()
        print(recv_text)
        taskQueue.put(recv_text)

        _thread.start_new_thread(cmd_handler, ())
        #result = cmd_handler(recv_text)

# 发送处理过后的消息
async def send_msg(websocket):
    while True:
        while sendQueue.empty():
            await asyncio.sleep(0.1)
        result = sendQueue.get()
        print("sending: ", result)
        await websocket.send(result)

# 客户端主逻辑
def main_logic():
    loop = asyncio.get_event_loop()
    websocket = loop.run_until_complete(login())
    loop.run_until_complete(asyncio.wait([recv_msg(websocket), send_msg(websocket)]))

#asyncio.get_event_loop().run_until_complete(main_logic())
if __name__ == "__main__":
    main_logic()
