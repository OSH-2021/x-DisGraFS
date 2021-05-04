# just for testing - prints what's received and
# tells the client to open the file just changed

import asyncio
import websockets

# 检测客户端权限，用户名密码通过才能退出循环
async def check_permit(websocket):
    while True:
        print("waiting for auth")
        recv_str = await websocket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "123456":
            response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
            print(response_str)
            await websocket.send(response_str)
            return True
        else:
            response_str = "sorry, the username or password is wrong, please submit again"
            await websocket.send(response_str)

# 接收客户端消息并处理，这里只是简单把客户端发来的返回回去
async def recv_msg(websocket):
    while True:
        print("awaiting recv...")
        recv_text = await websocket.recv()
        print("received: " + recv_text)
        recv_dict = eval(recv_text)

        target = ""
        if recv_dict["type"] == "modify":
            target = recv_dict["path1"]
        elif recv_dict["type"] == "move":
            target = recv_dict["path2"]

        if target != "":
            response_dict = {}
            if "exit" in target:
                response_dict = {"command": "exit", "parameter": []}
            else:
                response_dict = {"command": "open", "parameter": [target]}
            print("response: ", repr(response_dict))
            await websocket.send(repr(response_dict))

# 服务器端主逻辑
# websocket和path是该函数被回调时自动传过来的，不需要自己传
async def main_logic(websocket, path):
    print("before check permit")
    await check_permit(websocket)

    await recv_msg(websocket)

# 把ip换成自己本地的ip
start_server = websockets.serve(main_logic, "0.0.0.0", 9090)
# 如果要给被回调的main_logic传递自定义参数，可使用以下形式
# 一、修改回调形式
# import functools
# start_server = websockets.serve(functools.partial(main_logic, other_param="test_value"), '10.10.6.91', 5678)
# 修改被回调函数定义，增加相应参数
# async def main_logic(websocket, path, other_param)

print("before run")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
