import random

from tests.BasicTest import BasicTest

class SackDisorderTest(BasicTest):
    def __init__(self, forwarder, input_file):
        super(SackDisorderTest, self).__init__(forwarder, input_file, sackMode = True)

    def handle_packet(self):
        random.shuffle(self.forwarder.in_queue)
        for p in self.forwarder.in_queue:
            self.forwarder.out_queue.append(p)

        # empty out the in_queue
        self.forwarder.in_queue = []