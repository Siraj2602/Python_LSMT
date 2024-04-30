from BloomFilter import BloomFilter
import json

class SSTable:
    def __init__(self,folder_path ,filename, key_value_list, capacity):
        self.filename = filename
        self.filepath = folder_path + self.filename
        self.bloom_filter = BloomFilter(capacity=capacity, error_rate=0.01)

        for key, _ in key_value_list:
            self.bloom_filter.add(key)

        with open(self.filepath, 'w') as file:
            json.dump(dict(key_value_list), file)
    
    def find(self, key):
        if key in self.bloom_filter:
            return True
        return False
