# CS222 Spring 2023
# Cache Simulator
#
# Example data structures
# for a direct-mapped cache
MEMORY_SIZE = 65536  # 2^16
CACHE_SIZE = 1024  # 2^10
CACHE_BLOCK_SIZE = 64    # 2^6
ASSOCIATIVITY = 1
memory = bytearray(MEMORY_SIZE)
# ================================================


class CacheBlock:
    def __init__(self, cache_block_size):
        self.tag = -1
        self.dirty = False
        self.valid = False
        self.data = bytearray(cache_block_size)
# ================================================


class CacheSet:
    def __init__(self, cache_block_size, associativity):
        self.blocks = [CacheBlock(cache_block_size)
                       for i in range(associativity)]
        self.tag_queue = [-1 for i in range(associativity)]
# ================================================


class Cache:
    def __init__(self, num_sets, associativity, cache_block_size):
        self.write_through = False
        self.sets = [CacheSet(cache_block_size, associativity)
                     for i in range(num_sets)]
        memory_size_bits = logb2(MEMORY_SIZE)
        self.cache_size_bits = logb2(CACHE_SIZE)
        self.cache_block_size_bits = logb2(cache_block_size)
        self.index_length = logb2(num_sets)
        self.block_offset_length = logb2(cache_block_size)
# ============================================================
# helper function: compute the log base 2 of the input param


def logb2(val):
    i = 0
    assert val > 0
    while val > 0:
        i = i+1
        val = val >> 1
    return i-1
