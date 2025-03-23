import random

symbols = ['A', 'B', 'C', 'D', 'E']
connectives = ['and', 'or', 'implies', 'equiv']
negation = 'not '
N_LOGIC = 5

def random_atom():
    return random.choice(symbols)

def maybe_negate(s):
    return f"{negation}{s}" if random.random() < 0.3 else s

def random_expr(depth=0):
    if depth > 2 or random.random() < 0.3:
        return maybe_negate(random_atom())
    left = random_expr(depth + 1)
    right = random_expr(depth + 1)
    op = random.choice(connectives)
    return f"({left} {op} {right})"

def main():
    with open("logic_expressions.txt", "w", encoding="utf-8") as f:
        for _ in range(N_LOGIC):
            expr = random_expr()
            f.write(expr + "\n")

if __name__ == "__main__":
    main()