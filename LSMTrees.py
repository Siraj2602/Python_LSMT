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
import shutil

def merge_sorted_lists(sorted_lists):
    return list(merge(*sorted_lists))

class LSMTree:
    def __init__(self, capacity):
        self.memory = RedBlackTree()
        self.disk = []
        self.capacity = capacity
        self.sstable_no = 0
        self.tombstone = ""

        self.parent_folder = "disk"
        subfolders = [f"folder{i}" for i in range(1, 6)]
        threshold = 3

        self.sstable_map = dict()
        for folder in subfolders:
            self.sstable_map[folder] = []

        self.compaction_manager = CompactionManager(self.parent_folder, subfolders, threshold, self.sstable_map)

    def free(self):
        self.memory = RedBlackTree()
        
        folder_path = self.parent_folder
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            # If the item is a file, delete it
            if os.path.isfile(item_path):
                os.unlink(item_path)
            # If the item is a folder, delete it recursively
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                
        self.__init__(self.capacity)

    def insert(self, element):
        #key, value = element
        if self.memory.length < self.capacity:
            self.memory.insert(element)
        else:
            self.flush_memory_to_disk()
            self.memory = RedBlackTree()
            self.memory.insert(element)
    
    def construct(self, key_val_list):
        for key, value in key_val_list:
            self.insert((key, value))

    def _find_helper(self, sstable_obj: SSTable, key):
        
        file_path = sstable_obj.filepath

        # Read the original JSON file line by line and update the specified key-value pair
        with open(file_path, 'r') as file:
            segment_offset = ""
            for start_index, end_index in sstable_obj.index_table:
                if start_index <= key <= end_index:
                    segment_offset = sstable_obj.index_table[(start_index, end_index)]
                    break
                
            if not segment_offset :
                return False
            file.seek(int(segment_offset))
            segment_data = json.loads(file.readline())
            
            if str(key) in  segment_data:
                return segment_data[str(key)]
            else:
                return False
    
    def find(self, key):
        node = self.memory.search(key)
        if node:
            return node.value
        
        

        for folder in self.sstable_map:
            for sstable_obj in self.sstable_map[folder]:
                if sstable_obj.find(key):
                    val = self._find_helper(sstable_obj, key)
                    if val == False:
                        self.fp_count += 1
                    else:
                        return val       
        return False

    def _delete_key_helper(self, sstable_obj, key):
        # Perform deletion logic for a key within an SSTable
        # Here, we need to check delete_meta file associated with the SSTable

        delete_meta_file_path = sstable_obj.delete_meta_path


        with open(delete_meta_file_path, 'a') as f:
            f.write(str(key) + "\n")


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
        else:
            #print("key is deleted!!")
            pass

        
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


number_of_elements = 1000000

# Example usage:
lsm_tree = LSMTree(capacity=int(0.05*number_of_elements))

# Construct LSM tree
random_keys = random.sample(range(1, number_of_elements + 1), number_of_elements)
#random_keys = [str(i) for i in random_keys]
random_values = random.sample(range(1, number_of_elements + 1), number_of_elements)
random_elements = list(zip(random_keys, random_values))

start = time.time()

lsm_tree.construct(random_elements)

end = time.time()

print("Time taken for inserts :", end-start)

"""
start = time.time()

for key, val in tqdm(random_elements[250000:]):
    lsm_tree.find(key)

end = time.time()

print("Time taken for finds :", end-start)

print("\n False positive count for 50000 is , ", lsm_tree.fp_count)
"""
start = time.time()

result = lsm_tree.range_query(start=1, end=int(number_of_elements * 0.5))

end = time.time()

print("Time taken for Range Query : ", end - start)

range_query_time = end - start

start = time.time()

for key, val in tqdm(random_elements[: int(number_of_elements * 0.5)]):
    lsm_tree.delete(key)

end = time.time()

print("Time taken for Deletion : ", end - start)

for element in tqdm(random_elements[: int(number_of_elements*0.5)]):
    lsm_tree.insert(element)
    
start = time.time()

lsm_tree.free()

end = time.time()

print("Time taken for Free : ", end - start)
