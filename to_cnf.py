class LogicNode:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type  # 'var', 'not', 'and', 'or', 'implies', 'equiv'
        self.value = value  # for variables
        self.left = left
        self.right = right
    
    def __str__(self):
        if self.type == 'var':
            return self.value
        elif self.type == 'not':
            return f"¬({self.left})"
        elif self.type == 'and':
            return f"({self.left} ∧ {self.right})"
        elif self.type == 'or':
            return f"({self.left} ∨ {self.right})"
        elif self.type == 'implies':
            return f"({self.left} → {self.right})"
        elif self.type == 'equiv':
            return f"({self.left} ↔ {self.right})"


def tokenize(formula):
    """Tokenize a logical formula into a list of tokens."""
    # Add spaces around parentheses
    formula = formula.replace("(", " ( ")
    formula = formula.replace(")", " ) ")
    
    # Split by spaces and filter out empty tokens
    tokens = [token for token in formula.split() if token]
    # print(tokens) # for debugging
    
    return tokens

def parse_tokens(tokens, pos=0):
    """
    Parse tokens with proper operator precedence:
    1. Parentheses (highest)
    2. NOT
    3. AND
    4. OR
    5. IMPLIES
    6. EQUIV (lowest)
    """
    if pos >= len(tokens):
        return None, pos
    
    # Start with the lowest precedence: parse_equiv
    return parse_equiv(tokens, pos)

def parse_equiv(tokens, pos):
    """Parse equivalence (lowest precedence)"""
    left, pos = parse_implies(tokens, pos)
    
    while pos < len(tokens) and tokens[pos] == "equiv":
        pos += 1
        right, pos = parse_implies(tokens, pos)
        left = LogicNode("equiv", left=left, right=right)
    
    return left, pos

def parse_implies(tokens, pos):
    """Parse implication (second lowest precedence)"""
    left, pos = parse_or(tokens, pos)
    
    while pos < len(tokens) and tokens[pos] == "implies":
        pos += 1
        right, pos = parse_or(tokens, pos)
        left = LogicNode("implies", left=left, right=right)
    
    return left, pos

def parse_or(tokens, pos):
    """Parse disjunction"""
    left, pos = parse_and(tokens, pos)
    
    while pos < len(tokens) and tokens[pos] == "or":
        pos += 1
        right, pos = parse_and(tokens, pos)
        left = LogicNode("or", left=left, right=right)
    
    return left, pos

def parse_and(tokens, pos):
    """Parse conjunction"""
    left, pos = parse_not(tokens, pos)
    
    while pos < len(tokens) and tokens[pos] == "and":
        pos += 1
        right, pos = parse_not(tokens, pos)
        left = LogicNode("and", left=left, right=right)
    
    return left, pos

def parse_not(tokens, pos):
    """Parse negation"""
    if pos < len(tokens) and tokens[pos] == "not":
        pos += 1
        expr, pos = parse_not(tokens, pos)  # NOT binds to the term immediately following it
        return LogicNode("not", left=expr), pos
    
    return parse_term(tokens, pos)

def parse_term(tokens, pos):
    """Parse terms (variables or parenthesized expressions)"""
    if pos >= len(tokens):
        raise ValueError("Unexpected end of input")
    
    token = tokens[pos]
    
    # Handle parenthesized expressions
    if token == "(":
        pos += 1
        expr, pos = parse_equiv(tokens, pos)  # Start from the lowest precedence inside parentheses
        
        if pos >= len(tokens) or tokens[pos] != ")":
            raise ValueError("Expected closing parenthesis")
        
        return expr, pos + 1
    
    # Handle variables
    if token not in ["and", "or", "implies", "equiv", "not", "(", ")"]:
        return LogicNode("var", token), pos + 1
    
    raise ValueError(f"Unexpected token: {token}")

def parse_formula(formula):
    """
    Parse a propositional logic formula into a syntax tree with proper operator precedence.
    """
    tokens = tokenize(formula)
    tree, pos = parse_tokens(tokens)
    
    if pos < len(tokens):
        raise ValueError(f"Unexpected tokens after parsing: {tokens[pos:]}")
    
    return tree


def parse_formula(formula):
    """
    Parse a propositional logic formula into a syntax tree.
    """
    tokens = tokenize(formula)
    tree, _ = parse_tokens(tokens)
    return tree


