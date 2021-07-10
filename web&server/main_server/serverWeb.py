import asyncio
import websockets
import pytoneo
import time

class client_struct:
    username            = 0
    index_client        = 0
    web_websocket       = 0
    client_websocket    = 0

#用户数组和用户人数
client_array = []
client_num = 0

#标签服务器数组
tag_array = []
tag_num = 0

Neo4jServer = 0

# 服务器端主逻辑
# websocket和path是该函数被回调时自动传过来的，不需要自己传
async def main_logic(websocket, path):
    #引用全局变量
    global tag_num
    global client_num
    global Neo4jServer
    
    try:
        #记录日志
        localtime = time.asctime( time.localtime(time.time()))
        print(localtime,":",end='')
        
        recv_text = await websocket.recv()
        
        print(recv_text)
        
        print("websocket: ",websocket.port)
        
        #主页面链接上时，返回确认信息
        if recv_text == "mainWeb":
            await websocket.send("Close:A Good Connection, please close it")
            await websocket.close_connection()
            return
        
        #分解接收到的信息
        tag_split = recv_text.split('_')
        print(tag_split)
        
        #网页端连接逻辑
        if tag_split[1] == "web":
            
            client_item = client_struct()
            client_item.username        = tag_split[0]
            client_item.web_websocket   = websocket
            
            client_array.append(client_item)
            
            client_index = client_num
            client_num = client_num + 1
            
            print(tag_split,"：",recv_text)
            
            while True:
                recv_text = await websocket.recv()
                print(tag_split,"：",recv_text)
                
                if client_array[client_index].index_client == 1: 
                    await client_array[client_index].client_websocket.send(recv_text)
                else:
                    await websocket.send("no_client")
        
        #客户端连接逻辑            
        elif tag_split[1] == "client":
            
            #更改信号量，添加用户端的通信地址
            client_index = -1
            for client_item in client_array:
                client_index = client_index + 1
                if client_item.username == tag_split[0]:
                    client_item.index_client    = 1 
                    client_item.client_websocket= websocket
                    break
            
            print(tag_split,"：",recv_text)
            
            while True:
                    recv_text = await websocket.recv()
                    print(tag_split,"：",recv_text)

                    if tag_num == 0:
                        print("no tag server")

                    else:
                        #选择一个tag服务器作为打标服务器，之后可改为随机取打标服务器
                        tag_index = 0
                        await tag_array[tag_index].send(recv_text)
                    
        #标签端连接逻辑
        elif tag_split[1] == "tag":
            
            tag_array.append(websocket)
            tag_num = tag_num + 1
            
            #debug
            tag_index = 0
            
            while True:
                recv_text = await websocket.recv()
                print(tag_split,"：",recv_text)
                
                recv_list = eval(recv_text)
                
                #尝试解码从tag服务器中读出的数据，然后进行增删改的操作，所有跟数据库交互的操作在这边完成
                if recv_list[0] == "create":
                    print("创建指令")
                    print(recv_list[1])
                    Neo4jServer.create_newnode(recv_list[1])
                    
                elif recv_list[0] == "move":
                    print("修改指令")
                    # print(recv_list[2])
                    # Neo4jServer.delete_node(recv_list[1])
                    # Neo4jServer.create_newnode(recv_list[2])
                    
                elif recv_list[0] == "delete":
                    print("正在删除")
                    print(recv_list[1])
                    Neo4jServer.delete_node(recv_list[1].lower())
                    
                elif recv_list[0] == "invalid":
                    print("无效，忽略此消息")
                    
                elif recv_list[0] == "error":
                    print("错误指令")
                    
                else:
                    print("标签服务器传输有误")
        
        #错误的连接信息        
        else:
            await websocket.send("A wrong user, please check your message.")
            await websocket.close_connection()
            return
    
    #当前的websocket连接断开        
    except websockets.ConnectionClosed:
        
        client_index = -1
        for client_item in client_array:
            client_index = client_index + 1
            #网页连接断开则弹出整个连接
            if client_item.web_websocket == websocket:
                #先退出客户端
                
                #再弹出整个连接
                client_array.pop(client_index)
                client_num = client_num - 1
                
                print(client_item.username," web exit")
                return
            #客户端连接断开则只删除客户端信息
            elif client_item.client_websocket == websocket:
                client_item.index_client    = 0
                client_item.client_websocket= 0
                
                print(client_item.username," client exit")
                return
            
        tag_index = -1
        for tag_item in tag_array:
            tag_index = tag_index + 1
            #弹出当前打标连接
            if tag_item == websocket:
                tag_array.pop(tag_index)
                tag_num = tag_num - 1
                
            print("打标服务器[",tag_index,"]已退出")
            return
        
        #未找到这个websocket    
        print("client didn't login")
        
        return
    
    # #其他的异常情况
    # except:
    #     print("错误的连接信息")

if __name__ == "__main__":
    #端口名、用户名、密码根据需要改动
    #create_newnode(node)用于创建结点（包括检测标签、创建标签节点、添加相应的边等功能）
    #delete_node(node.name)用于删去名为node.name的结点
    
    #连接数据库 
    scheme = "neo4j"  # Connecting to Aura, use the "neo4j+s" URI scheme
    host_name = "localhost"
    port = 7474
    url = "bolt://47.119.121.73:7687".format(scheme=scheme, host_name=host_name, port=port)
    user = "neo4j"
    password = "disgrafs"
    
    Neo4jServer = pytoneo.App(url, user, password)
    print("Neo4j服务器连接成功...")
    
    #启动webserver服务器
    start_server = websockets.serve(main_logic, '0.0.0.0', 9090)
    print("主服务器初始化成功，等待连接...")
    
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
