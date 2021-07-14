# Ceph部署指南

USTC OSH-2021-x-DisGraFS小组 彭怡腾

本指南参考

https://blog.csdn.net/qyf158236/article/details/113814906?utm_source=app&app_version=4.10.0&code=app_1562916241&uLinkId=usr1mkqgl919blen

相比原文，在功能上有所删减，但对于安装过程中的顺序做了一些调整和补充。

## 1、写在前面

由于本人在部署Ceph的过程中遇到过一些玄学问题，所以建议使用全新的虚拟机开展下面的部署环节。

我们选用CentOS7.9MINI操作系统作为虚拟机的操作系统，MINI版的CentOS体积较小，较轻量，安装下载较为简洁。

虚拟机需要有两块硬盘，其中一块（sdb）作为ceph的osd节点使用。

## 2、安装并配置环境

首先可以只在一台虚拟机上进行如下操作，之后再克隆即可。

首先，使用

```
nmtui
```

连接上网络，顺便可以修改hostname为ceph01，ceph02……

由于MINI系统实在是太小了，连wget也没有，所以，请下载wget。

```
yum install wget -y
```

将原repo源移动到另一个文件夹

```
cd /etc/yum.repos.d/
mkdir backup
mv C* backup
```

用wget命令下载新的yum源

```
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
```

配置ceph源

```
vi /etc/yum.repos.d/ceph.repo
```

请将如下内容写入ceph.repo

```
[ceph]
name=Ceph packages for
baseurl=https://mirrors.aliyun.com/ceph/rpm-mimic/el7/$basearch
enabled=1
gpgcheck=1
type=rpm-md
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc
priority=1

[ceph-noarch]
name=Ceph noarch packages 
baseurl=https://mirrors.aliyun.com/ceph/rpm-mimic/el7/noarch/
enabled=1
gpgcheck=1
type=rpm-md
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc
priority=1

[ceph-source]
name=Ceph source packages 
baseurl=https://mirrors.aliyun.com/ceph/rpm-mimic/el7/SRPMS/
enabled=1
gpgcheck=1
type=rpm-md
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc
priority=1
```

关闭防火墙

```
systemctl stop firewalld
systemctl disable firewalld
setenforce 0
vi /etc/selinux/config
SELINUX =disabled
```

创建ceph的文件夹

```
mkdir /etc/ceph
```

再克隆出两台虚拟机，将此三台虚拟机分别命名为ceph01，ceph02，ceph03。

在/etc/hosts文件中追加如下内容

```
192.168.85.10  ceph01
192.168.85.11  ceph02
192.168.85.12  ceph03
```

其中每一个节点前的ip地址可用

```
ip a
```

命令获得。

在ceph01上依次输入如下指令，按照提示操作，完成免密交互的建立。

```
ssh-keygen
ssh-copy-id root@ceph01
ssh-copy-id root@ceph02
ssh-copy-id root@ceph03
```

在ceph01上安装如下工具

```
yum install ceph-deploy ceph python-setuptools -y
```

在ceph02，ceph03上安装如下工具

```
yum install ceph python-setuptools -y
```

## 3、安装Ceph

如果你能成功进行到这一步，那么现在你已经快成功了，建议先去洗把脸，求个好运。

以下命令均在ceph01下进行。

进入文件夹

```
cd /etc/ceph
```

创建mon节点

```
ceph-deploy new ceph01
```

初始化

```
ceph-deploy mon create-initial
```

## 4、添加osd

以下命令均在ceph01下进行。

```
ceph-deploy osd create --data /dev/sdb ceph01
```

至此便已完成单机的部署。

```
ceph-deploy osd create --data /dev/sdb ceph02
```

```
ceph-deploy osd create --data /dev/sdb ceph03
```

此时查看集群状态可发现有两个osd加入进来。

```
 ceph -s
```

（可选，建议这么做，方便之后可能的操作）。

```
ceph-deploy admin ceph01 ceph02 ceph03
```

分别在ceph01，ceph02，ceph03上运行如下命令。

```
chmod +r ceph.client.admin.keyring 
```

至此，集群已创建完成，可开始使用或者测试。