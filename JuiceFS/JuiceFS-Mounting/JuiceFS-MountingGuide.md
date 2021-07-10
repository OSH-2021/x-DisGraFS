# JuiceFS客户端挂载指南

## Windows

由于Windows不自带FUSE，需要先手动安装`winfsp`。

在cmd中运行Windows版的`juicefs.exe`

```
juicefs mount redis://:disgrafs@juicefs.disgrafs.tech Z: -v --writeback
```

其中`@`前的`disgrafs`是redis密码，@后是redis服务器域名，`Z:`表示挂载到Z盘，`-v`表示显示调试信息，`--writeback`开启针对小文件上传的写回优化。Windows下必须挂载到某个空闲的盘符，不能指定任意文件夹。

在cmd中按下`Ctrl + C`结束程序，即可自动卸载。

## Linux

大部分Linux自带FUSE，但如果没有，需要先手动安装。

在bash中运行Linux版的`juicefs`

```
./juicefs mount redis://:disgrafs@juicefs.disgrafs.tech ~/jfs -v --writeback
```

Linux下可以挂载到任意文件夹，但如果挂载的文件夹需要sudo权限，那么也要用sudo运行`juicefs`。同样按下`Ctrl + C`结束程序即可自动卸载。

**注意！**直接从网络上下载的`juicefs`可执行文件在一些Linux系统上由于不受信而无法执行，这时需要先执行`chmod 777 juicefs`。

## MacOS

黑苹果还没装好，抱歉。

目前已知需要先安装[macFUSE](https://osxfuse.github.io/)

