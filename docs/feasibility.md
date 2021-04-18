# 可行性报告

## 目录

[**项目介绍**](#项目介绍)

[**理论依据**](#理论依据)

​	[**分布式系统**](#分布式系统)

​	[**图数据库**](#图数据库)

​	[**文件的自然属性**](#文件的自然属性)

[**技术依据**](#技术依据)

​	[**文件系统监控**](#文件系统监控-watchdog)

​	[**文件传输**](#文件传输)

​	[**Linux平台下的FTP服务器**](#Linux平台下的FTP服务器-VSFTP)

​	[**Windows平台下的FTP服务器**](#Windows平台下的FTP服务器-FileZillaServer)

​	[**NEO4J**](#neo4j)

​	[**从机打标应用的技术**](#从机打标应用的技术)

[**技术路线**](#技术路线)

​	[**系统架构**](#系统架构)

​	[**操作实现**](#操作实现)

[**参考内容**](#参考内容)

## 项目介绍

​		在信息大爆炸的时代，人类所能够获取和存储的信息量不断增长，这对人类自身对大量信息的管理能力了更高的要求。但是，现有的基于树形结构的文件系统设计主要面向机器思维而非人类思维，这迫使人类不得不以机器的方式思考，试图将自己思维映射到树形结构上从而适应机器，从而导致人类不能按照自然的思维模式对存储的信息进行检索。在这种思维的扭曲下，分类困难、文件起名困难、找不到文件等令人头疼的问题便层出不穷。

​		考虑到人类的思维很大程度上基于信息与信息之间的“相关性”，用图的结构来描述文件之间的关系显然比树形结构更加符合人类思维。现有的图文件系统、图数据库文件系统等技术，都是对这种新思路的探索。典型的图文件系统采用算法自动对各种文件进行标记，通过寻找共同的标记进行建图，并且在图数据库中对图进行维护。这些项目说明了图文件系统技术的可行性与各种理论上优点，但是仍然不够成熟。它们目前仅仅持在单机上运行，一方面，由同一台机器完成存储、标记、索引等所有工作，容易造成资源的紧张；另一方面，单机信息规模的索引仍在人的记忆能力之内，对图文件系统的需求不突出。这几方面的原因导致图文件系统并未能够投入实用。

​		由此，我们提出构建分布式图文件系统（DisGraFS, Distributed Graph Filesystem）。在分布式机群的规模上，图文件系统能够实现所管理的信息规模的扩大与各类资源的均衡分配，从而在超出人类记忆能力的信息规模上体现出图文件系统相对于传统树形结构的优越性。通过主机（Master）对从机（Slave）的存储空间以及算力的合理调度以及在主机的指导下用户与从机之间的直接对接，我们的项目期望实现一个高效的、用户友好的、高可扩展性的分布式图文件系统，以进一步拓展图文件系统在未来应用中的可能性。

## 理论依据

### 分布式系统

​		相较于传统的单机存储，跨平台分布式系统的优点是：方便用户对存储空间的扩展，在目前个人持有设备数持续增加的时代，方便用户对于已有的设备上的文件进行更便捷的管理，以及对于为了可能持有的设备做出灵活的扩展。而相较于传统的树状检索，图检索更符合人类的使用习惯，尤其是在海量文件分布式存储的环境下，能为用户在检索文件的过程中节约大量时间。

​		目前主流的分布式文件系统有GFS、HDFS、Ceph、MooseFS等。这些项目各有优点，但是他们均不支持图数据库，部分也不支持跨平台。因此我们需要制作自己的跨平台图分布式系统，而不使用现成的产品。

以下简要说明上述数据库在本项目中可以汲取的优点：

- GFS：组件失效被认为是常态，有着良好的容忍组件失效的机制。对于文件的修改操作采用追加的形式而不是覆盖原有数据。
- HDFS：使用分布式冗余的方式实现了高度的容错性。
- Ceph：有高读扩展性，接口丰富，支持对象式存储，只需要将文件信息发送给主机而不需要发送完整的文件。

​        本项目DisGraFS将统一上述分布式文件系统的优点。并将图结构与思想应用于分布式文件系统上面，使得分布式图文件系统兼具图文件系统方便用户快速搜索，模糊搜索，查找相关文件的特点以及分布式文件系统的海量文件存储，云存储的特点。同时吸取前人的经验，整个项目开发过程均会使用便于跨平台的语言和属性，以满足当今以及未来社会对于多设备，多平台的大容量，快搜索的文件系统的需求。

### 图数据库

​		图数据库（graph database）是一个使用图结构进行查询的数据库，它使用节点、边和属性来表示和存储数据。该系统的关键概念是图，它直接将存储中的数据项，与数据节点和节点间表示关系的边的集合相关联。这些关系允许直接将存储区中的数据链接在一起，并且在许多情况下，可以通过一个操作进行检索。图数据库将数据之间的关系作为优先级。查询图数据库中的关系很快，因为它们永久存储在数据库本身中。可以使用图数据库直观地显示关系，使其对于高度互连的数据非常有效。

​		我们用图数据库中的结点来表示文件系统中的文件，将根据文件内容而做出的文件标签作为结点的属性，根据文件标签来构建文件节点之间的关系，使用成熟的图数据库进行储存和图的构建；用相应的算法来完成文件的上传（插入结点）、文件的删除（删除结点）、文件的查找（图的查询）等基本操作；并利用图数据库不断将文件之间的关系、整个文件图的储存等图属性进行优化，提高查找效率，使得在大规模的文件系统上的查询变得可行。

### 文件的自然属性

#### 文件的元数据(Metadata)

**元数据**[1]，又称**诠释资料**、**中介资料**、**中继资料**、**后设资料**等，为描述其他资料信息的资料。有三种不同类型的元数据，分别是**记叙性元数据**、**结构性元数据**和**管理性元数据**。

- 记叙性元数据描述了用于发现与辨别意义的资源。它可以包括如标题、摘要、作者和关键字等元素。

- 结构性元数据是有关于资料容器的元数据，指示如何整理其中复合的对象。例如页面依什么排序方式组成章节。

- 管理性元数据是用于管理资源的信息，例如资料产生的时间和方式、文件种类和其它技术信息，以及谁有权限访问它。

#### 文件的内容属性

虽然元数据在一定程度上描述了一个文件，但却无法提供一个文件的详细信息，如文本文档的关键词，音频大概在讲什么，图片中的内容是什么等。目前针对不同的文件类型的内容属性提取，有以下理论依据。

##### 自然语言处理 (**NLP**)

自然语言处理[2]是人工智能和语言学领域的分支学科。此领域探讨如何处理及运用自然语言；自然语言处理包括多方面和步骤，基本有认知、理解、生成等部分。

**自然语言认知和理解**是让电脑把输入的语言变成有意思的符号和关系，然后根据目的再处理。**自然语言生成系统**则是把计算机数据转化为自然语言。

##### 计算机视觉(CV)

计算机视觉[3]是一门研究如何使机器看的科学，更进一步的说，就是指用和计算机代替人眼对目标进行识别、跟踪和测量等机器视觉，并进一步做图像处理，用计算机处理成为更适合人眼观察或传送给仪器检测的图像。

## 技术依据

### 文件系统监控-watchdog

​		在我们的项目中，有多个场景需要使用到文件系统监控：从机管理实际的存储，需要对存储空间进行监控以便摸清存储状态、确保存储安全；从机和用户之间以及从机和从机之间进行文件传输，需要对缓冲区进行监控；主机和从机之间相互沟通，需要即时识别相互发送的信息，等等。这些文件系统事件直接起到了触发事件的作用，在整个分布式存储系统中十分关键。在考虑到效率的同时，由于我们希望做到对相关机器平台的要求最低，所以我们希望选择本身支持跨平台的技术进行文件系统监控。Python下实现的watchdog是一个较为理想的选择。

`watchdog`是一款用于监控文件系统事件的Python库，对不同平台的事件进行了封装。`watchdog`优先使用底层原生API，在没有API支持的情况下才会通过轮询磁盘实现监控。目前支持直接调用API的以下操作系统：

- Windows：ReadDirectoryChangesW
- Linux 2.6+：inotify
- Mac OS X：kqueue或FSEvents
- BSD Unix variants：kqueue

可以看到先前提到过的ReadDirectoryChangesW和inotify等函数在此处都会被优先使用，因而WatchDog理论上具有较高的效率。

WatchDog是一个第三方包，仅支持Python3.4+，需要另外安装：

```bash
pip install watchdog
```

WatchDog使用观察者模型，主要有observer、event_handler和被监控的文件夹三个角色，使用相对简单。

```python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(event.event_type, event.src_path)


event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path='.', recursive=False)
observer.start()
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

相应地得到类似下面的运行结果：

```
created .\a.txt
modified .\a.txt~
modified .\a.txt
moved .\a.txt
deleted .\b.txt
```

### 文件传输

​		在本项目中，有以下场景需要进行文件传输：用户和主机之间的通信，用户和从机进行的文件传输，从机和主机的通信，以及从机和从机之间在调度过程中的文件传输。其中用户和主机之间的通信以及从机和主机的通信，均为少量信息的交互，使用网络直接传输即可，而从机和用户之间的文件传输，以及从机和从机之间的文件传输，均会涉及到较大文件的传输，因此我们需要一种可以快速传输大文件的方式，如此才不会影响本文件系统整体的效率，于是我们选择了FTP的方式进行传输。

​		FTP全称为File Transfer Protocol，是 TCP/IP 协议组中的协议之一。FTP协议包括两个组成部分，其一为FTP服务器，其二为FTP客户端。其中FTP服务器用来存储文件，用户可以使用FTP客户端通过FTP协议访问位于FTP服务器上的资源。FTP传输效率非常高，适合传输大型文件。

​		对于用户与主机的信息交互，已经尝试过可行的方式是使用php和html的方式或是JavaScript和html的方式。以下给出php和html直接将信息传递到主机的代码，已经证明可以使用：

```html
<form action="upload_file.php" method="post" enctype="multipart/form-data">	            	<input class="button fit" type="file" name="file" id="file">
    <input class="shuangyebutton" type="submit" name="submit" value="提交">
</form>
```

```php+HTML
<?php
$temp = explode(".", $_FILES["file"]["name"]);
echo $_FILES["file"]["size"];
$extension = end($temp);     // 获取文件后缀名
if (($_FILES["file"]["size"] < 20480000))// 小于 20 mb
{
	if ($_FILES["file"]["error"] > 0)
	{
		echo "错误：: " . $_FILES["file"]["error"] . "<br>";
	}
	else
	{
		echo "上传文件名: " . $_FILES["file"]["name"] . "<br>";
		echo "文件类型: " . $_FILES["file"]["type"] . "<br>";
		echo "文件大小: " . ($_FILES["file"]["size"] / 1024) . " kB<br>";
		echo "文件临时存储的位置: " .  $_FILES["file"]["tmp_name"] . "<br>";
		
		if (file_exists("../Upload_File/" . $_FILES["file"]["name"]))
		{
			echo $_FILES["file"]["name"] . " 文件已经存在。 ";
		}
		else
		{
			move_uploaded_file($_FILES["file"]["tmp_name"], "../Upload_File/" . $_FILES["file"]["name"]);
			
			$str="../Upload_File/";
            $url="../Upload_File/";
            $str=str_replace($url,'<a href="'.$url.'">'.$url.'</a>', $str);
			echo "文件存储在: " . $str . $_FILES["file"]["name"];
		}
	}
}
else
{
	echo "非法的文件格式";
}
?>
```

​		通过上述代码我们可以发现，$_FILES对象中包含了用户上传的文件的多种信息，我们可以通过读取这些信息实现对文件特征的提取，从而可以方便我们后续对于文件管理，打标等操作的实现。		

​		另一种文件传输方式是使用php和html通过FTP的方式将文件传递到从机，使用FTP的优势在于，我们只需要传递不同的host值以及不同的用户名，就可以很方便的将用户端的文件分发到不同的从机，实现资源的合理分配，以下是基于php和html的FTP传输测试代码，已证明可以用来进行文件传输：

```html
<form action="upload_file.php" method="post" enctype="multipart/form-data">	            	<input class="button fit" type="file" name="file" id="file">
    <input class="shuangyebutton" type="submit" name="submit" value="提交">
</form>
```

```php
<?php
$host = 'slave1.disgrafs.tech';
$user = 'disgrafs';
$pwd = 'disgrafs';
 
// 进行ftp连接，根据port是否设置，传递的参数会不同
if(empty($port)){
    $f_conn = ftp_connect($host);
}else{
    $f_conn = ftp_connect($host, $port);
}
if(!$f_conn){
    echo "connect fail\n";
    exit(1);
}
echo "connect success\n";
 
// 进行ftp登录，使用给定的ftp登录用户名和密码进行login
$f_login = ftp_login($f_conn,$user,$pwd);
if(!$f_login){
    echo "login fail\n";
    exit(1);
}
echo "login success\n";
 
ftp_pasv($f_conn, true); 
 
// 进行文件上传
$result = ftp_put($f_conn, $_FILES["file"]["name"], $_FILES["file"]["tmp_name"], FTP_BINARY);
if(!$result){
    echo "upload file fail\n";
    exit(1);
}else{
    echo "upload file success\n";
    exit(0);
}

ftp_close($f_conn);
?>
```

​		以上代码中，设置FTP的部分为

```php
$host = 'slave1.disgrafs.tech';
$user = 'disgrafs';
$pwd = 'disgrafs';
```

​		其中host确定了本次文件传输使用的从机IP，user和pwd则存储着本次使用从机FTP服务器的用户名和密码，基于此本项目在后期还可设立用户登陆页面，使得不同的账号看到的是不同的图，从而更方便不同用户组的使用。

​		同时，除以上两种方法以外，还有node.js以及python也可以实现用户和主机之间的信息传输和文件传输，暂且可以作为本项目文件传输的备选项。

### Linux平台下的FTP服务器-VSFTP

​		VSFTP是一个基于GPL发布的类Unix系统上使用的FTP服务器软件，它的全称是Very Secure FTP。它是一个安全、高速、稳定的FTP服务器，可以做基于多个IP的虚拟FTP主机服务器，并且不执行任何外部程序，减少安全隐患，同时它还支持虚拟用户，每个虚拟用户可以具有独立的属性配置。

​		以下给出vsftp的常用命令

```
安装
yum install vsftpd
//或是
apt-get install vsftpd

添加新用户
useradd -d ./dir username
设置密码
passwd username

更改用户权限
usermod -s xxx username

重启vsftpd服务器
vsftpd restart
```

​		值得注意的是，在每一次修改配置文件之后均需要重启vsftpd服务器。

### Windows平台下的FTP服务器-FileZillaServer

​		基于Windows Server的服务器具有图形界面，使用开源FTP解决方案FileZilla的服务端软件，可以方便地进行FTP服务器的搭建。该软件支持多个FTP用户、用户组权限管理、主动/被动模式等FTP功能，可以用作项目中Windows平台主机/从机架设FTP服务器的解决方案。

![FileZillaServerDemo](./src/FileZillaServerDemo.jpg)

​		另外，为了使不更改DisGraFS客户端中的防火墙设置，FTP服务器应设为被动模式，并开放一定数量的被动模式端口。这些端口和21端口应该在服务器的防火墙设置中设为允许。

​		除此两种方法之外，还可以使用宝塔面板，对主机和从机进行方便快捷的统一化FTP配置，并且，宝塔面板具有一键配置SSH开启关闭，防火墙端口放行，可视化查看服务器CPU运行情况，内存占用情况，磁盘使用情况等多种功能，适用于后台的极速管理。

### neo4j

Neo4j是一个高性能的NOSQL图形数据库，它将结构化数据存储在图上而不是表中。它是一个嵌入式的、基于磁盘的、具备完全的事务特性的Java持久化高性能引擎，该引擎具有成熟数据库的所有特性。

- #### 储存结构[12]

  Neo4J属于原生图数据库，其使用的存储后端专门为图结构数据的存储和管理进行定制和优化的，在图上互相关联的节点在数据库中的物理地址也指向彼此，因此更能发挥出图结构形式数据的优势。

  - **Nodes: 15bytes**

    1byte：inUse标记和关系id的高位信息

    4 bytes：第一个relation id

    4 bytes：第一个property id

    5 bytes：4bytes的IsLables信息和1byte的hsbLables信息

    1 byte：保留字段extra，记录该Node是否为一个superNode

  - **Relation: 34bytes**

    1 byte：存该关系记录是否在使用中，以及关系的起点和下一个属性的高位信息

    8 bytes：该关系的起点和终点

    8 bytes：该关系的类型

    16 bytes：该关系起点前后关系、终点前后关系

    4 bytes：第一个property的id

    1 byte：是否为起终点的第一个关系

  - **property：41bytes**

    1 byte：前后property id的高位信息

    8 bytes：前后property

    32 bytes：默认的4个属性块

- #### Cypher查询语言[13]

  Cypher是以重声明式查询语言，可用于表达性歌搞笑的查询更新和图管理。它同时适合开发人员和运营管理人员。Cypher的设计简单同时功能强大，可以轻松表达高度复杂的数据库查询操作。Cypher受到许多不同方法的启发，并以表达查询为基础。 许多关键字（例如`WHERE`和`ORDER BY`）都受到SQL的启发。 模式匹配借鉴了SPARQL的表达方法。 某些列表语义是从Haskell和Python等语言中借用的，使查询变得容易。 

  例如，下面是一个创建图的简单实例：

  ```cypher
  CREATE (john:Person {name: 'John'})
  CREATE (joe:Person {name: 'Joe'})
  CREATE (steve:Person {name: 'Steve'})
  CREATE (sara:Person {name: 'Sara'})
  CREATE (maria:Person {name: 'Maria'})
  CREATE (john)-[:FRIEND]->(joe)-[:FRIEND]->(steve)
  CREATE (john)-[:FRIEND]->(sara)-[:FRIEND]->(maria)
  ```

  使用上述代码，即可创造出如下图所示的简单图:

  ![simple_example](./scr/simple_example.png)

  在这个图中，如果我们需要查询John的朋友，只需要使用下面的语句：

  ```cypher
  MATCH (john {name: 'John'})-[:FRIEND]->()-[:FRIEND]->(fof)
  RETURN john.name, fof.name
  ```

  就可以得到结果：

  ```
  +----------------------+
  | john.name | fof.name |
  +----------------------+
  | "John"    | "Maria"  |
  | "John"    | "Steve"  |
  +----------------------+
  2 rows
  ```

- #### **图算法**[14]

  Neo4j基于其特殊的储存结构与Cypher查询语言，设计并优化了多种图上的算法，使得查询、插入、删除等图操作的效率大大提高。

  - **中心性算法（Centrality algorithms）**:主要用来判断一个图中不同节点的重要性
  - **社区发现算法（Community detection algorithms）**:评估一个群体是如何聚集或划分的，以及其增强或分裂的趋势
  - **路径寻找算法（Path Finding algorithms）**:用于找到最短路径，或者评估路径的可用性和质量
  - **相似度算法（Similarity algorithms）**:用于计算节点间的相似度
  - **链接预测算法（Link Prediction algorithms）**:有助于确定一对节点的紧密程度
  - **预处理算法（Preprocessing functions and procedures）**:使用one-hot encoding对数据进行预处理

### 从机打标应用的技术

- #### pke


pke[4]是一个基于python的文本关键词提取工具包。 它提供了一个端到端的关键短语提取管道，其中的每个组件都可以轻松修改或扩展以开发新模型。 pke还可以轻松对最新的关键短语提取模型进行基准测试，并附带在SemEval-2010数据集上训练的监督模型。 

以下是一个用pke包提取关键词的代码实例：

```python
import pke

# initialize keyphrase extraction model, here TopicRank
extractor = pke.unsupervised.TopicRank()

# load the content of the document, here document is expected to be in raw
# format (i.e. a simple text file) and preprocessing is carried out using spacy
extractor.load_document(input='/path/to/input.txt', language='en')

# keyphrase candidate selection, in the case of TopicRank: sequences of nouns
# and adjectives (i.e. `(Noun|Adj)*`)
extractor.candidate_selection()

# candidate weighting, in the case of TopicRank: using a random walk algorithm
extractor.candidate_weighting()

# N-best selection, keyphrases contains the 10 highest scored candidates as
# (keyphrase, score) tuples
keyphrases = extractor.get_n_best(n=10)
```

- #### imagga


Imagga[5]图像自动标记技术可将相关标记或关键字自动分配给大量图像。 图像标记深度学习模型是Imagga计算机视觉产品的核心功能，它可以分析视觉图像的像素内容，提取其特征并检测感兴趣的物体。 该模型从日常生活中接受了3000多个对象的训练，并且可以额外地通过客户特定的标签进行训练，以实现最高的精度。 

以下是一个用imagga image tagging API进行图片打标的应用实例：

```python
import requests

url = "https://api.imagga.com/v2/tags"

querystring = {"image_url":"http://playground.imagga.com/static/img/example_photo.jpg","version":"2"}

headers = {
    'accept': "application/json",
    'authorization': "Basic YWNjXzJkYzdkNzNjMmYwODliMToxYzQ3Yzg2ZDg0YjdmYjdjYjZjNzQ1NTQ1MmYwNTgzMQ=="
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
```

- #### speech-to-text-wavenet[6]


speech-to-text-wavenet是一项语音转文本技术。它基于DeepMind的WaveNet，是原始音频生成模型的语音识别张量流实现。

经过初始训练后，即可实现语音转文本的功能。

```
python recognize.py --file 
```

- #### metadata_extractor[7]


元数据提取器是一个Java库，用于从媒体文件中读取元数据。 

以下是一个应用实例：

```java
Metadata metadata = ImageMetadataReader.readMetadata(imagePath);
```

## 技术路线

### 系统架构

DisGraFS分为3个组成部分：主机(Master), 从机(Slave), 客户端(Client)。

主机与用户使用网页端进行交互，通过浏览器本身的特性调用操作系统文件管理器，对用户文件进行分析，通过网络传递信息至主服务器。再由主机对文件信息分析，对从机空间进行调度之后，返回给用户本次传输的从机IP地址，用户的文件将通过FTP传输到指定的从机服务器上。最后，从机发送收到指令以及文件标签给主机，主机对图结构做出更新，等待下一次用户的操作。

下面对每一组成部分进行详细介绍。

#### 主机（Master）

主机是提供核心服务的服务器，负责构建、维护图数据库，管理调度计算和存储资源等。

主机系统包含以下几个模块：

* Graph Database

  *图数据库*根据文件语义关系，将DisGraFS所存储的所有文件链接以图结构保存，从而实现快速的、基于语义的文件搜索。

* Slave Info

  *从机信息*保存有所有从机的相关信息，如计算、存储、网络等资源的占用情况。从机信息是主机实现资源调度的前提。

* File Info

  *文件信息*保存有DisGraFS所存储的所有文件的信息，包括文件名称、类型、大小、标签、所在从机等。基于这些信息，从机可及时向用户提供文件的基本信息，满足与客户端实时交互的要求，并且可快速索引至文件存储的具体位置，从而实现对文件的修改操作。

* Scheduling Module

  *调度模块*根据从机存储资源占用情况，利用调度算法，在必要时将一些文件在从机间转移，进一步保证从机的计算、存储资源的占用平衡，使从机资源得到充分利用。

* Search Module

  为进一步增强对用户关键字的理解，提高搜索结果的准确性，*搜索模块*将用户关键字与已有标签进行语义相似度对比，根据与关键词最接近的标签查找文件，避免了因用户搜索关键词与文件标签不完全一致导致的搜索结果遗漏问题。

* Interaction Module

  *交互模块*实现主机与从机、客户端的必要信息传输。

  对于从机上传的文件标签信息，主机利用系统的文件监控及时对接受的标签信息进行反应，进行更新*图数据库*、*文件信息*等操作。每次接受的标签信息均会保留，增强了系统鲁棒性。

#### 从机（Slave）

从机提供计算及存储资源。用户可根据自己的需求增减从机数量。通过安装DisGraFS的从机端，用户可以快速地将自己的设备转变为DisGraFS的一部分，从而充分利用其算力和存储资源。

从机系统主要由以下部分组成：

* File Monitor

  *文件监控*模块利用系统接口实施监控本机文件的变动，从而对新增文件做出及时反应，包括建立标签并将标签上传至主机。

* Tag Generator

  *标签生成*利用多种现有的打标服务，对本机上的新增文件生成符合文件语义的标签，从而使此文件在主机的图数据库中构建正确关系。

* Interaction Module

  *交互模块*实现主机与从机、客户端的必要信息传输，包括向主机上传新增文件的标签信息，接受用户上传的新增文件等。

  对新增文件，从机会按照协议规定的格式生成`.json`文件，包含新增文件信息及其标签信息，并将此文件上传至主机。

#### 客户端（Client）

客户端负责直接接收用户对文件系统的操作，并将操作反馈以友好方式向用户展示。

客户端使用浏览器与主机交互。用户无需安装其他依赖，任何连接互联网的设备都可作为客户端。

### 操作实现

一个完整的文件系统需支持新增文件、文件搜索、获取文件和删除文件的操作。

下面分别介绍这些操作在DisGraFS上的实现流程。

#### 新增文件

1. 用户在客户端使用浏览器提出新增文件请求；客户端浏览器利用系统调用获取新增文件的信息，将信息上传至主机
2. 主机根据文件大小、类型等信息以及当前从机的资源调用情况，利用调度算法确定用于存储新增文件的从机；主机将所确定的从机地址返回给客户端
3. 客户端将用户的文件直接上传至目标从机
4. 从机的文件监控系统检测到新增文件；接受完毕后开始生成次文件的语义标签；从机将新增标签上传至主机
5. 主机根据标签将新增文件的连接加入图数据库系统

#### 文件搜索

1. 用户在客户端提出文件搜索请求；客户端将搜索关键字上传至主机
2. 主机*搜索模块*将关键字与现有文件的标签进行语义对比，在图数据库中搜索得文件连接，并在*文件信息*中获得相应文件信息；主机将获得的目标文件及其信息返回至客户端。

#### 文件获取

1. 用户在客户端提出获取文件的请求；客户端将目标文件ID上传至主机
2. 主机利用文件ID在*文件信息*中获取存储有此文件的从机信息；主机向此从机发送客户端地址及目标文件ID
3. 从机将目标文件传输至客户端设备

#### 删除文件

1. 用户在客户端提出获取文件的请求；客户端将目标文件ID上传至主机
2. 主机利用文件ID在*文件信息*中获取存储有此文件的从机信息；主机向此从机发送目标文件ID，并更新*文件信息*及*图数据库*中的数据。
3. 从机将目标文件删除

## 参考内容

[1]https://en.wikipedia.org/wiki/Metadata

[2]https://en.wikipedia.org/wiki/Natural_language_processing

[3]https://en.wikipedia.org/wiki/Computer_vision

[4]https://github.com/boudinfl/pke

[5]https://imagga.com/solutions/auto-tagging

[6]https://github.com/buriburisuri/speech-to-text-wavenet

[7]https://github.com/drewnoakes/metadata-extractor

[8]https://www.filezilla.cn/

[9]https://filezilla-project.org/

[10]https://www.w3school.com.cn/

[11]https://www.xenonstack.com/insights/graph-database/

[12]https://neo4j.com/docs/pdf/neo4j-getting-started-4.2.pdf

[13]https://neo4j.com/docs/pdf/neo4j-cypher-manual-4.2.pdf

[14]https://neo4j.com/docs/graph-algorithms/current/

