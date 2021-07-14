# 默认配置下的性能测试

使用Rados性能测试工具进行写测试，顺序读测试，随机读测试。

## 写测试

```
hurrypeng@node0:/usr/local$ sudo docker exec mon rados bench -p pool0 10 write --no-cleanup
hints = 1
Maintaining 16 concurrent writes of 4194304 bytes to objects of size 4194304 for up to 10 seconds or 0 objects
Object prefix: benchmark_data_node0_1059
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0      16        16         0         0         0           -           0
    1      16        20         4   15.1465        16    0.988697    0.768534
    2      16        28        12   23.3284        32     1.65521     1.06448
    3      16        46        30   39.0293        72     1.45035     1.43172
    4      16        56        40   38.8286        40     1.17152     1.32535
    5      16        69        53   41.3889        52     1.47377     1.34722
    6      16        79        63   41.1557        40     1.15899     1.33316
    7      16        98        82   45.9602        76    0.817211     1.27948
    8      16       110        94   46.1733        48     1.02199     1.25141
    9      16       121       105   45.9012        44     1.31435     1.26474
   10      16       129       113   44.5267        32    0.687286     1.26813
Total time run:         11.0407
Total writes made:      129
Write size:             4194304
Object size:            4194304
Bandwidth (MB/sec):     46.7363
Stddev Bandwidth:       18.1891
Max bandwidth (MB/sec): 76
Min bandwidth (MB/sec): 16
Average IOPS:           11
Stddev IOPS:            4.54728
Max IOPS:               19
Min IOPS:               4
Average Latency(s):     1.36492
Stddev Latency(s):      0.586269
Max latency(s):         3.32948
Min latency(s):         0.237294
```

## 顺序读

```
hurrypeng@node0:/usr/local$ sudo docker exec mon rados bench -p pool0 10 seq
hints = 1
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0      16        16         0         0         0           -           0
    1      16        26        10   39.3465        40    0.939169    0.503938
    2      16        48        32   63.3849        88    0.228749    0.855262
    3      16       114        98   129.795       264    0.575245    0.444874
    4      13       129       116   115.369        72    0.650047    0.406905
Total time run:       4.38024
Total reads made:     129
Read size:            4194304
Object size:          4194304
Bandwidth (MB/sec):   117.802
Average IOPS:         29
Stddev IOPS:          25.1661
Max IOPS:             66
Min IOPS:             10
Average Latency(s):   0.507471
Max latency(s):       2.00018
Min latency(s):       0.0118541
```

## 随机读

```
hurrypeng@node0:/usr/local$ sudo docker exec mon rados bench -p pool0 10 rand
hints = 1
  sec Cur ops   started  finished  avg MB/s  cur MB/s last lat(s)  avg lat(s)
    0      16        16         0         0         0           -           0
    1      16        78        62   243.481       248     1.00665    0.141633
    2      16       176       160   316.906       392   0.0234956    0.178979
    3      16       271       255   337.746       380  0.00789931    0.177046
    4      16       372       356   354.092       404     0.45456    0.172165
    5      16       481       465   370.369       436    0.012525    0.166875
    6      16       589       573   380.562       432    0.368795    0.163041
    7      16       697       681    387.85       432    0.294978    0.160827
    8      16       788       772   384.847       364    0.394631    0.161735
    9      16       897       881   390.487       436   0.0255106    0.157381
   10      16       996       980   391.001       396   0.0657781    0.159949
Total time run:       10.1666
Total reads made:     996
Read size:            4194304
Object size:          4194304
Bandwidth (MB/sec):   391.87
Average IOPS:         97
Stddev IOPS:          14.1657
Max IOPS:             109
Min IOPS:             62
Average Latency(s):   0.162156
Max latency(s):       1.04399
Min latency(s):       0.00481386
```

