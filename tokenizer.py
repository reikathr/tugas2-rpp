from logic_node import LogicNode

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