import random

from tests.BasicTest import BasicTest

class DisorderTest(BasicTest):
    def handle_packet(self):
        random.shuffle(self.forwarder.in_queue)
        for p in self.forwarder.in_queue:
            self.forwarder.out_queue.append(p)

        # empty out the in_queue
        self.forwarder.in_queue = []
