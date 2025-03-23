from utils import is_tautology

def verify_solution(kb, assignment):
    """
    Verifies whether the given assignment satisfies all clauses in the KB.
    """
    for clause in kb:
        clause_satisfied = False
        for literal in clause:
            if literal in assignment and assignment[literal]:
                clause_satisfied = True
                break
        if not clause_satisfied:
            return False  # If any clause is not satisfied, return False
    return True


def solve(kb, query, visited=None, assignment=None):
    """
    SLD resolution using backward chaining with contradiction detection and solution verification.
    """
    if visited is None:
        visited = set()
    if assignment is None:
        assignment = {}

    # Remove contradictions
    query = is_tautology(query)
    
    if not query:
        print(f"Solution verified! Truth assignments: {assignment}")
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

            new_query = is_tautology(new_query)  # Clean new query

            print(f"New query: {new_query}")

            # Mark q as true in assignment
            assignment[q] = True

            if solve(kb, new_query, visited, assignment):
                # After solving, verify if the assignment satisfies KB
                if verify_solution(kb, assignment):
                    print(f"Solution verified! Truth assignments: {assignment}")
                    return True

    return False


def solve_opt(kb, query, cache=None, visited=None, assignment=None):
    """
    Optimized SLD resolution using backward chaining with caching, cycle detection, and solution verification.
    """
    if cache is None:
        cache = {}
    if visited is None:
        visited = set()
    if assignment is None:
        assignment = {}

    # Convert query to a canonical tuple representation
    query_key = tuple(sorted(query))

    if query_key in cache:
        return cache[query_key]  # Use cached result

    if query_key in visited:
        print(f"Cycle detected for query: {query}")
        return False  # Prevent infinite loops

    visited.add(query_key)  # Mark query as visited

    # Remove contradictions
    query = is_tautology(query)

    if not query:
        cache[query_key] = True
        print(f"Solution verified! Truth assignments: {assignment}")
        return True  # If contradiction removed all, assume success.

    q = query[0]
    rest_query = query[1:]

    for clause in kb:
        if q in clause:
            new_query = list(set([
                (lit.replace('¬', '') if '¬' in lit else '¬' + lit) for lit in clause if lit != q
            ] + rest_query))

            new_query = is_tautology(new_query)

            print(f"Resolving {q} using clause {clause} gives new query: {new_query}")

            # Mark q as true in assignment
            assignment[q] = True

            if solve_opt(kb, new_query, cache, visited, assignment):
                # After solving, verify if the assignment satisfies KB
                if verify_solution(kb, assignment):
                    cache[query_key] = True
                    print(f"Solution verified! Truth assignments: {assignment}")
                    return True

    cache[query_key] = False
    return False