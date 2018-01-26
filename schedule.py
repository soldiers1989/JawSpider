# -*- coding: UTF-8 -*-
import sched
import os
import time

import time
import sched

# 第一个工作函数
# 第二个参数 @starttime 表示任务开始的时间
# 很明显参数在建立这个任务的时候就已经传递过去了，至于任务何时开始执行就由调度器决定了
def worker(msg, starttime):
    print u"任务执行的时刻", time.time(), "传达的消息是", msg, '任务建立时刻', starttime


# 创建一个调度器示例
# 第一参数是获取时间的函数，第二个参数是延时函数
print u'----------  两个简单的例子  -------------'
print u'程序启动时刻：', time.time()
s = sched.scheduler(time.time, time.sleep)
s.enter(1, 1, worker, ('hello', time.time()))
s.enter(3, 1, worker, ('world', time.time()))
s.run()  # 这一个 s.run() 启动上面的两个任务
print u'睡眠２秒前时刻：', time.time()
time.sleep(2)
print u'睡眠２秒结束时刻：', time.time()