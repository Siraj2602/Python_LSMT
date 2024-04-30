from RedBlackTrees import RedBlackTree
from Compaction import CompactionManager
from SSTable import SSTable
from heapq import merge
import random
from pprint import pprint
import json

def merge_sorted_lists(sorted_lists):
    return list(merge(*sorted_lists))

class LSMTree:
    def __init__(self, capacity=1500):
        self.memory = RedBlackTree()
        self.disk = []
        self.capacity = capacity
        self.sstable_no = 0

        parent_folder = "disk"
        subfolders = [f"folder{i}" for i in range(1, 6)]
        threshold = 3

        self.sstable_map = dict()
        for folder in subfolders:
            self.sstable_map[folder] = []

        self.compaction_manager = CompactionManager(parent_folder, subfolders, threshold, self.sstable_map)

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
        
        for folder in self.sstable_map:
            for sstable_obj in self.sstable_map[folder]:
                if sstable_obj.find(key):
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
        memory_key_values = self.memory.inorder_traversal()
        self.sstable_no += 1
        sstable_name = "sstable" + str(self.sstable_no)

        sstable = SSTable(folder_path="disk/folder1/", filename=sstable_name, key_value_list=memory_key_values, capacity=self.capacity)
        self.sstable_map["folder1"].append(sstable)
        self.memory = RedBlackTree()
        #if len(self.disk) > self.merge_threshold:
        #    self.compact()
        print("Flushed Memtable to SSTable No. ", self.sstable_no)
        self.compaction_manager.manage_compact()

    def compact(self):
        segments_to_merge = self.disk[:self.merge_threshold]
        merged_segment = merge_sorted_lists(segments_to_merge)

        self.disk = self.disk[self.merge_threshold:]
        self.disk.append(merged_segment)


# Example usage:
lsm_tree = LSMTree()

# Construct LSM tree
random_keys = random.sample(range(1, 50001), 50000)
random_values = random.sample(range(1, 50001), 50000)
random_elements = list(zip(random_keys, random_values))
for element in random_elements:
    lsm_tree.insert(element)

print("LSM Tree SSTable Dictionary", lsm_tree.sstable_map)

"""
print("Memory : ")
print(lsm_tree.memory.inorder_traversal())
print("Disk : ")
pprint(lsm_tree.disk)
print("Range Query: ")
print(lsm_tree.range_query(5, 70))
"""