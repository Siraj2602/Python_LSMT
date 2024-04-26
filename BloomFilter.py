import math
import mmh3
from bitarray import bitarray

class BloomFilter:
    def __init__(self, capacity, error_rate):
        self.capacity = capacity
        self.error_rate = error_rate
        self.bit_array = bitarray(self.capacity)
        self.bit_array.setall(0)

        self.num_hash_functions = int(-(capacity * (error_rate) / (math.log(2) ** 2)))

    def add(self, item):
        for i in range(self.num_hash_functions):
            hash_index = mmh3.hash(item, i) % self.capacity
            self.bit_array[hash_index] = True

    def __contains__(self, item):
        for i in range(self.num_hash_functions):
            hash_index = mmh3.hash(item, i) % self.capacity
            if not self.bit_array[hash_index]:
                return False
        return True

