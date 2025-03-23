from utils import convert_to_logical_format
from backward_chaining import solve, solve_opt
from convert_to_cnf import convert_to_cnf_list
import yaml, os, time, psutil, tracemalloc

def main():
    log = {}
    # Step 1: Load input by file
    data_dir = "data"
    covid_files = [f for f in os.listdir(data_dir) if f.startswith('covid') and f.endswith('.txt')]
    for file_name in covid_files:
        file_path = os.path.join(data_dir, file_name)
        log[file_name] = {
            'solver_stats': {}
        }
        print(f"\n=== Processing file: {file_path} ===")

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
            log[file_name]['solver_stats'][solver_name] = {
                'total_tests': len(test_cases),
                'passed_tests': 0,
                'test_details': [],
                'performance': {
                    'total_time': 0,
                    'peak_memory': 0,
                    'avg_time_per_test': 0
                }
            }

            # Start memory tracking
            tracemalloc.start()
            total_time = 0

            for conditions, expected in test_cases:
                print(f"\nTesting conditions: {conditions}")
                test_details = {
                    'conditions': conditions,
                    'expected': expected,
                    'performance': {}
                }

                # Step 5.1: Create a local KB for each test with facts included
                test_kb = kb.copy()  # Start with general KB
                for fact in conditions:
                    test_kb.append([fact])  # Add each condition as a fact

                # Step 5.2: Print KB before solving
                print("\nFinal KB before solving:")
                for clause in test_kb:
                    print(clause)

                # Step 5.3: Query reasoning engine
                start_time = time.time()
                query = [expected]
                result = solver(test_kb, query)
                end_time = time.time()

                # Calculate metrics
                execution_time = end_time - start_time
                current_memory, peak_memory = tracemalloc.get_traced_memory()

                # Update test details
                test_details.update({
                    'result': result,
                    'passed': result == True,
                    'performance': {
                        'execution_time': execution_time,
                        'memory_used': current_memory / 1024 / 1024  # Convert to MB
                    }
                })

                total_time += execution_time
                log[file_name]['solver_stats'][solver_name]['test_details'].append(test_details)
                
                if result == True:
                    log[file_name]['solver_stats'][solver_name]['passed_tests'] += 1

                # Step 5.4: Print results and validate
                print(f"Query: {query}, Result: {result}, Expected: {expected}")
                assert result == True, f"Test failed for conditions: {conditions}"

            # Update solver performance stats
            log[file_name]['solver_stats'][solver_name]['performance'].update({
                'total_time': total_time,
                'peak_memory': peak_memory / 1024 / 1024,  # Convert to MB
                'avg_time_per_test': total_time / len(test_cases)
            })

            # Stop memory tracking
            tracemalloc.stop()

            print(f"\nAll tests passed for {solver_name}!")

    # Step 6: Save results
    with open(f'output/results_log.yml', 'w') as f:
        yaml.dump(log, f, width=float('inf'))

if __name__ == "__main__":
    main()