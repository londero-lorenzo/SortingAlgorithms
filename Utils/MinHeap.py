class MinHeap:
    class Node:
        def __init__(self, key, data):
            self.key = key
            self.data = data
        def __le__(self, other):
            return self.key <= other.key
        def __lt__(self, other):
            return self.key < other.key
        def __gt__(self, other):
            return self.key > other.key
    def __init__(self):
        self.h = []
    @staticmethod
    def left(i):
        return 2*i+1
    @staticmethod
    def right(i):
        return (i+1)*2
    @staticmethod
    def parent(i):
        return (i-1)//2
    def heapify(self, i):
        l = MinHeap.left(i)
        r = MinHeap.right(i)
        if l < self.heap_size() and self[l] < self[i]:
            smallest = l
        else:
            smallest = i
            
        if r < self.heap_size() and self[r] < self[smallest]:
            smallest  = r
        
        if smallest != i:
            self.swap(i, smallest)
            self.heapify(smallest)
    def insert(self, node):
        self.h.append(node)
        node_index = self.heap_size() - 1
        while node_index > 0 and self[node_index] < self[MinHeap.parent(node_index)]:
            self.swap(node_index, MinHeap.parent(node_index))
            node_index = MinHeap.parent(node_index)
    def pop(self):
        if self.heap_size() == 0:
            raise IndexError("Pop from empty heap")
        self.swap(0, self.heap_size() - 1)
        min_node = self.h.pop()
        self.heapify(0)
        return min_node
    def peek(self):
        return self.h[0] if self.h else None
    def swap(self, i, k):
        self[i], self[k] = self[k], self[i]
    def clear(self):
        self.h = []
    def __getitem__(self, index):
        return self.h[index]
    def __setitem__(self, index, value):
        self.h[index] = value
    def heap_size(self):
        return len(self.h)

    def validate_heap(self):
        for i in range(self.heap_size()):
            l = MinHeap.left(i)
            r = MinHeap.right(i)
            if l < self.heap_size():
                assert self[i].key <= self[l].key, f"Heap invalid at {i}: {self[i].key} > {self[l].key}"
            if r < self.heap_size():
                assert self[i].key <= self[r].key, f"Heap invalid at {i}: {self[i].key} > {self[r].key}"