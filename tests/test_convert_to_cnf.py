from convert_to_cnf import convert_to_cnf_list

def test_run():
    # Test run
    test_formulas = [
        "p implies q",
        "p equiv q",
        "not (p and q)",
        "not p or q",
        "p or (q and r)",
        "(p implies q) and (q implies r)",
        "not p or not q",
        "(p or q) and (not q or r)",
        "not p or p",
        "S02 or S03 and S04 implies L02"
    ]
    
    for formula in test_formulas:
        print(f"Original: {formula}")
        cnf_list = convert_to_cnf_list(formula)
        print(f"CNF as list of lists: {cnf_list}")
        
        # Print the meaning
        if len(cnf_list) == 1:
            print(f"Meaning: {' OR '.join(cnf_list[0])}")
        else:
            clauses = []
            for clause in cnf_list:
                if len(clause) == 1:
                    clauses.append(clause[0])
                else:
                    clauses.append(f"({' OR '.join(clause)})")
            print(f"Meaning: {' AND '.join(clauses)}")
        print()

if __name__ == "__main__":
    test_run()