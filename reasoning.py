def solve(kb, query):
    """
    SLD resolution using backward chaining for CNF clauses.
    :param kb: List of clauses (each clause is a list of literals).
    :param query: List of literals to prove.
    :return: True if query is entailed by KB, else False.
    """
    if not query:
        return True  # Base case: If query is empty, we have proven all goals

    q = query[0]  # Take the first goal
    rest_query = query[1:]  # Remaining goals

    # Try to resolve q using KB
    for clause in kb:
        if q in clause:  # If q appears in a clause, try resolving its subgoals
            # Negate every [¬p1,...,¬pm]
            new_query = [(lit.replace('¬', '') if '¬' in lit else '¬' + lit) for lit in clause if lit != q] + rest_query
            print(f"new query: {new_query}")
            if solve(kb, new_query):  # Recursively check if the new query can be solved
                return True

    return False  # If no resolution leads to success, return False

def solve_opt(kb, query, cache=None):
    """
    SLD resolution using backward chaining for CNF clauses with caching.
    :param kb: List of clauses (each clause is a list of literals).
    :param query: List of literals to prove.
    :param cache: A dictionary to store visited queries.
    :return: True if query is entailed by KB, else False.
    """
    if cache is None:
        cache = {}

    # Convert query to a canonical tuple representation
    query_key = tuple(sorted(query))
    if query_key in cache:
        return cache[query_key]

    if not query:
        cache[query_key] = True
        return True

    q = query[0]         # Take the first goal
    rest_query = query[1:]  # Remaining goals

    # Try to resolve q using KB
    for clause in kb:
        if q in clause:  # If q appears in a clause, try resolving its subgoals
            # Negate every literal in the clause except q
            new_query = [(lit.replace('¬', '') if '¬' in lit else '¬' + lit) 
                         for lit in clause if lit != q] + rest_query
            print(f"Resolving {q} using clause {clause} gives new query: {new_query}")
            if solve_opt(kb, new_query, cache):  # Recursively check if the new query can be solved
                cache[query_key] = True
                return True

    cache[query_key] = False
    return False

def run_tests(solver, solver_name):
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
        }
    ]

    print(f"\n=== Running tests for {solver_name} ===")
    for i, case in enumerate(test_cases, 1):
        print(f"\n=== Test Set {i}: {case['description']} ===")
        for j, (query, expected) in enumerate(case["queries"], 1):
            print(f"\nTest {j}: Query = {query}")
            result = solver(case["kb"], query)
            print(f"Result: {result}, Expected: {expected}")
            assert result == expected, f"Test {i}.{j} failed!"
    print(f"\nAll test cases passed for {solver_name}!")

def main():
    # Run tests separately for both versions
    run_tests(solve, "Unoptimized Solve")
    run_tests(solve_opt, "Optimized Solve")

    #TODO: write the main code
    # load input by file
    # process input into chosen format
    # convert input to cnf
    # call solve(kb, query)
    # print result

if __name__ == "__main__":
    main()