def eliminate_implications(node):
    """
    Step 1: Eliminate implications and equivalences
    P → Q becomes ¬P ∨ Q
    P ↔ Q becomes (¬P ∨ Q) ∧ (¬Q ∨ P)
    """
    if node is None:
        return None
    
    if node.type == 'var':
        return node
    
    if node.type == 'not':
        return LogicNode('not', left=eliminate_implications(node.left))
    
    if node.type == 'and' or node.type == 'or':
        return LogicNode(node.type, 
                         left=eliminate_implications(node.left),
                         right=eliminate_implications(node.right))
    
    if node.type == 'implies':
        # P → Q becomes ¬P ∨ Q
        not_p = LogicNode('not', left=eliminate_implications(node.left))
        q = eliminate_implications(node.right)
        return LogicNode('or', left=not_p, right=q)
    
    if node.type == 'equiv':
        # P ↔ Q becomes (P → Q) ∧ (Q → P)
        p = eliminate_implications(node.left)
        q = eliminate_implications(node.right)
        
        # (P → Q) becomes (¬P ∨ Q)
        not_p = LogicNode('not', left=p)
        p_implies_q = LogicNode('or', left=not_p, right=q)
        
        # (Q → P) becomes (¬Q ∨ P)
        not_q = LogicNode('not', left=q)
        q_implies_p = LogicNode('or', left=not_q, right=p)
        
        return LogicNode('and', left=p_implies_q, right=q_implies_p)
    
    return node


def push_negation_inward(node):
    """
    Step 2: Push negations inward using De Morgan's laws
    ¬(P ∧ Q) becomes ¬P ∨ ¬Q
    ¬(P ∨ Q) becomes ¬P ∧ ¬Q
    ¬¬P becomes P
    """
    if node is None:
        return None
    
    if node.type == 'var':
        return node
    
    if node.type == 'not':
        if node.left.type == 'not':
            # Double negation: ¬¬P becomes P
            return push_negation_inward(node.left.left)
        
        if node.left.type == 'and':
            # De Morgan's law: ¬(P ∧ Q) becomes ¬P ∨ ¬Q
            not_p = LogicNode('not', left=node.left.left)
            not_q = LogicNode('not', left=node.left.right)
            return LogicNode('or', 
                             left=push_negation_inward(not_p),
                             right=push_negation_inward(not_q))
        
        if node.left.type == 'or':
            # De Morgan's law: ¬(P ∨ Q) becomes ¬P ∧ ¬Q
            not_p = LogicNode('not', left=node.left.left)
            not_q = LogicNode('not', left=node.left.right)
            return LogicNode('and', 
                             left=push_negation_inward(not_p),
                             right=push_negation_inward(not_q))
        
        # If none of the above, just push the negation down
        return LogicNode('not', left=push_negation_inward(node.left))
    
    if node.type == 'and' or node.type == 'or':
        return LogicNode(node.type, 
                         left=push_negation_inward(node.left),
                         right=push_negation_inward(node.right))
    
    return node


def distribute_or_over_and(node):
    """
    Step 3: Distribute OR over AND
    P ∨ (Q ∧ R) becomes (P ∨ Q) ∧ (P ∨ R)
    (P ∧ Q) ∨ R becomes (P ∨ R) ∧ (Q ∨ R)
    """
    if node is None:
        return None
    
    if node.type == 'var' or node.type == 'not' and node.left.type == 'var':
        return node
    
    if node.type == 'not':
        return LogicNode('not', left=distribute_or_over_and(node.left))
    
    if node.type == 'and':
        return LogicNode('and', 
                         left=distribute_or_over_and(node.left),
                         right=distribute_or_over_and(node.right))
    
    if node.type == 'or':
        left = distribute_or_over_and(node.left)
        right = distribute_or_over_and(node.right)
        
        # Check if we need to distribute
        if left.type == 'and':
            # (P ∧ Q) ∨ R becomes (P ∨ R) ∧ (Q ∨ R)
            p_or_r = LogicNode('or', left=left.left, right=right)
            q_or_r = LogicNode('or', left=left.right, right=right)
            return LogicNode('and', 
                             left=distribute_or_over_and(p_or_r),
                             right=distribute_or_over_and(q_or_r))
        
        if right.type == 'and':
            # P ∨ (Q ∧ R) becomes (P ∨ Q) ∧ (P ∨ R)
            p_or_q = LogicNode('or', left=left, right=right.left)
            p_or_r = LogicNode('or', left=left, right=right.right)
            return LogicNode('and', 
                             left=distribute_or_over_and(p_or_q),
                             right=distribute_or_over_and(p_or_r))
        
        return LogicNode('or', left=left, right=right)
    
    return node


