#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import getopt
import Checksum
import BasicSender
import base64

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''


class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False, timeout=0.5):
        super(Sender, self).__init__(dest, port, filename, debug)
        self.sackMode = sackMode
        self.timeout = timeout
        self.win = 5  # 窗口大小
        self.base = 0  # 窗口前沿
        self.next_seqno = 0  # 下一个要发的seqno
        self.packets = []  # 要发的包
        self.ack = 0
        self.acks = []

    # Handles a response from the receiver.
    def handle_response(self, response_packet):
        if not Checksum.validate_checksum(response_packet):
            print("recv: %s <--- CHECKSUM FAILED" % response_packet)
            # 校验和不对就丢弃，直接返回即可
            return
        handle_pieces = response_packet.split('|')
        ack_type, ackno = handle_pieces[0:2]
        if (ack_type == "ack"):
            self.ack = int(ackno)
        elif (ack_type == "sack"):
            sack = ackno.split(";")
            self.ack = int(sack[0])
            if (self.sackMode):
                s_ack = sack[1].split(",")
                if (s_ack[0] != ''):
                    ack_s = [int(i) for i in s_ack]
                    for j in ack_s:
                        self.acks[j] = 1

        if self.ack >= self.base:
            self.handle_new_ack(self.ack)

    # Main sending loop.
    def start(self):
        seqno = 0
        # 分割数据到packets中
        msg = self.infile.read(500)
        msg_type = None
        while not msg_type == 'end':
            next_msg = self.infile.read(500)

            msg_type = 'data'
            if seqno == 0:
                msg_type = 'start'
            elif next_msg == "":
                msg_type = 'end'
            msg = base64.b64encode(msg)
            packet = self.make_packet(msg_type, seqno, msg)
            self.packets.append(packet)

            msg = next_msg
            seqno += 1

        self.infile.close()
        length = len(self.packets)
        self.acks = [0]*length

        while (self.ack < length):
            if (self.sackMode):
                no = self.next_seqno
                while (self.next_seqno < min(self.base+self.win, length)):
                    if (self.acks[self.next_seqno] == 0): 
                        self.send(self.packets[self.next_seqno])
                    self.next_seqno += 1

            else:
                no = self.next_seqno
                while (self.next_seqno < min(self.base+self.win, length)):
                    self.send(self.packets[self.next_seqno])
                    self.next_seqno += 1

            response = self.receive(self.timeout)

            if (response == None):
                self.handle_timeout(no)
            else:
                response = response.decode()
                self.handle_response(response)

    def handle_timeout(self, no):
        # no超时，下一次从no开始
        self.next_seqno = no

    def handle_new_ack(self, ack):
        self.base = ack
        if (self.sackMode == True):
            flag = 1
            for i in range(self.base, min(self.base+self.win, len(self.acks))):
                if (self.acks[i] == 0):
                    flag = 0
                    self.next_seqno = i
                    break
            if (flag == 1):
                self.next_seqno = ack
        else:
            self.next_seqno = ack

    def handle_dup_ack(self, ack):
        pass

    def log(self, msg):
        if self.debug:
            print(msg)


'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print("RUDP Sender")
        print("-f FILE | --file=FILE The file to transfer; if empty reads from STDIN")
        print("-p PORT | --port=PORT The destination port, defaults to 33122")
        print("-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost")
        print("-d | --debug Print debug messages")
        print("-h | --help Print this usage message")
        print("-k | --sack Enable selective acknowledgement mode")

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    timeout = 0.5
    sackMode = False

    for o, a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest, port, filename, debug, sackMode, timeout)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
