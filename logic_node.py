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