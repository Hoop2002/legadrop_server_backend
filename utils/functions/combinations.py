def find_combination(target, values) -> list:
    dp = [False] * (target + 1)
    dp[0] = True
    prev = [None] * (target + 1)

    for i in range(1, target + 1):
        for val in values:
            if i >= val and dp[i - val]:
                dp[i] = True
                prev[i] = val

    closest_sum = target
    while not dp[closest_sum]:
        closest_sum -= 1

    combination = []
    current_sum = closest_sum
    while current_sum > 0:
        combination.append(prev[current_sum])
        current_sum -= prev[current_sum]

    return combination
