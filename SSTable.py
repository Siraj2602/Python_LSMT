from BloomFilter import BloomFilter
import json

class SSTable:
    def __init__(self,folder_path ,filename, key_value_list, capacity):
        self.filename = filename
        self.filepath = folder_path + self.filename
        self.bloom_filter = BloomFilter(capacity=capacity, error_rate=0.01)
        self.index_table = {}
        self.delete_meta_path = self.filepath + "_delete_meta"
        self.segment_size = int(0.1 * len(key_value_list))
        start_offset = 0

        for key, _ in key_value_list:
            self.bloom_filter.add(key)

        number_of_segments = int(len(key_value_list) // self.segment_size)  # Number of segments created for the SSTable
        start_offset = 0  # Start offset of the segment in the file
        with open(self.filepath, 'w') as file:
            for i in range(number_of_segments):
                start_index = i * self.segment_size
                end_index = start_index + self.segment_size
                start_offset = file.tell()
                # Slicing the current segment data from the key value list. And dumping in the file.
                current_segment_data = key_value_list[start_index : end_index]
                json.dump(dict(sorted(current_segment_data)), file)
                file.write("\n")
                # Calculating the offset on the file at the end of the write of the current segment.
                key_range = (int(current_segment_data[0][0]), int(current_segment_data[-1][0]))
                self.index_table[key_range] = start_offset
                
                # Changing the start of the segment for the next iteration.
    
    def find(self, key):
        if key in self.bloom_filter:
            return True
        return False
