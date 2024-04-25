import queue


class Queue:
    """
    A implementation of a queue that allows for items to be marked for removal. \n
    If it is seen when popping from the queue, we remove it and continue until 
    we see one that isn't marked for removal.
    """
    def __init__(self):
        self.queue = queue.Queue()
        self.items_in_queue = {}

    def put(self, item):
        if item in self.items_in_queue:
            return False
        self.items_in_queue[item] = True
        self.queue.put(item)
        return True
    
    def mark_for_removal(self, item):
        if item not in self.items_in_queue:
            return False
        self.items_in_queue.pop(item)
        return True
    
    def contains(self, item):
        return item in self.items_in_queue
    
    def get(self):
        item = self.queue.get()
        while item not in self.items_in_queue:
            item = self.queue.get()
        return item