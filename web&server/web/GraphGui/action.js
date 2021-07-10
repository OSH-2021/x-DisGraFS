    var FS_username = window.location.href.split("username=")[1];
    var FS_postion = window.location.href.split("pos=")[1].split("&")[0];

    var A_label = document.getElementById("OpenClient") 
    A_label.setAttribute("href","disgrafs://redis://:disgrafs@juicefs.disgrafs.tech "+decodeURIComponent(FS_postion)+" ws://47.119.121.73:9090 "+decodeURIComponent(FS_username)+"_client");

    function MsgInitial(obj, doc_msg){
        doc_msg.setAttribute("MsgInitial","old");

        var Title = document.createElement("h2");
        Title.innerText = "DisGraFS文件操作";

        var FileName = document.createElement("h4");
        FileName.innerText = obj.children[0].children[1].innerHTML;

        //设置按钮的属性
        var DivStyle = "background-color: #22252a;border: none;color: white;padding: 15px 32px;text-align: center;text-decoration: none;\
        display: inline-block;font-size: 16px;margin: 4px 2px;cursor: pointer;margin:40 auto;width:150px;";

        // var FunctForm = document.createElement("form");
        // FunctForm.setAttribute("action","html2py.php");
        // FunctForm.setAttribute("method","post");      

        var Download = document.createElement("div");
        Download.innerText = "打开文件";
        Download.setAttribute("style",DivStyle);
        
        if(decodeURIComponent(FS_postion)===""){
            Download.setAttribute("title","当前未选择挂载路径");
            Download.setAttribute("disabled","disabled");
        }
        else{
            Download.setAttribute("onclick","OpenAction(this);");
        }

        var Delete = document.createElement("div");
        Delete.innerText = "删除文件";
        Delete.setAttribute("style",DivStyle);
        Delete.setAttribute("onclick","DeleteAction(this);");

        // Delete.setAttribute("name","funct");
        // Delete.setAttribute("type","submit");
        // Delete.setAttribute("value","Delete");

        var Cancel = document.createElement("div");
        Cancel.innerText = "取消";       
        Cancel.setAttribute("style",DivStyle);
        Cancel.setAttribute("onclick","CancelAction(this);");
        
        
        doc_msg.appendChild(Title);
        doc_msg.appendChild(FileName);
        doc_msg.appendChild(Download);
        doc_msg.appendChild(Delete);
        doc_msg.appendChild(Cancel);
        // doc_msg.appendChild(FunctForm);   
}
    
    // 点击打开响应函数
    function OpenAction(obj){
        ws.send("{'command': 'open', 'parameter': ['"+ obj.parentNode.children[1].innerText +"']}");
    }
    
    // 点击取消响应函数
    function CancelAction(obj){
        obj.parentNode.style.display = "none";
    }
    
    // 点击删除响应函数
    function DeleteAction(obj){
        ws.send("{'command': 'delete', 'parameter': ['"+ obj.parentNode.children[1].innerText +"']}");
        alert("删除成功");
    }

    function FileMenuGet(obj){
        var obj_id = obj.id;
        var msg_id = "msg_"+ obj.id;//我们将每一个元素对应的消息框的id设置为msg_popoto-result-x，其中x是变量。
        var doc_msg = document.getElementById(msg_id);
        
        var e = event || window.event;
        doc_msg.style.left= e.clientX + "px";
        doc_msg.style.top = e.clientY + "px";
        
        if(doc_msg.style.display == "block")
            doc_msg.style.display = "none";
        else
            doc_msg.style.display = "block";

        
        if(doc_msg.getAttribute("MsgInitial") == "new")
            MsgInitial(obj, doc_msg);
    }