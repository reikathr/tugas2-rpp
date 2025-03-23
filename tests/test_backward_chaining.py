from backward_chaining import solve, solve_opt

def run_tests():
    """
    Runs test cases for a given solver function.
    :param solver: The solver function to use (solve or solve_opt).
    :param solver_name: Name of the solver function (for display).
    """
    test_cases = [
        {
            "kb": [
                ['¬B', '¬C', 'A'],  # (¬B OR ¬C OR A)
                ['¬D', 'B'],        # (¬D OR B)
                ['C'],              # Fact: C
                ['D']               # Fact: D
            ],
            "queries": [
                (['A'], True),  # Can prove A
                (['B'], True),  # Can prove B
                (['E'], False)  # Cannot prove E
            ],
            "description": "Basic KB with A as goal"
        },
        {
            "kb": [
                ['¬X', 'Y'],  # (¬X OR Y)
                ['¬Y', 'Z'],  # (¬Y OR Z)
                ['X']         # Fact: X
            ],
            "queries": [
                (['Z'], True),  # Can prove Z
                (['Y'], True),  # Can prove Y
                (['X'], True),  # Can prove X
                (['W'], False)  # Cannot prove W
            ],
            "description": "Chain of dependencies: X -> Y -> Z"
        },
        {
            "kb": [
                ['¬P', 'Q', 'R'],  # (¬P OR Q OR R)
                ['¬Q', 'S'],       # (¬Q OR S)
                ['¬S'],            # (¬S) (fact)
                ['P']              # Fact: P
            ],
            "queries": [
                (['R'], True),  # Can prove R
                (['S'], False), # Cannot prove S
                (['P'], True)   # Can prove P
            ],
            "description": "More complex KB with negations"
        },
        {
            "kb": [
                ['C', 'E', 'E'],  # (C OR E OR E)
                ['¬D', 'C'],      # (¬D OR C)
                ['D']             # Fact: D
            ],
            "queries": [
                (['C'], True),  # Can prove C
                (['E'], False)  # Cannot prove E (no explicit evidence)
            ],
            "description": "Clause with repeated literals (C OR E OR E)"
        },
        {
            "kb": [
                ['¬E', 'E'],  # (¬E OR E) - Always true
                ['¬F', 'G'],  # (¬F OR G)
                ['F']         # Fact: F
            ],
            "queries": [
                (['G'], True),  # Can prove G
                (['E'], True)   # E is trivially true due to (¬E OR E)
            ],
            "description": "Tautology (¬E OR E) and other inference"
        }
    ]

    for solver_name, solver in [("Unoptimized Solve", solve), ("Optimized Solve", solve_opt)]:
        print(f"\n=== Running tests for {solver_name} ===")
        for i, case in enumerate(test_cases, 1):
            print(f"\n=== Test Set {i}: {case['description']} ===")
            for j, (query, expected) in enumerate(case["queries"], 1):
                print(f"\nTest {j}: Query = {query}")
                result = solver(case["kb"], query)
                print(f"Result: {result}, Expected: {expected}")
                assert result == expected, f"Test {i}.{j} failed!"
        print(f"\nAll test cases passed for {solver_name}!")

if __name__ == "__main__":
    run_tests()