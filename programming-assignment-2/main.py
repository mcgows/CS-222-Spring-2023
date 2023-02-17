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

    def read_from_offset(self, offset):
        if offset % 4 == 0:
            value = self.data[offset] + (self.data[offset + 1] << 8) + \
                (self.data[offset + 2] << 16) + (self.data[offset + 3] << 24)
            return value

    def read_from_memory(self, start_addr, end_addr):
        self.data = memory[start_addr: end_addr]


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

        print('-----------------------------')
        print(f'cache size = {CACHE_SIZE}')
        print(f'block size = {CACHE_BLOCK_SIZE}')
        num_blocks = CACHE_SIZE // CACHE_BLOCK_SIZE
        print(f'#blocks = {num_blocks}')
        print(f'#sets = {num_sets}')
        print(f'associativity = {ASSOCIATIVITY}')

        print(
            f'tag length = {logb2(MEMORY_SIZE // CACHE_SIZE)}')
        print('-----------------------------')

    def compute_offset_index_tag(self, address):
        # Takes the num bits that the Offset takes up
        index_shift = logb2(CACHE_BLOCK_SIZE)

        # Takes the number of bits that the block index, plus the block offset take up
        tag_shift = index_shift + \
            logb2((CACHE_SIZE // CACHE_BLOCK_SIZE) // ASSOCIATIVITY)

        offset = (address) & (CACHE_BLOCK_SIZE - 1)
        index = (address >> index_shift) & (CACHE_SIZE // CACHE_BLOCK_SIZE - 1)

        max_tag_val = MEMORY_SIZE // CACHE_SIZE
        tag = (address >> tag_shift) & (max_tag_val - 1)

        return offset, index, tag

    def read_word(self, address):
        self.worker_algo(address, read_flag=True)

    def write_word(self, address, word):
        # This is for part 2
        pass

    def worker_algo(self, address, read_flag):

        # Define inner output function
        def print_output_result(read_write, hit_miss_replace):
            print(
                f'{read_write} {hit_miss_replace} [addr={address} index={index} tag={tag}: word={word} ({bottom_mem_addr} - {top_mem_addr})]')

        def print_output_tag_queue():
            tag_queue_string = ''
            for elm in cache_set.tag_queue:
                tag_queue_string += (str(elm) + ' ')

            print(f'[ {tag_queue_string}]')

        def print_output_address_word():
            print(
                f'address = {address} {bin(address)[2:].zfill(logb2(MEMORY_SIZE))}; word = {word}')
            print('')

        def print_output_evict_tag(tag, block_index):
            print(f'evict tag {tag} in block_index {block_index}')

        def print_output_read_in_from_memory(start_addr, end_addr):
            print(f'read in ({start_addr} - {end_addr})')

        MAX_BYTE_VAL = 63  # 2^8 - 1
        offset, index, tag = self.compute_offset_index_tag(address)
        block_address = address // CACHE_BLOCK_SIZE
        bottom_mem_addr = CACHE_BLOCK_SIZE * block_address
        top_mem_addr = bottom_mem_addr + MAX_BYTE_VAL

        cache_set = self.sets[index]

        for block_index, block in enumerate(cache_set.blocks):
            # Cache Hit
            if (block.tag == tag) and (block.valid):
                word = self.read_or_write_from_cache(block, read_flag, offset)
                block.tag = tag
                block.valid = True
                cache_set.tag_queue = self.move_to_end_of_tag_queue(
                    cache_set.tag_queue, tag)

                print_output_result('read', 'hit')
                print_output_tag_queue()
                print_output_address_word()

                return

            # Cache Miss
            else:
                for block in cache_set.blocks:
                    if (not block.valid):
                        # Do the work to use this block

                        block.tag = tag
                        cache_set.blocks[block_index].valid = True
                        cache_set.tag_queue = self.move_to_end_of_tag_queue(
                            cache_set.tag_queue, tag)
                        block.read_from_memory(
                            bottom_mem_addr, top_mem_addr)

                        word = self.read_or_write_from_cache(
                            block, read_flag, offset)

                        print_output_result('read', 'miss')
                        print_output_tag_queue()
                        print_output_address_word()
                        return

                # Else we must evict a cache block
                    else:
                        # Find LRU block
                        for block in cache_set.blocks:
                            lru_tag = cache_set.tag_queue[0]

                            block.tag = tag
                            cache_set.blocks[block_index].valid = True
                            cache_set.tag_queue = self.move_to_end_of_tag_queue(
                                cache_set.tag_queue, tag, lru_tag)
                            block.read_from_memory(
                                bottom_mem_addr, top_mem_addr)

                            word = self.read_or_write_from_cache(
                                block, read_flag, offset)

                            print_output_result('read', 'miss + replace')
                            print_output_read_in_from_memory(
                                bottom_mem_addr, top_mem_addr)
                            print_output_evict_tag(lru_tag, block_index)
                            print_output_tag_queue()
                            print_output_address_word()
                            return

                    # update tag queue
                    # if (read_flag):
                    #     self.read_back(block)
                    # elif (write_allocate):
                    #   self.write_allocate(block)
                    #
                    # This will be for a write-back cache
                    # else:
                    #   self.check_dirty(block)

    def move_to_end_of_tag_queue(self, tag_queue: list[int], tag, lru_tag=None):
        invalid_tag = -1

        if invalid_tag in tag_queue:
            tag_queue.remove(invalid_tag)
        elif lru_tag:
            tag_queue.remove(lru_tag)

        else:
            tag_queue.remove(tag)
        tag_queue.append(tag)
        return tag_queue

    def write_back(self, block: CacheBlock):
        pass

    def write_allocate(self, block: CacheBlock):
        self.read_back(block)
        # write the value to the block
        # If write through
        #   self.write_back(block)

    def read_back(self, block: CacheBlock):
        pass

    def check_dirty(self, block: CacheBlock):
        if (block.dirty):
            self.write_back(block)

    def read_or_write_from_cache(self, block: CacheBlock, read_flag: bool, offset: int):
        if read_flag:
            # Do the work to read the word
            return block.read_from_offset(offset)

        # This is a write, don't worry about for now
        else:
            pass

    def read_or_write_from_memory(self, block: CacheBlock, read_flag: bool, offset: int):
        pass

# ============================================================
# helper function: compute the log base 2 of the input param


def logb2(val):
    i = 0
    assert val > 0
    while val > 0:
        i = i+1
        val = val >> 1
    return i-1


def init_memory():
    MAX_BYTE_NUM = 255  # 2^8 - 1
    for i in range(0, MEMORY_SIZE, 4):
        memory[i + 3] = (i >> 24) & MAX_BYTE_NUM
        memory[i + 2] = (i >> 16) & MAX_BYTE_NUM
        memory[i + 1] = (i >> 8) & MAX_BYTE_NUM
        memory[i] = (i) & MAX_BYTE_NUM


def main():
    init_memory()
    test_one()


def test_one():
    num_sets = (CACHE_SIZE // CACHE_BLOCK_SIZE) // ASSOCIATIVITY
    c = Cache(num_sets, ASSOCIATIVITY, CACHE_BLOCK_SIZE)
    c.read_word(46916)
    c.read_word(46932)
    c.read_word(12936)
    c.read_word(13964)
    c.read_word(46956)
    c.read_word(56132)


main()
