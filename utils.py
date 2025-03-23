import re

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

def convert_to_logical_format(file_path):
    """
    Converts a rule file into a logical format using ['and', 'or', 'implies', 'equiv'],
    ensuring correct logical precedence with parentheses.
    
    :param file_path: Path to the inference rules file.
    :return: List of formatted logical expressions.
    """
    logical_expressions = []
    
    # Define mappings for connectives
    CONNECTIVES = {
        "AND": "and",
        "OR": "or",
        "THEN": "implies"
    }

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            # Extract parts
            parts = re.split(r'\s+', line)
            if "THEN" not in parts:
                continue  # Skip malformed lines

            then_index = parts.index("THEN")
            conditions = parts[:then_index]  # Everything before THEN
            conclusion = parts[then_index + 1]  # The conclusion after THEN

            # Process conditions with correct precedence
            condition_stack = []
            i = 0
            while i < len(conditions):
                token = conditions[i]

                if token == "NOT":  # Handle negation
                    i += 1
                    condition_stack.append(f"not {conditions[i]}")
                elif token in CONNECTIVES:
                    condition_stack.append(CONNECTIVES[token])
                else:
                    condition_stack.append(token)

                i += 1

            # Ensure OR conditions are grouped with parentheses
            if "or" in condition_stack:
                grouped_conditions = []
                current_or_group = []

                for term in condition_stack:
                    if term == "or":
                        current_or_group.append(term)
                    elif term == "and" and current_or_group:
                        grouped_conditions.append(f"({' '.join(current_or_group)})")
                        grouped_conditions.append("and")
                        current_or_group = []
                    else:
                        current_or_group.append(term)

                if current_or_group:
                    grouped_conditions.append(f"({' '.join(current_or_group)})")
                final_conditions = " ".join(grouped_conditions)
            else:
                final_conditions = " ".join(condition_stack)

            # Build the final logical expression
            formatted_expression = f"({final_conditions}) implies {conclusion}"
            logical_expressions.append(formatted_expression)

    return logical_expressions