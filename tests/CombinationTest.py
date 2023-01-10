import random
from tests.BasicTest import BasicTest

class CombinationTest(BasicTest):
    def handle_packet(self):
        random.shuffle(self.forwarder.in_queue)
        for p in self.forwarder.in_queue:
            if random.choice([True, False]):
                self.forwarder.out_queue.append(p)
                self.forwarder.out_queue.append(p)

        # empty out the in_queue
        self.forwarder.in_queue = []