# verifier/generator.py

import random

def generate_states(num_tests, min_val, max_val):
    """
    Generates up to `num_tests` unique test states (x, y, z) in the range [min_val, max_val].
    Includes boundary seed cases (0, 1, -1, min, max) and fills with random values.
    """
    if min_val > max_val:
        raise ValueError("Minimum value cannot be greater than maximum value.")

    # Core boundaries
    seeds = {0, 1, -1, min_val, max_val}
    seeds = {v for v in seeds if min_val <= v <= max_val}
    seed_list = list(seeds)

    states = set()

    # 1. Seed some standard combinations of boundary values
    # If the user requested very few tests, seed fewer.
    seed_limit = min(num_tests // 3 + 1, 30)
    if seed_list:
        for _ in range(seed_limit):
            bx = random.choice(seed_list)
            by = random.choice(seed_list)
            bz = random.choice(seed_list)
            states.add((bx, by, bz))

    # 2. Compute physical combinations limit to prevent infinite search loops
    range_size = max_val - min_val + 1
    # Check if range is small, (e.g. range_size = 2 -> 2^3 = 8 combinations)
    if range_size < 1000:
        max_possible = range_size ** 3
    else:
        max_possible = float('inf')

    target_limit = min(num_tests, max_possible)

    # 3. Add random states to fill the target limit
    attempts = 0
    max_attempts = target_limit * 10
    while len(states) < target_limit and attempts < max_attempts:
        rx = random.randint(min_val, max_val)
        ry = random.randint(min_val, max_val)
        rz = random.randint(min_val, max_val)
        states.add((rx, ry, rz))
        attempts += 1

    # 4. Convert tuples to dictionaries and shuffle
    result = [{'x': s[0], 'y': s[1], 'z': s[2]} for s in states]
    random.shuffle(result)
    return result
