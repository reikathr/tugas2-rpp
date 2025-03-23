import re
from to_cnf import convert_to_cnf_list

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

import re

def convert_to_logical_format(file_path):
    """
    Converts a rule file into a logical format using ['and', 'or', 'implies', 'equiv'],
    ensuring correct logical precedence with parentheses.
    
    :param file_path: Path to the inference rules file.
    :return: List of formatted logical expressions.
    """
    logical_expressions = []
    
    # Define mappings for connectives
    CONNECTIVES = {
        "AND": "and",
        "OR": "or",
        "THEN": "implies"
    }

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            # Extract parts
            parts = re.split(r'\s+', line)
            if "THEN" not in parts:
                continue  # Skip malformed lines

            then_index = parts.index("THEN")
            conditions = parts[:then_index]  # Everything before THEN
            conclusion = parts[then_index + 1]  # The conclusion after THEN

            # Process conditions with correct precedence
            condition_stack = []
            i = 0
            while i < len(conditions):
                token = conditions[i]

                if token == "NOT":  # Handle negation
                    i += 1
                    condition_stack.append(f"not {conditions[i]}")
                elif token in CONNECTIVES:
                    condition_stack.append(CONNECTIVES[token])
                else:
                    condition_stack.append(token)

                i += 1

            # Ensure OR conditions are grouped with parentheses
            if "or" in condition_stack:
                grouped_conditions = []
                current_or_group = []

                for term in condition_stack:
                    if term == "or":
                        current_or_group.append(term)
                    elif term == "and" and current_or_group:
                        grouped_conditions.append(f"({' '.join(current_or_group)})")
                        grouped_conditions.append("and")
                        current_or_group = []
                    else:
                        current_or_group.append(term)

                if current_or_group:
                    grouped_conditions.append(f"({' '.join(current_or_group)})")
                final_conditions = " ".join(grouped_conditions)
            else:
                final_conditions = " ".join(condition_stack)

            # Build the final logical expression
            formatted_expression = f"({final_conditions}) implies {conclusion}"
            logical_expressions.append(formatted_expression)

    return logical_expressions

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
    # Step 1: Load input by file
    file_path = "covidinferencerules.txt"  # Ensure the correct file path

    # Step 2: Process input into logical expressions
    logical_expressions = convert_to_logical_format(file_path)

    # Step 3: Convert expressions to CNF
    kb = []
    for expression in logical_expressions:
        cnf_clause = convert_to_cnf_list(expression)  # Convert each logical rule to CNF
        kb.extend(cnf_clause)  # Add CNF clauses to KB

    # Step 4: Define test cases with patient conditions
    test_cases = [
        (["S02"], "L01"),  # 18-59 years old → Eligible for vaccine
        (["S04"], "L02"),  # Severe allergic reaction → Not eligible
        (["S12"], "L03"),  # Pregnant → Delayed consultation
        (["S07", "S09"], "L03"),  # Blood cancer + Chemotherapy → Delayed
        (["S14"], "L03"),  # Covid survivor → Delayed
        (["S03", "S11"], "L03"),  # Chronic conditions (DM, heart disease, kidney failure) → Delayed
    ]

    # Step 5: Run tests
    for conditions, expected in test_cases:
        print(f"\nTesting conditions: {conditions}")

        # Step 5.1: Create a local KB for each test with facts included
        test_kb = kb.copy()  # Start with general KB
        for fact in conditions:
            test_kb.append([fact])  # Add each condition as a fact

        # Step 5.2: Print KB before solving
        print("\nFinal KB before solving:")
        for clause in test_kb:
            print(clause)

        # Step 5.3: Query reasoning engine with recursion limit
        query = [expected]
        try:
            result = solve(test_kb, query)  # Ensure solve() has termination conditions
        except RecursionError:
            print(f"Error: Recursion limit exceeded for query: {query}")
            result = False

        # Step 5.4: Print results and validate
        print(f"Query: {query}, Result: {result}, Expected: {expected}")
        assert result == True, f"Test failed for conditions: {conditions}"

    print("\nAll tests passed!")

if __name__ == "__main__":
    main()
    # Run tests separately for both versions
    # run_tests(solve, "Unoptimized Solve")
    # run_tests(solve_opt, "Optimized Solve")