def convert_to_cnf(formula):
    """
    Convert a propositional logic formula to Conjunctive Normal Form (CNF)
    """
    # Step 0: Parse the formula
    parse_tree = parse_formula(formula)
    
    # Step 1: Eliminate implications and equivalences
    no_implications = eliminate_implications(parse_tree)
    
    # Step 2: Push negations inward
    negations_inward = push_negation_inward(no_implications)
    
    # Step 3: Distribute OR over AND
    cnf = distribute_or_over_and(negations_inward)
    
    return cnf


def node_to_list_of_lists(node):
    """
    Convert a CNF node to a list of lists representation
    [[p, q]] means p or q
    [[p], [q, r]] means p and (q or r)
    """
    if node is None:
        return []
    
    if node.type == 'var':
        return [[node.value]]
    
    if node.type == 'not' and node.left.type == 'var':
        # Negated variable, represent as "¬p"
        return [[f"¬{node.left.value}"]]
    
    if node.type == 'or':
        # For OR, we combine literals into a single clause
        result = []
        clause = set()  # Use a set to remove duplicates

        # Helper function to collect literals in an OR expression
        def collect_or_literals(or_node, clause_set):
            if or_node.type == 'var':
                clause_set.add(or_node.value)
            elif or_node.type == 'not' and or_node.left.type == 'var':
                clause_set.add(f"¬{or_node.left.value}")
            elif or_node.type == 'or':
                collect_or_literals(or_node.left, clause_set)
                collect_or_literals(or_node.right, clause_set)
            else:
                # This shouldn't happen in a well-formed CNF
                sub_result = node_to_list_of_lists(or_node)
                for sub_clause in sub_result:
                    clause_set.update(sub_clause)

        collect_or_literals(node, clause)
        result.append(list(set(clause)))  # Remove duplicates by converting to a set and back to a list

        return result
    
    if node.type == 'and':
        # For AND, we combine clauses from left and right
        left_clauses = node_to_list_of_lists(node.left)
        right_clauses = node_to_list_of_lists(node.right)
        return left_clauses + right_clauses
    
    return [[str(node)]]


def convert_to_cnf_list(formula):
    """
    Convert a propositional logic formula to a list of lists representation of CNF
    """
    cnf_node = convert_to_cnf(formula)
    cnf_list = node_to_list_of_lists(cnf_node)
    cnf_list = [clause for clause in cnf_list if not is_tautology(clause)]
    return cnf_list

def is_tautology(query):
    """
    Detects tautologies from the query.
    Example: If 'S07' and '¬S07' exist, the query is a tautology.
    
    :param query: List of literals.
    :return: boolean
    """
    cleaned_query = set(query)  # Convert list to set for efficient lookups

    for lit in list(cleaned_query):  # Iterate over a copy of the set
        if lit.startswith("¬"):
            pos_lit = lit[1:]  # Get the positive version
            if pos_lit in cleaned_query:
                print(f"Tautology detected: {lit} or {pos_lit}.")
                return True

        elif f"¬{lit}" in cleaned_query:
            print(f"Tautology detected: {lit} or ¬{lit}.")
            return True

    return False


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

def main():
    input_path = "logic_expressions.txt"
    output_path = "cnf_expressions.txt"
    test_run()

    with open(input_path, "r", encoding="utf-8") as infile, \
         open(output_path, "w", encoding="utf-8") as outfile:

        for line in infile:
            formula = line.strip()
            if not formula:
                continue  # skip blank lines

            outfile.write(f"Original: {formula}\n")
            cnf_list = convert_to_cnf_list(formula)
            outfile.write(f"CNF as list of lists: {cnf_list}\n")

            # Print human-readable CNF
            if len(cnf_list) == 1:
                meaning = ' OR '.join(cnf_list[0])
            else:
                clauses = []
                for clause in cnf_list:
                    if len(clause) == 1:
                        clauses.append(clause[0])
                    else:
                        clauses.append(f"({' OR '.join(clause)})")
                meaning = ' AND '.join(clauses)

            outfile.write(f"Meaning: {meaning}\n\n")

    print(f"CNF transformation complete! Output saved to: {output_path}")

if __name__ == "__main__":
    main()