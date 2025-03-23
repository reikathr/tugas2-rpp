from utils import convert_to_logical_format
from backward_chaining import solve, solve_opt
from convert_to_cnf import convert_to_cnf_list
import yaml, os, time, psutil, tracemalloc

def run_test_suite(kb, test_cases, solver, solver_name, log, file_name):
    """Run a suite of tests with given solver and test cases"""
    print(f"\n=== Running Tests with {solver_name} ===")
    log[solver_name] = {
        'total_tests': len(test_cases),
        'passed_tests': 0,
        'test_details': [],
        'performance_metrics': {
            'total_time_ms': 0,
            'avg_time_ms': 0,
            'total_memory_kb': 0,
            'avg_memory_kb': 0,
            'peak_memory_kb': 0
        }
    }

    # Start memory tracking
    tracemalloc.start()
    total_time = 0
    total_memory = 0
    peak_memory = 0

    for conditions, expected in test_cases:
        print(f"\nTesting conditions: {conditions}")

        # Create a local KB for each test
        test_kb = kb.copy()
        for fact in conditions:
            test_kb.append([fact])

        # Execute test
        start_time = time.perf_counter()
        query = [expected]
        result = solver(test_kb, query)
        end_time = time.perf_counter()

        # Calculate metrics
        execution_time = (end_time - start_time) * 1000
        current_memory, current_peak = tracemalloc.get_traced_memory()
        peak_memory = max(current_memory, current_peak)

        current_memory_mb = current_memory / 1024
        total_time += execution_time
        total_memory += current_memory_mb
        
        if result == True:
            log[solver_name]['passed_tests'] += 1

        print(f"Query: {query}, Result: {result}, Expected: {expected}")

    # Update solver performance stats
    num_tests = len(test_cases)
    log[solver_name]['performance_metrics'].update({
        'total_time_ms': total_time,
        'avg_time_ms': total_time / num_tests,
        'total_memory_kb': round(total_memory, 2),
        'avg_memory_kb': round(total_memory / num_tests, 2),
        'peak_memory_kb': round(peak_memory / 1024, 2)
    })

    tracemalloc.stop()
    print(f"\nAll tests completed for {solver_name}!")

def main():
    log = {}
    # Step 1: Load input by file
    data_dir = "data"
    covid_files = [f for f in os.listdir(data_dir) if f.startswith('covid') and f.endswith('.txt')]
    for file_name in covid_files:
        file_path = os.path.join(data_dir, file_name)
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

    test_cases_2 = [
        (["S02"], "L01"),  # 18-59 years old → Eligible
        (["S03"], "L01"),  # Over 59 years old → Eligible
        (["S01"], "L02"),  # Under 18 → Not Eligible
        (["S04"], "L02"),  # Severe allergy → Not Eligible
        (["S10"], "L03"),  # Chronic conditions (e.g., DM, heart disease) → Delayed
        (["S12"], "L02"),  # Pregnant → Not Eligible
        (["S14"], "L02"),  # Covid survivor → Not Eligible
        (["S13"], "L03"),  # Recent vaccination → Delayed
        (["S05", "S12"], "L02"),  # Autoimmune disease + Pregnant → Not Eligible
        (["S13", "S14"], "L03"),  # Recent vaccination + Covid survivor → Delayed
    ]

    # Step 5: Run both test suites with both solvers
    for solver_name, solver in [("Unoptimized Solve", solve), ("Optimized Solve", solve_opt)]:
        run_test_suite(kb, test_cases, solver, f"{solver_name}_Dataset_1", log, file_name)
        run_test_suite(kb, test_cases_2, solver, f"{solver_name}_Dataset_2", log, file_name)

    # Step 6: Save results
    os.makedirs('output', exist_ok=True)
    with open(f'output/results_log.yml', 'w') as f:
        yaml.dump(log, f, default_flow_style=False)

if __name__ == "__main__":
    main()