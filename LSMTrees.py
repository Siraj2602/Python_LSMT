from RedBlackTrees import RedBlackTree, Node
from heapq import merge
import random
from pprint import pprint

def merge_sorted_lists(sorted_lists):
    return list(merge(*sorted_lists))

class LSMTree:
    def __init__(self, capacity=5, merge_threshold=5):
        self.memory = RedBlackTree()
        self.disk = []
        self.capacity = capacity
        self.merge_threshold = merge_threshold

    def construct(self, data):
        self.disk.append(sorted(data))

    def free(self):
        self.disk = []

    def insert(self, element):
        key, value = element
        if self.memory.length < self.capacity:
            self.memory.insert(key, value)
        else:
            self.flush_memory_to_disk()
            self.memory = RedBlackTree()
            self.memory.insert(key,value)

    def find(self, key):
        if self.memory.search(key):
              return True
        for segment in self.disk[::-1]:
            if key in segment:
                return True
        return False


    def delete(self, key):
        if self.find(key):
            if self.memory.search(key):
                self.memory.delete(key)
                return
            for segment in self.disk:
                for k,v in segment:
                    if k == key:
                        segment.remove((k, v))
                    if len(segment) == 0:
                        self.disk.remove(segment)
                    break

    def range_query(self, start, end):
        result = []
        memory_keys = self.memory.range_query(start_key=start, end_key=end)
        result.extend(memory_keys)
        for segment in self.disk[::-1]:
            result.extend([(key,value) for key, value in segment if start <= key <= end])
        return sorted(result)

    def flush_memory_to_disk(self):
        memory_keys = self.memory.inorder_traversal()
        self.disk.append(memory_keys)
        self.memory = RedBlackTree()
        if len(self.disk) > self.merge_threshold:
            self.compact()

    def compact(self):
        segments_to_merge = self.disk[:self.merge_threshold]
        merged_segment = merge_sorted_lists(segments_to_merge)

        self.disk = self.disk[self.merge_threshold:]
        self.disk.append(merged_segment)


# Example usage:
lsm_tree = LSMTree()

# Construct LSM tree
random_keys = random.sample(range(1, 101), 35)
random_values = random.sample(range(1, 101), 35)
random_elements = list(zip(random_keys, random_values))
for element in random_elements:
    lsm_tree.insert(element)
print("Memory : ")
print(lsm_tree.memory.inorder_traversal())
print("Disk : ")
pprint(lsm_tree.disk)
print("Range Query: ")
print(lsm_tree.range_query(5, 70))