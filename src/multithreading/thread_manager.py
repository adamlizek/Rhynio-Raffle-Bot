from src.multithreading.thread import Thread


class ThreadManager:
    def __init__(self):
        self.threads = []

    def start_threads(self, action, action_init, count):
        self.threads.clear()

        shared_memory = action_init()
        
        for _ in range(count):
            self.threads.append(Thread(action, shared_memory))

        for thread in self.threads:
            thread.start()

    def stop_threads(self):
        for thread in self.threads:
            thread.stop()

