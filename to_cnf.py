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


def parse_tokens(tokens, start=0, end=None):
    """
    Parse a list of tokens into a syntax tree with modified precedence.
    """
    if end is None:
        end = len(tokens)
    
    if start >= end:
        return None, start
    
    # Handle higher precedence operations first (NOT and parentheses)
    if tokens[start] == "not":
        # Parse just the next term (variable or parenthesized expression)
        next_pos = start + 1
        if next_pos < end:
            if tokens[next_pos] == "(":
                # Handle parenthesized expression
                depth = 1
                pos = next_pos + 1
                while pos < end and depth > 0:
                    if tokens[pos] == "(":
                        depth += 1
                    elif tokens[pos] == ")":
                        depth -= 1
                    pos += 1
                
                if depth > 0:
                    raise ValueError("Unbalanced parentheses")
                
                inner_expr, _ = parse_tokens(tokens, next_pos + 1, pos - 1)
                term = LogicNode("not", left=inner_expr)
                next_pos = pos
            else:
                # Handle single variable
                term = LogicNode("not", left=LogicNode("var", tokens[next_pos]))
                next_pos += 1
            
            # Check if there are operators after the NOT expression
            if next_pos < end and tokens[next_pos] in ["and", "or", "implies", "equiv"]:
                operator = tokens[next_pos]
                right_expr, further_pos = parse_tokens(tokens, next_pos + 1, end)
                return LogicNode(operator, left=term, right=right_expr), further_pos
            
            return term, next_pos
        else:
            raise ValueError("Expected term after 'not'")
    
    # Handle parenthesized expression
    if tokens[start] == "(":
        # Find the matching closing parenthesis
        depth = 1
        pos = start + 1
        while pos < end and depth > 0:
            if tokens[pos] == "(":
                depth += 1
            elif tokens[pos] == ")":
                depth -= 1
            pos += 1
        
        if depth > 0:
            raise ValueError("Unbalanced parentheses")
        
        # Parse the expression inside parentheses
        inner_end = pos - 1  # Position of the closing parenthesis
        if inner_end == start + 1:  # Empty parentheses
            return None, pos
        
        inner_expr, _ = parse_tokens(tokens, start + 1, inner_end)
        
        # Check for operators after parentheses
        if pos < end and tokens[pos] in ["and", "or", "implies", "equiv"]:
            operator = tokens[pos]
            right_expr, next_pos = parse_tokens(tokens, pos + 1, end)
            return LogicNode(operator, left=inner_expr, right=right_expr), next_pos
        
        return inner_expr, pos
    
    # Handle simple variable
    if tokens[start] not in ["and", "or", "implies", "equiv", ")", "("]:
        term = LogicNode("var", tokens[start])
        next_pos = start + 1
        
        # Check if there are operators after the variable
        if next_pos < end and tokens[next_pos] in ["and", "or", "implies", "equiv"]:
            operator = tokens[next_pos]
            right_expr, further_pos = parse_tokens(tokens, next_pos + 1, end)
            return LogicNode(operator, left=term, right=right_expr), further_pos
        
        return term, next_pos
    
    # If we reach here, something is wrong with the input
    raise ValueError(f"Unexpected token: {tokens[start]}")


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
        clause = []
        
        # Helper function to collect literals in an OR expression
        def collect_or_literals(or_node, clause_list):
            if or_node.type == 'var':
                clause_list.append(or_node.value)
            elif or_node.type == 'not' and or_node.left.type == 'var':
                clause_list.append(f"¬{or_node.left.value}")
            elif or_node.type == 'or':
                collect_or_literals(or_node.left, clause_list)
                collect_or_literals(or_node.right, clause_list)
            else:
                # This shouldn't happen in a well-formed CNF
                sub_result = node_to_list_of_lists(or_node)
                for sub_clause in sub_result:
                    clause_list.extend(sub_clause)
        
        collect_or_literals(node, clause)
        result.append(clause)
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
    return node_to_list_of_lists(cnf_node)


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
        "(p or q) and (not q or r)"
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