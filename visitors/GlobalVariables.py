import ast

class GlobalVariableExtraction(ast.NodeVisitor):
    """ 
        We extract all the left hand side of the global (top-level) assignments
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.results = set()
        self.assignAtInitialization = []

    def visit_Assign(self, node):
        if len(node.targets) != 1:
            raise ValueError("Only unary assignments are supported")
        if len(node.targets[0].id)<=8:
            self.results.add(node.targets[0].id)
        else:
            self.results.add(node.targets[0].id[:8])  


    def visit_FunctionDef(self, node):
        """We do not visit function definitions, they are not global by definition"""
        pass
   