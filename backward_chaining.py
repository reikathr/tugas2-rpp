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

def solve(kb, query, visited=None):
    """
    SLD resolution using backward chaining with contradiction detection.
    """
    if visited is None:
        visited = set()

    query = is_tautology(query)
    
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

            new_query = is_tautology(new_query)  # Clean new query

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

    query = is_tautology(query)
    
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

            new_query = is_tautology(new_query)

            print(f"Resolving {q} using clause {clause} gives new query: {new_query}")

            if solve_opt(kb, new_query, cache, visited):  # Recursive call with cycle detection
                cache[query_key] = True
                return True

    cache[query_key] = False
    return False