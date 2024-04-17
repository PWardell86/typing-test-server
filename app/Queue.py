class Queue:
    def __init__(self):
        self.q = []

    def put(self, item):
        self.q.append(item)

    def get(self):
        return self.q.pop(0)
    
    def has(self, item):
        return item in self.q

    def size(self):
        return len(self.q)

    def remove(self, item):
        self.q.remove(item)


