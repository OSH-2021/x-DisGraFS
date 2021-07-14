# Ceph-Docker 部署指南

USTC OSH-2021-x-DisGraFS小组 HurryPeng

本指南参考[https://blog.csdn.net/u014534808/article/details/109159160](https://blog.csdn.net/u014534808/article/details/109159160) ，部署了一个三节点的简单Ceph集群。相比原文，在功能上有所删减，但对于安装过程中可能出现的问题做了一些细节补充。阅读时，不妨将本问文为原文的一份“注”。在一些“你为什么不自己搜”的问题上，本指南尽量提供了有效的参考链接，以求对读者友好。

在阅读本文前，最好先对Ceph的整体架构、不同节点的角色等基本知识有所了解。参考：[https://www.jianshu.com/p/cc3ece850433](https://www.jianshu.com/p/cc3ece850433) （你为什么不自己搜）。

本指南编写动机来源于中国科学技术大学2021春季学期操作系统H课程Lab4。参考：[https://osh-2021.github.io/lab-4/index.html](https://osh-2021.github.io/lab-4/index.html) 。

## 说明

### 操作顺序

本指南的顺序和原文不同，先安装Docker和脚本。这是因为除了网络环境之外，每台节点上所需要的环境是几乎相同的。可以先在一台虚拟机上安装完，再使用虚拟机克隆功能，完成后再分别配置网络，这样就能避免重复操作。直到组网之前，所有内容均在一台虚拟机上操作即可。

但是，此处涉及到部分与主机名、IP相关的参数，需要预先设计好，如下介绍。

### 环境

三台VMWare Ubuntu虚拟机（ubuntu-20.04.2-live-server-amd64.iso），Docker version 20.10.2，通过VMWare的NAT组网。

| 主机名 | IP             | 功能               |
| ------ | -------------- | ------------------ |
| node0  | 192.168.92.200 | mon, osd, mgr, mds |
| node1  | 192.168.92.201 | mon, osd, mgr, mds |
| node2  | 192.168.92.202 | mon, osd, mgr, mds |

仅供规划，现在可以先不用组网，后续会介绍组网步骤。

## Docker环境配置

本节所有内容均在一台虚拟机上操作即可。

### 创建Ceph目录

在宿主机上创建Ceph目录与容器建立映射，便于直接操纵管理Ceph配置文件，依次在三台节点上创建/usr/local/ceph/{admin,data, etc,lib, logs}目录：

```
sudo mkdir -p /usr/local/ceph/{admin,data,etc,lib,logs}
```

### 安装Docker

更新apt列表并安装Docker。可以自行配置源加快下载速度，参考：[http://mirrors.ustc.edu.cn/help/ubuntu.html](http://mirrors.ustc.edu.cn/help/ubuntu.html)

```
sudo apt update
sudo apt install docker
sudo apt install docker.io
```

启动Docker：

```
sudo systemctl start docker
```

设置开机自启动：

```
sudo systemctl enable docker
```

配置Docker源。这一步非常重要，默认Docker源非常慢，即使挂了梯子也很容易下载失败，所以一定要配置加速源。通过修改daemon.json来配置：

```
sudo mkdir /etc/docker
sudo vim /etc/docker/daemon.json
```

在该文件中写入以下内容：

```
{
    "registry-mirrors": 
    [
        "https://hub-mirror.c.163.com",
        "https://mirror.baidubce.com"
    ]
}
```

但是实际测试发现，这两个源的速度也不是非常理想。使用阿里云的专用镜像加速源可以达到比较理想的速度。这是免费的，但是需要一个阿里云账号。参考：[https://developer.aliyun.com/article/29941](https://developer.aliyun.com/article/29941)

配置后，需要重启服务：

```
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl enable docker
```

## Ceph环境配置

本节所有内容均在一台虚拟机上操作即可。

### 拉取Ceph镜像

配置好Docker后，这一步应该执行得比较快。如果频频失败，大概率是网络问题，需要重新配置加速源。

```
docker pull ceph/daemon:latest-nautilus
```

### 编写启动脚本

以下的每一个脚本对应启动Ceph的一个进程。因为虚拟机后续会克隆，最后每台虚拟机都会拥有这些脚本，所以它们可以任意放在某个文件夹下，本次放在了`~/ceph/`下。

对于脚本的内容，不需要每项都了解，此处只介绍比较重要的内容，详细介绍请参考原文。

#### start_mon.sh

```
#!/bin/bash
docker run -d --net=host \
    --name=mon \
    -v /etc/localtime:/etc/localtime \
    -v /usr/local/ceph/etc:/etc/ceph \
    -v /usr/local/ceph/lib:/var/lib/ceph \
    -v /usr/local/ceph/logs:/var/log/ceph \
    -e MON_IP=192.168.92.200,192.168.92.201,192.168.92.202 \
    -e CEPH_PUBLIC_NETWORK=192.168.92.0/24 \
    ceph/daemon:latest-nautilus  mon

```

注意，原文中的这段脚本第一行缺了一个`#`。

这个脚本是为了启动监视器，监视器的作用是维护整个Ceph集群的全局状态。一个集群至少要有一个监视器，最好要有奇数个监视器。方便当一个监视器挂了之后可以选举出其他可用的监视器。

脚本中需要注意`MON_IP`一项，这一项指定了需要作为monitor的所有节点的IP。虽然我们现在还没有组网，但是也要先把规划的IP填上。这些IP要与下面`CEPH_PUBLIC_NETWORK`的网段一致。

#### start_osd.sh

```
#!/bin/bash
docker run -d \
    --name=osd \
    --net=host \
    --restart=always \
    --privileged=true \
    --pid=host \
    -v /etc/localtime:/etc/localtime \
    -v /usr/local/ceph/etc:/etc/ceph \
    -v /usr/local/ceph/lib:/var/lib/ceph \
    -v /usr/local/ceph/logs:/var/log/ceph \
    -v /usr/local/ceph/data/osd:/var/lib/ceph/osd \
    ceph/daemon:latest-nautilus  osd_directory  
```

#### start_mgr.sh

```
#!/bin/bash
docker run -d --net=host  \
  --name=mgr \
  -v /etc/localtime:/etc/localtime \
  -v /usr/local/ceph/etc:/etc/ceph \
  -v /usr/local/ceph/lib:/var/lib/ceph \
  -v /usr/local/ceph/logs:/var/log/ceph \
  ceph/daemon:latest-nautilus mgr
```

#### start_mds.sh

```
#!/bin/bash
docker run -d \
   --net=host \
   --name=mds \
   --privileged=true \
   -v /etc/localtime:/etc/localtime \
   -v /usr/local/ceph/etc:/etc/ceph \
   -v /usr/local/ceph/lib:/var/lib/ceph \
   -v /usr/local/ceph/logs:/var/log/ceph \
   -e CEPHFS_CREATE=0 \
   -e CEPHFS_METADATA_POOL_PG=512 \
   -e CEPHFS_DATA_POOL_PG=512 \
   ceph/daemon:latest-nautilus  mds
```

### 创建OSD磁盘

 OSD服务是对象存储守护进程，负责把对象存储到本地文件系统，必须要有一块独立的磁盘作为存储。考虑到每台节点最后都可能需要充当osd的角色，这里在克隆前先把磁盘创建好。

如果没有独立磁盘，我们可以在Linux下面创建一个虚拟磁盘进行挂载，步骤如下：

初始化10G的镜像文件：

```
sudo mkdir -p /usr/local/ceph-disk
sudo dd if=/dev/zero of=/usr/local/ceph-disk/ceph-disk-01 bs=1G count=10
```

将镜像文件虚拟成块设备：

```
sudo losetup -f /usr/local/ceph-disk/ceph-disk-01
```

注意，上一步执行的时候，可能系统会找不到空闲的loop设备。尤其是反复操作了好几次之后容易发生这种情况。这时可以查看目前所有loop设备，找到一个未使用的，并将其卸载。参考：[https://blog.csdn.net/litianze99/article/details/44453991](https://blog.csdn.net/litianze99/article/details/44453991)

使用`sudo fdisk -l`查询块设备，确定上一步将镜像文件映射到了哪个设备。在本文使用的系统中，第一次操作一般会映射到`loop6`。

格式化：

```
sudo mkfs.xfs -f /dev/loop6
```

上一步中的`loop6`需要替换成之前查到的设备。

挂载文件系统，将loop6磁盘挂载到/usr/local/ceph/data/osd/目录下。如果挂载点不存在，则需要新建。挂载点不空，则需要清空。

```
sudo mkdir /usr/local/ceph/data/osd/
sudo mount /dev/loop6 /usr/local/ceph/data/osd/
```

上一步中的`loop6`同样需要替换成之前查到的设备。

## 网络配置

本节开始之前，请将刚刚配置好的虚拟机克隆出另外两台，或者在另外两台机器上执行完全相同的步骤。虚拟机克隆的步骤参考：[https://blog.csdn.net/qq_42774325/article/details/81189033](https://blog.csdn.net/qq_42774325/article/details/81189033)

现在，你有了三台节点，接下来需要对它们进行网络配置。由于刚克隆好的机器完全一样，同时开机可能会造成IP地址冲突等问题，这里建议每次只操作一台机器。

### 环境

三台VMWare Ubuntu虚拟机（ubuntu-20.04.2-live-server-amd64.iso），Docker version 20.10.2，通过VMWare的NAT组网。

| 主机名 | IP             | 功能          |
| ------ | -------------- | ------------- |
| node0  | 192.168.92.200 | mon, osd, mgr |
| node1  | 192.168.92.201 | mon, osd, mgr |
| node2  | 192.168.92.202 | mon, osd, mgr |

在使用VMWare NAT固定IP组网时，需要特别注意在客户端上设置的默认网关一般是xxx.xxx.xxx.2，设置错了不影响内网，但是连不上外网。参考[https://www.jianshu.com/p/6fdbba039d79](https://www.jianshu.com/p/6fdbba039d79)

注意到原文是在CentOS上操作的，而新版本Ubuntu内的固定IP设置需要靠修改netplan实现。参考[https://www.jianshu.com/p/872e2e2e502d](https://www.jianshu.com/p/872e2e2e502d)

### 防火墙

部署前先关闭防火墙相关设置。

```
systemctl stop firewalld
systemctl disable firewalld
```

关闭SELinux。这个版本的Ubuntu上没有预装SELinux，可以不用操作，但是依然把步骤保留如下：

```
sed -i 's/enforcing/disabled/' /etc/selinux/config
setenforce 0
```

### 主机设置

分别在三台客户端上配置自己的主机名，重启生效。

```
# 在node0上
hostnamectl set-hostname node0
```

```
# 在node1上
hostnamectl set-hostname node1
```

```
# 在node2上
hostnamectl set-hostname node2
```

还需要在每个节点上设置别人的主机名。将下列内容加入到`/etc/hosts`中（需要sudo）：

```
192.168.92.200 node0
192.168.92.201 node1
192.168.92.202 node2
```

### SSH免密登录

在主节点node0配置免密登录到node1和node2，下面命令在主节点node0上执行即可，不需要执行三次。

```
ssh-keygen
ssh-copy-id node1
ssh-copy-id node2
```

## Ceph启动

### 启动MON

首先在主节点node0上执行`start_mon.sh`脚本，启动后通过`sudo docker ps -a`查看镜像是否创建成功，通过`sudo docker exec mon ceph -s`检查Ceph状态。启动成功之后会在`/usr/local/ceph/`生成配置数据。

在其他节点启动mon之前，需要先将配置数据原样拷贝至每个节点。理想情况下，执行下面的命令：

```
sudo scp -r /usr/local/ceph 你的用户名@node1:/usr/local/
sudo scp -r /usr/local/ceph 你的用户名@node2:/usr/local/
```

原文是使用CentOS操作的，默认用户是`root`，这样就可以成功了。但是在Ubuntu下，`root`不是一个日常操作的用户，而使用自己的用户来执行上面的命令会出现权限问题。具体而言，无法直接scp至node1和node2的`/usr/local/`目录。这时可以采取一个曲线救国的方式，先将node0的`/usr/local/ceph`scp至node1的一个非关键目录，比如`~/temp/`，再操作node1将其移动至`/usr/local/`：

```
# 在node0上
sudo scp -r /usr/local/ceph 你的用户名@node1:~/temp/
```

```
# 在node1上
sudo mv ~/temp/ceph/* /usr/local/ceph
```

在node2上也重复这个步骤。

之后，在node1和node2上也执行`start_mon.sh`脚本来启动mon并加入已有的集群。启动完成后，可以在任意一个节点上通过`sudo docker exec mon ceph -s`检查Ceph状态。

### 启动OSD

在执行`start_osd.sh`脚本之前，首先需要在mon节点生成osd的密钥信息，不然直接启动会报错。命令如下：

```
sudo docker exec -it mon ceph auth get client.bootstrap-osd -o /var/lib/ceph/bootstrap-osd/ceph.keyring
```

接着在每个节点执行`start_osd.sh`即可。

### 启动MGR

在每个节点执行`start_mgr.sh`即可。

### 启动MDS

在每个节点执行`start_mds.sh`即可。

全部启动完成后，在任意节点上执行`sudo docker exec mon ceph -s`查看集群状态，应该看到类似下面的信息：

```
  cluster:
    id:     6d8eb26d-xxxx-xxxx-xxxx-d2b241d7edbd
    health: HEALTH_WARN
            mons are allowing insecure global_id reclaim

  services:
    mon: 3 daemons, quorum node0,node1,node2 (age 116m)
    mgr: node0(active, since 103m), standbys: node2, node1
    mds:  3 up:standby
    osd: 3 osds: 3 up (since 103m), 3 in (since 103m)
```

下方的data相关信息，由于没有创建pool，所以全部为0。

## CephFS部署

下列步骤在node0执行即可。

### 创建Data Pool

```
sudo docker exec osd ceph osd pool create cephfs_data 128 128
```

### 创建Metadata Pool

```
docker exec osd ceph osd pool create cephfs_metadata 64 64
```

### 创建CephFS

```
docker exec osd ceph fs new cephfs cephfs_metadata cephfs_data
```

### 查看FS信息

```
sudo docker exec osd ceph fs ls
```

至此，搭建完成。

关于文件系统的挂载，参考：[https://blog.csdn.net/wylfengyujiancheng/article/details/81102717](https://blog.csdn.net/wylfengyujiancheng/article/details/81102717)

关于性能测试，参考：[https://www.cnblogs.com/Alysa-lrr/p/6027194.html](https://www.cnblogs.com/Alysa-lrr/p/6027194.html)