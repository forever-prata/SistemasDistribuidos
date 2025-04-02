from dataclasses import dataclass
import threading
import time
import random

@dataclass
class Message:
    sender_id: int
    logical_clock: int
    content: str

class Process:
    def __init__(self, process_id, total_processes):
        self.process_id = process_id
        self.logical_clock = 0
        self.total_processes = total_processes
        self.mailbox = []
        self.lock = threading.Lock()

    def increment_clock(self):
        with self.lock:
            self.logical_clock += 1
            return self.logical_clock

    def send_message(self, receiver_process, content):
        clock = self.increment_clock()
        message = Message(self.process_id, clock, content)
        print(f"Process {self.process_id} (clock={clock}) sends message to Process {receiver_process.process_id}: '{content}'")
        receiver_process.receive_message(message)

    def receive_message(self, message):
        with self.lock:
            self.logical_clock = max(self.logical_clock, message.logical_clock) + 1
            self.mailbox.append(message)
            print(f"Process {self.process_id} (clock={self.logical_clock}) received message from Process {message.sender_id}: '{message.content}'")

    def internal_event(self):
        clock = self.increment_clock()
        print(f"Process {self.process_id} (clock={clock}) performs an internal event")

def simulate_process(process):
    for _ in range(3):
        time.sleep(random.uniform(0.1, 0.5))
        action = random.choice(["internal", "send"])
        
        if action == "internal":
            process.internal_event()
        else:
            other_process = random.choice([p for p in processes if p != process])
            process.send_message(other_process, f"Hello from {process.process_id}")

processes = [Process(i, 3) for i in range(3)]

threads = []
for process in processes:
    t = threading.Thread(target=simulate_process, args=(process,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("\nFinal logical clocks:")
for process in processes:
    print(f"Process {process.process_id}: {process.logical_clock}")