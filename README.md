## 发送端说明
发送端主要实现以下几点功能：
- 读取一个文件并将该文件通过UDP套接字发给指定的接收端
- 如果文件过大，需将文件划分为大小合适的段后再装入RUDP报文
- 通过start消息指定初始序号
- 在每个报文后附加校验和字段（生成和验证校验和的函数已经在Checksum.py中提供）
- 对于收到的校验和无效的ack消息，直接丢掉
- 通过Go Back N算法实现可靠传输（记得接收端窗口大小为5）
发送端应当在以下几种情况下仍然保证可靠传输：
- 丢包：任意等级的丢包，包括100%的丢包率，也包括数据包或确认包的丢失
- 失序：数据包到达接收端的顺序是任意的
- 重复：数据包可能会重复发送给接收端
发送端通过以下命令调用：
Python Sender.py -f <input file>
关于发送端的其他注意事项：
- 发送端应当设置一个500ms的重传计时器，对于超过500ms但是仍未收到确认消息的数据包，应当进行重传
- 发送端应当设置一个大小为5的发送窗口
- 发送端应当可以支持任意类型的文件（即可以发送图片/视频文件等等）
在此原代码基础上实现Go-Back-N算法和Selective Acknowledgements（选择重传）。
## 测试
TestHarness.py提供了一个测试框架（通过python TestHarness.py -s YourSender.py -r Receiver.py调用），tests目录下是具体的测试用例。
编写完测试用例后，需要在TestHarness.py中的tests_to_run函数中加入该测试用例，然后才能通过调用TestHarness运行该用例。
目前的测试用例包含了模拟丢包、失序和重复以及以上复合并传输多媒体格式的测试用例。
每种测试条件（丢包、失序、重复）写了两个测试类，分别用来测Go-Back-N和选择重传。

测试执行
python TestHarness.py -s Sender.py -r Receiver.py

## 源文档
In this folder you'll find the sample receiver, code for computing and
validating checksums, as well as example sender code.

Quick! What do I have to write?
===============================
Sender.py is the file in which you will implement your reliable sender.
Sender.py provides all the scaffolding you need to handle the
command line arguments we will use in the grading of your project.

The Receiver
============
Receiver.py is the sample receiver.

BasicSender and Friends
=======================
The BasicSender class in BasicSender.py provides a skeleton upon which to build
your reliable sender. It provides the following methods:

    __init__(self,dest,port,filename,debug=False,sackMode=False): Creates a
        BasicSender. Specify the destination's hostname, the port at which
        the receiver is listening, and a filename to transmit. If no filename
        is provided, it will read from STDIN.

    receive(self, timeout): Receive a packet. Waits for a packet before
        returning. Optionally you can specify a maximum timeout to wait for a
        packet. Returns the received packet as a string, or None if receive
        times out.

    send(self,message): Sends message to the receiver specified when you
        created the sender.

    make_packet(self,msg_type,seqno,message): Creates a RUDP packet from
        the specified message type, sequence number, and message. Generates the
        appropriate checksum, and returns the full RUDP packet with
        checksum appended.

    split_packet(self,packet): Given a RUDP packet, splits a packet into a
        tuple of the form (msg_type, seqno, data, checksum). For packets
        without a data field, the data element will be the empty string.

In addition, it defines one method which you must implement:

    start(self): Starts the Sender.

We provide two example senders that build upon the BasicSender; you are
welcome to base your design upon these:

UnreliableSender.py: While it provides no reliability, it will read from a file
or STDIN and send to a receiver using our protocol.

InteractiveSender.py: A simple interactive sender. It will send any message you
type to the specified receiver. It then waits for a response before prompting
you for a new message.

Checksums
=========
Checksum.py includes two functions for validating and generating checksums for
your packets:

    validate_checksum(message): Returns true if the message's checksum matches
        the message, and false otherwise. This function assumes the last field
        of the message the checksum.

    generate_checksum(message): Returns the checksum string for a message. This
        function assumes the message includes the trailing delimiter. The
        checksum is ONLY valid if you simply append this function's result to
        the message you pass in.

Testing
=======
You are expected to write test cases for your own code to ensure compliance
with the project specifications. To assist you, we've given you a simple test
harness (TestHarness.py). The test harness is designed to intercept all packets
sent between your sender and the receiver. It can modify the stream of packets
and check to ensure the stream meets certain conditions. This is very similar
to the grading script that we will use to evaluate your projects.

We have provided three test cases (BasicTest, DropRandomPackets, and
SackDropRandomPackets) as examples of how to use the test harness. These test
cases send this README file using the specified sender implementation to the
specified receiver implementation, either passing all packets through the
forwarder unmodified or dropping random packets. They both then verify that
the file received by the receiver matches the input.

To run a test using this test harness, do the following:

    python TestHarness.py -s YourSender.py -r Receiver.py

where "YourSender.py" is the path to your sender implementation, "Receiver.py"
is the path to the receiver implementation. Inside TestHarness.py, you need to
modify the function "tests_to_run" at the top of the script to include any test
cases you add.

Passing the basic test cases we provide is a necessary but not sufficient
condition for doing well on this project; there are still cases that they do not cover.

