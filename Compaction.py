import os
import shutil
import csv
import json
import heapq 
from SSTable import SSTable

class CompactionManager:
    def __init__(self, parent_folder, subfolders, threshold, sstable_map):
        self.parent_folder = parent_folder
        self.subfolders = subfolders
        self.threshold = threshold
        self.folder_paths = {}
        self.merge_no = 0
        self.sstable_map = sstable_map

        if not os.path.exists(self.parent_folder):
            os.makedirs(self.parent_folder)
        for folder in self.subfolders:
            folder_path = os.path.join(self.parent_folder, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            self.folder_paths[folder] = folder_path
    
    def check_threshold_and_compact(self, folder_name):
        folder_path = self.folder_paths.get(folder_name)
        if folder_path:
            file_count = len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])
            if file_count >= self.threshold:
                self.compact_and_move(folder_name)
                return True
        
        return False

    def compact_and_move(self, folder_name):
        folder_path = self.folder_paths.get(folder_name)
        next_folder_index = self.subfolders.index(folder_name) + 1
        if next_folder_index < len(self.subfolders):
            next_folder_name = self.subfolders[next_folder_index]
            next_folder_path = self.folder_paths.get(next_folder_name)

        # List to store contents of all JSON files
        all_files_contents = []
        
        
        sstable_list = self.sstable_map[folder_name]
        for sstable in sstable_list:
            
            filepath = sstable.filepath
            with open(filepath, "r") as file:
                data_dict = json.load(file)
                all_files_contents.append(data_dict.items())
                
            os.remove(filepath)
        
        self.merge_no += 1
        
        compacted_file_name = 'merged' + str(self.merge_no)
        merged_sorted_list = list(heapq.merge(*all_files_contents))
        sstable_obj = SSTable(folder_path=next_folder_path + "/", filename=compacted_file_name , key_value_list=merged_sorted_list, capacity=len(merged_sorted_list))
        #all_files_contents.sort(key=lambda x: int(x['key']))
        
        self.sstable_map[folder_name] = []
        self.sstable_map[next_folder_name].append(sstable_obj)
        
        # Write the merged contents to a new CSV file in the next folder
       
    def manage_compact(self):
        for folder_name in self.subfolders:
            if not self.check_threshold_and_compact(folder_name):
                break
