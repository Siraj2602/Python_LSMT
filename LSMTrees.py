from RedBlackTrees import RedBlackTree
from Compaction import CompactionManager
from SSTable import SSTable
from heapq import merge
import random
from pprint import pprint
import json
import time
from tqdm import tqdm
import os

def merge_sorted_lists(sorted_lists):
    return list(merge(*sorted_lists))

class LSMTree:
    def __init__(self, capacity=300000):
        self.memory = RedBlackTree()
        self.disk = []
        self.capacity = capacity
        self.sstable_no = 0
        self.tombstone = ""

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

    def _delete_key_helper(self, sstable_obj: SSTable, key):

        file_path = sstable_obj.filepath

        # Read the original JSON file line by line and update the specified key-value pair
        with open(file_path, 'r+') as file:
            
            key_start_index = None
            key_end_index = None
            segment_offset = ""
            for start_index, end_index in sstable_obj.index_table:
                if start_index <= key <= end_index:
                    segment_offset = sstable_obj.index_table[(start_index, end_index)]
                    key_start_index = start_index
                    key_end_index = end_index
                    break

            file.seek(int(segment_offset))

            segment_data = json.loads(file.readline())

            segment_data[key] = self.tombstone

            segment_data = [(int(key), value) for key, value in segment_data.items()]

            segment_data = dict(sorted(segment_data, key=lambda x: x[0]))

            file.seek(sstable_obj.index_table[(key_start_index, key_end_index)])

            json.dump(segment_data, file)

    def delete(self, key):
        if self.memory.search(key):
            self.memory.delete(key)
            return
        
        found = False
        for folder in self.sstable_map:
            for sstable_obj in self.sstable_map[folder]:
                if sstable_obj.find(key):
                    found = True
                    self._delete_key_helper(sstable_obj, key)
                    break

        if not found:
            print("Key not found")
    
    def _range_query_sstables(self, start, end):
        result = []
        for folder in self.sstable_map:
            for sstable_obj in self.sstable_map[folder]:
                index_table = sstable_obj.index_table
                for start_index, end_index in index_table.keys():
                    if end < start_index or start > end_index:
                        continue
                    else:
                        file_path = sstable_obj.filepath
                        with open(file_path, "r") as file:
                            line = file.readline()
                            full_data = {}
                            while line:
                                segment_data = json.loads(line)
                                full_data.update(segment_data)
                                line = file.readline()

                            full_data = full_data.items()
                            full_data = [(int(key) , value) for key, value in full_data]

                        sstable_elements = []
                        for key, value in full_data:
                            if start <= key <= end:
                                sstable_elements.append((key, value))
                        result.extend(sstable_elements)

        return result

    def range_query(self, start, end):
        result = []
        memory_keys = self.memory.range_query(start_key=start, end_key=end)
        result.extend(memory_keys)

        sstable_elements = self._range_query_sstables(start, end)

        result.extend(sstable_elements)

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
        self.compaction_manager.manage_compact()

    def compact(self):
        segments_to_merge = self.disk[:self.merge_threshold]
        merged_segment = merge_sorted_lists(segments_to_merge)

        self.disk = self.disk[self.merge_threshold:]
        self.disk.append(merged_segment)


# Example usage:
lsm_tree = LSMTree()

# Construct LSM tree
random_keys = random.sample(range(1, 10000001), 10000000)
#random_keys = [str(i) for i in random_keys]
random_values = random.sample(range(1, 10000001), 10000000)
random_elements = list(zip(random_keys, random_values))

start = time.time()
for element in tqdm(random_elements):
    lsm_tree.insert(element)

end = time.time()

print("Time taken for 10Million inserts ", end-start)
print("LSM Tree SSTable Dictionary", lsm_tree.sstable_map)

start = time.time()

result = lsm_tree.range_query(start=1, end=50000)

end = time.time()

print("Range Query result, ", len(result))
print("Start element :", result[0])
print("End element :", result[-1])
print("Range Query Time : ", end - start)

"""
for i in random.sample(range(10, 60), 40):
    lsm_tree.delete(random_elements[i][0])


start = time.time()

for i in tqdm(range(len(random_elements))):
    lsm_tree.delete(random_elements[i][0])

end = time.time()
print("Time taken for 50000 Deletes ", end-start)

"""