    var a;

    document.onmouseup=function(){
        if(!a)
            return;
        document.all?a.releaseCapture():window.captureEvents(Event.MOUSEMOVE|Event.MOUSEUP);
        a="";
    };
    
    document.onmousemove=function (d){
            if(!a) return;
            if(!d) d=event;
            a.style.left=(d.clientX-b)+"px";a.style.top=(d.clientY-c)+"px";
    };

    function Msg_Move(o,e){
        a=o;
        document.all?a.setCapture():window.captureEvents(Event.MOUSEMOVE);
        b=e.clientX-parseInt(a.style.left);
        c=e.clientY-parseInt(a.style.top);
        o.style.zIndex=parseInt(getMaxIndex())+1;
    }
        
    function $(id){return document.getElementById(id);}
        
    function getMaxIndex(){
        var index=0;
        var ds=$('main').getElementsByTagName('div');
        var l=$('main').getElementsByTagName('div').length;

        for (i=0;i<l;i++)
        {
        if (ds[i].style.zIndex>index) index=ds[i].style.zIndex;
        }
        return index;
    }
