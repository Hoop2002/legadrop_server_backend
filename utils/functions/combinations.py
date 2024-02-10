from itertools import combinations

def find_combinations(target, values):
    for r in range(1, len(values) + 1):
        for combination in combinations(values, r):
            if sum(combination) == target:
                yield combination



#result = list(find_combinations(target_number, value_set))

#for combination in result:
#    print(combination)
