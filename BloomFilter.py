import math
import mmh3
from bitarray import bitarray

class BloomFilter:
    def __init__(self, capacity, error_rate):
        self.capacity = capacity
        self.error_rate = error_rate

        number_of_bits = int(-(self.capacity)*math.log(error_rate)/((math.log(2))**2))

        self.bit_array = bitarray(number_of_bits)
        self.bit_array.setall(0)

        self.num_hash_functions = int(number_of_bits*math.log(2)/self.capacity)

    def add(self, item):
        for i in range(self.num_hash_functions):
            hash_index = mmh3.hash(str(item), i) % len(self.bit_array)
            self.bit_array[hash_index] = True

    def __contains__(self, item):
        for i in range(self.num_hash_functions):
            hash_index = mmh3.hash(str(item), i) % len(self.bit_array)
            if not self.bit_array[hash_index]:
                return False
        return True

