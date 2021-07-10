# JuiceFS Introduction

## 简介

> JuiceFS 是一款高性能 [POSIX](https://en.wikipedia.org/wiki/POSIX) 文件系统，针对云原生环境特别优化设计，在 GNU Affero General Public License v3.0 开源协议下发布。使用 JuiceFS 存储数据，数据本身会被持久化在对象存储（例如，Amazon S3），而数据所对应的元数据可以根据场景需求被持久化在 Redis、MySQL、SQLite 等多种数据库引擎中。JuiceFS 可以简单便捷的将海量云存储直接接入已投入生产环境的大数据、机器学习、人工智能以及各种应用平台，无需修改代码即可像使用本地存储一样高效使用海量云端存储。

DisGraFS采用JuiceFS作为底层的分布式文件系统。上面是一段来自其GitHub仓库的介绍。目前，JuiceFS有两个版本：一个是2021年刚刚开源的版本，也就是[GitHub上的版本](https://github.com/juicedata/juicefs)，需要自己在服务器上搭建；另一个是[软件即服务版本](https://juicefs.com/)，由其开发公司直接提供服务。两种版本有不同的客户端，不能混用。在DisGraFS中，我们采用开源版本，在一个阿里云服务器上自己搭建。

从介绍中可以看出，JuiceFS仅仅是作为一个中间件，提供一个兼容POSIX标准的文件系统接口，其本身并不负责底层的存储。其底层存储可以使用各种常见的分布式存储服务或框架，如Ceph、Hadoop、亚马逊S3、阿里云OSS等。DisGraFS使用阿里云OSS作为底层存储。

## JuiceFS的搭建

DisGraFS在一台Windows服务器上搭建了JuiceFS，大体流程和[官网文档](https://github.com/juicedata/juicefs/blob/main/docs/zh_cn/quick_start_guide.md)一致，此处不再赘述。需要注意的几个问题是，该服务器上需要先安装redis再安装JuiceFS，而且要在服务器防火墙设置中开放几个特定的端口。

## JuiceFS的挂载

为了访问JuiceFS内的数据，需要先将JuiceFS挂载为当前操作系统的一个磁盘/文件夹。具体到DisGraFS，客户端和Ray分布式计算集群都需要挂载JuiceFS：客户端需要直接通过挂载的接口来操作文件，而Ray集群需要从JuiceFS中将用户上传的文件取出进行语义识别。挂载的过程也可以参考官网文档。为了方便用户进行挂载，DisGraFS中也整理了一份JuiceFS挂载指南。挂载中所需要使用的各种参数，在搭建JuiceFS的过程中都会遇到，无需额外解释。

本仓库中也包含了我们所使用的JuiceFS客户端。如果有更新版本的客户端，也可以从官网上下载。需要特别注意的是，开源版JuiceFS和服务版JuiceFS的客户端文件名相同，但是内容不相同，使用时一定要小心区分。

