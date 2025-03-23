import re
from to_cnf import convert_to_cnf_list

def remove_contradictions(query):
    """
    Removes contradictory literals from the query.
    Example: If 'S07' and '¬S07' exist, both are removed.
    
    :param query: List of literals.
    :return: Cleaned query (list), or [] if a contradiction is found.
    """
    cleaned_query = set(query)  # Convert list to set for efficient lookups

    for lit in list(cleaned_query):  # Iterate over a copy of the set
        if lit.startswith("¬"):
            pos_lit = lit[1:]  # Get the positive version
            if pos_lit in cleaned_query:
                print(f"Contradiction detected: {lit} and {pos_lit}. Removing both.")
                cleaned_query.remove(lit)
                cleaned_query.remove(pos_lit)

        elif f"¬{lit}" in cleaned_query:
            print(f"Contradiction detected: {lit} and ¬{lit}. Removing both.")
            cleaned_query.remove(lit)
            cleaned_query.remove(f"¬{lit}")

    return list(cleaned_query)  # Convert back to a list


def solve(kb, query, visited=None):
    """
    SLD resolution using backward chaining with contradiction detection.
    """
    if visited is None:
        visited = set()

    # Remove contradictions
    query = remove_contradictions(query)
    
    if not query:
        return True  # If contradiction removed all, assume success.

    query_key = tuple(sorted(query))
    if query_key in visited:
        print(f"Cycle detected for query: {query}")
        return False  # Prevent infinite loops.

    visited.add(query_key)  # Mark query as visited.

    q = query[0]  # Take the first goal
    rest_query = query[1:]  # Remaining goals

    for clause in kb:
        if q in clause:
            new_query = list(set([
                (lit.replace('¬', '') if '¬' in lit else '¬' + lit) for lit in clause if lit != q
            ] + rest_query))

            new_query = remove_contradictions(new_query)  # Clean new query

            print(f"New query: {new_query}")

            if solve(kb, new_query, visited):
                return True

    return False

def solve_opt(kb, query, cache=None, visited=None):
    """
    SLD resolution using backward chaining for CNF clauses with caching and cycle detection.
    """
    if cache is None:
        cache = {}
    if visited is None:
        visited = set()

    # Convert query to a canonical tuple representation
    query_key = tuple(sorted(query))
    
    if query_key in cache:
        return cache[query_key]  # Use cached result

    if query_key in visited:
        print(f"Cycle detected for query: {query}")
        return False  # Prevent infinite loops

    visited.add(query_key)  # Mark query as visited

    # Remove contradictions
    query = remove_contradictions(query)
    
    if not query:
        cache[query_key] = True
        return True

    q = query[0]         
    rest_query = query[1:]

    # Try to resolve q using KB
    for clause in kb:
        if q in clause:
            new_query = list(set([
                (lit.replace('¬', '') if '¬' in lit else '¬' + lit) for lit in clause if lit != q
            ] + rest_query))

            new_query = remove_contradictions(new_query)

            print(f"Resolving {q} using clause {clause} gives new query: {new_query}")

            if solve_opt(kb, new_query, cache, visited):  # Recursive call with cycle detection
                cache[query_key] = True
                return True

    cache[query_key] = False
    return False


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
    file_path = "covid_extended_rules_1.txt"  # Ensure the correct file path

    # Step 2: Process input into logical expressions
    logical_expressions = convert_to_logical_format(file_path)

    # Step 3: Convert expressions to CNF
    kb = []
    for expression in logical_expressions:
        cnf_clause = convert_to_cnf_list(expression)  # Convert each logical rule to CNF
        kb.extend(cnf_clause)  # Add CNF clauses to KB

    # Step 4: Define test cases based on the **5 simplified rules**
    test_cases = [
        (["S02"], "L01"),  # 18-59 years old → Eligible
        (["S03"], "L01"),  # Over 59 years old → Eligible
        (["S01"], "L02"),  # Under 18 → Not Eligible
        (["S02", "S04"], "L02"),  # Severe allergy → Not Eligible
        (["S02", "S10"], "L03"),  # Chronic conditions (e.g., DM, heart disease) → Delayed
        (["S10"], "L03"),  # Chronic conditions (e.g., DM, heart disease) → Delayed
    ]

    # Step 4: Define test cases based on the **simplified 10 rules**
    # test_cases = [
    #     (["S02"], "L01"),  # 18-59 years old → Eligible
    #     (["S03"], "L01"),  # Over 59 years old → Eligible
    #     (["S01"], "L02"),  # Under 18 → Not Eligible
    #     (["S04"], "L02"),  # Severe allergy → Not Eligible
    #     (["S10"], "L03"),  # Chronic conditions (e.g., DM, heart disease) → Delayed
    #     (["S12"], "L02"),  # Pregnant → Not Eligible
    #     (["S14"], "L02"),  # Covid survivor → Not Eligible
    #     (["S13"], "L03"),  # Recent vaccination → Delayed
    #     (["S05", "S12"], "L02"),  # Autoimmune disease + Pregnant → Not Eligible
    #     (["S13", "S14"], "L03"),  # Recent vaccination + Covid survivor → Delayed
    # ]

    # Step 5: Run tests with both `solve` and `solve_opt`
    for solver_name, solver in [("Unoptimized Solve", solve), ("Optimized Solve", solve_opt)]:
        print(f"\n=== Running Tests with {solver_name} ===")

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

            # Step 5.3: Query reasoning engine
            query = [expected]
            result = solver(test_kb, query)

            # Step 5.4: Print results and validate
            print(f"Query: {query}, Result: {result}, Expected: {expected}")
            assert result == True, f"Test failed for conditions: {conditions}"

        print(f"\nAll tests passed for {solver_name}!")

if __name__ == "__main__":
    main()
    # Run tests separately for both versions
    # run_tests(solve, "Unoptimized Solve")
    # run_tests(solve_opt, "Optimized Solve")

