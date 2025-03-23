from utils import convert_to_logical_format
from backward_chaining import solve, solve_opt
from convert_to_cnf import convert_to_cnf_list

def main():
    # Step 1: Load input by file
    file_path = "data/covid_extended_rules_1.txt"  # Ensure the correct file path

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