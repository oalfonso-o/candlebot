class CircularQueue():
    def __init__(self, size):
        self.size = size
        self.queue = [None for i in range(size)]
        self.front = self.rear = -1

    def enqueue(self, data):
        if ((self.rear + 1) % self.size == self.front):
            self.dequeue()
        if self.front == -1:
            self.front = 0
            self.rear = 0
            self.queue[self.rear] = data
        else:
            self.rear = (self.rear + 1) % self.size
            self.queue[self.rear] = data

    def dequeue(self):
        if self.front == self.rear:
            temp = self.queue[self.front]
            self.front = -1
            self.rear = -1
            return temp
        else:
            temp = self.queue[self.front]
            self.front = (self.front + 1) % self.size
            return temp

    def get_queue(self):
        queue = []
        if self.rear >= self.front:
            for i in range(self.front, self.rear + 1):
                queue.append(self.queue[i])
        else:
            for i in range(self.front, self.size):
                queue.append(self.queue[i])
            for i in range(0, self.rear + 1):
                queue.append(self.queue[i])
        queue.reverse()
        return queue
