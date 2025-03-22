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
            new_query = [lit for lit in clause if lit != q] + rest_query
            if solve(kb, new_query):  # Recursively check if the new query can be solved
                return True

    return False  # If no resolution leads to success, return False


def main():
    #TODO: write the main code
    # load input by file
    # process input into chosen format
    # convert input to cnf
    # call solve(kb, query)
    # print result
    pass