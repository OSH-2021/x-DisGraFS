        var FS_username = window.location.href.split("username=")[1];
        
        window.onbeforeunload = ExitClient;
        window.onunload = ExitClient;
        
        if(decodeURIComponent(FS_username) === ""){
            alert("当前未输入用户名！可能会出现未知错误！建议重新来过！");
            window.location.href = "../";
        }
    
        if("WebSocket" in window){
        　　　　console.log("您的浏览器支持WebSocket");
                ws = new WebSocket("ws://47.119.121.73:9090"); //创建WebSocket连接
        　　　　//...
                ws.onopen = function(){
                　　//当WebSocket创建成功时，触发onopen事件
                  console.log("open");
                  ws.send(decodeURIComponent(FS_username) + "_web");
                };
                
                ws.onerror = function(){
                    console.log("error");
                    alert("连接服务器失败！");
                    document.getElementById("BEGIN").setAttribute("disabled","disabled");
                }
        　　}else{
        　　　　alert("您的浏览器不支持WebSocket，请更换浏览器");
        　　　　window.close();
        }
        
        function ExitClient(){
            ws.send("{'command': 'exit', 'parameter': []}");
        }
        