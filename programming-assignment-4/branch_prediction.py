import sys

BRANCH_BASE = 16


class BHT:
    def __init__(self, predictor_size_bits, memory_size_bits):
        self.size = (
            memory_size_bits
            if predictor_size_bits == 0
            else int(memory_size_bits / predictor_size_bits)
        )
        self.arr = [0] * self.size

    def addr_to_int(self, branch_addr):
        return int(branch_addr, BRANCH_BASE)

    def read_from_branch(self, branch_addr):
        return self.arr[self.addr_to_int(branch_addr) % self.size]

    def write_to_arr(self, branch_addr, new_value):
        self.arr[self.addr_to_int(branch_addr) % self.size] = new_value


def read_trace(fileName: str) -> list:
    branches = []
    with open(fileName) as file:
        lines = file.readlines()

        for line in lines:
            split = line.split()
            if split[0] != "#eof":
                branches.append({"branch": split[0], "result": split[1]})

    return branches


def static_bp(branches: list) -> dict:
    branches_checked, branches_correct, prediction = 0, 0, 0

    for branch in branches:
        branches_checked += 1
        if int(branch["result"]) == prediction:
            branches_correct += 1

    return {
        "checked": branches_checked,
        "correct": branches_correct,
        "percentage": round(branches_correct / branches_checked * 100.0, 2),
    }


def one_bit_bp(branches: list, bht: BHT) -> dict:
    branches_checked, branches_correct = 0, 0
    for branch in branches:
        prediction = bht.read_from_branch(branch["branch"])
        branches_checked += 1
        if int(branch["result"]) == prediction:
            branches_correct += 1
        else:
            bht.write_to_arr(branch["branch"], not prediction)

    return {
        "checked": branches_checked,
        "correct": branches_correct,
        "percentage": round(branches_correct / branches_checked * 100.0, 2),
    }


def saturating_counter(branch, max_saturated_value, bht):
    prediction = bht.read_from_branch(branch["branch"])

    predict_taken = False
    if prediction >= ((max_saturated_value + 1) / 2):
        predict_taken = True

    if int(branch["result"]) == 1:
        bht.write_to_arr(branch["branch"], min(prediction + 1, max_saturated_value))
        if predict_taken:
            return True

    else:
        bht.write_to_arr(branch["branch"], max(prediction - 1, 0))
        if not predict_taken:
            return True


def two_bit_bp(branches: list, bht: BHT) -> dict:
    TWO_BIT_MAX_SATURATED = 3
    branches_checked, branches_correct = 0, 0

    for branch in branches:
        branches_checked += 1
        if saturating_counter(branch, TWO_BIT_MAX_SATURATED, bht):
            branches_correct += 1

    return {
        "checked": branches_checked,
        "correct": branches_correct,
        "percentage": round(branches_correct / branches_checked * 100.0, 2),
    }


def three_bit_bp(branches: list, bht: BHT) -> dict:
    THREE_BIT_MAX_SATURATED = 7
    branches_checked, branches_correct = 0, 0

    for branch in branches:
        branches_checked += 1
        if saturating_counter(branch, THREE_BIT_MAX_SATURATED, bht):
            branches_correct += 1

    return {
        "checked": branches_checked,
        "correct": branches_correct,
        "percentage": round(branches_correct / branches_checked * 100.0, 2),
    }


def main():
    cmd_args = sys.argv

    if len(cmd_args) != 4:
        print(
            """Please call with args for trace file name, 
            number of bits for predictor, and size of BHT"""
        )
        return

    trace = cmd_args[1]
    predictor_size = int(cmd_args[2])
    memory_size = int(cmd_args[3])
    branches = read_trace(trace)

    bht = BHT(predictor_size, memory_size)

    if predictor_size == 0:
        print("=== STATIC ===")
        static = static_bp(branches)
        print(static)

    elif predictor_size == 1:
        print(f"=== ONE BIT === | === MEMORY SIZE {memory_size} ===")
        one_bit = one_bit_bp(branches, bht)
        print(one_bit)

    elif predictor_size == 2:
        print(f"=== TWO BIT === | === MEMORY SIZE {memory_size} ===")
        two_bit = two_bit_bp(branches, bht)
        print(two_bit)

    elif predictor_size == 3:
        print(f"=== THREE BIT === | === MEMORY SIZE {memory_size} ===")
        three_bit = three_bit_bp(branches, bht)
        print(three_bit)

    else:
        print("please enter valid predictor size in size { 0, 1, 2, 3 }")


main()
