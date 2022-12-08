import ast

LabeledInstruction = tuple[str, str]

class FunctionLevelProgram(ast.NodeVisitor):
    """We supports assignments and input/print calls"""
    
    def __init__(self, numOfArgs, node) -> None:
        super().__init__()
        self.__instructions = list()
        self.__should_save = True
        self.__current_variable = None
        self.__elem_id = 0
        self.root = node
        self.args = node.args.args
        self.numOfArgs = numOfArgs
        self.localVariables = set()
        self.constantValues = []
        self.allocateMemory = []

        self.store = True
        

    def finalize(self):
        for arguement in self.args:
            self.localVariables.add(arguement.arg)
        if len(self.localVariables) != self.numOfArgs:
            self.__instructions.append((None, 'ADDSP '+ str((len(self.localVariables)-self.numOfArgs)*2) + ',i'))
            self.__instructions.append((None,'RET'))
            self.__instructions.append((self.root.name, 'SUBSP '+ str((len(self.localVariables)-self.numOfArgs)*2) + ',i'))
            for variable in self.localVariables:
                variableMatch = False
                for Param in self.args:
                    if variable == Param.arg:
                        variableMatch = True
                        break
                if not variableMatch:
                    self.allocateMemory.append(variable)

            
        else:
            self.__instructions.append((None,'RET'))
            self.__instructions.append((self.root.name, 'NOP1'))
        
        
        
        return self.__instructions

    ####
    ## Handling Assignments (variable = ...)
    ####

    def visit_Assign(self, node):
        # remembering the name of the target
        if len(node.targets[0].id)<=8:
            self.__current_variable = node.targets[0].id
        else:
            self.__current_variable = node.targets[0].id[:8]
        # visiting the left part, now knowing where to store the result
        self.visit(node.value)
        if self.__should_save:
            if self.store: 
                self.__record_instruction(f'STWA m{self.__current_variable},s')
                self.localVariables.add(self.__current_variable)
            self.store = True
        else:
            self.__should_save = True
        self.__current_variable = None

    def visit_Constant(self, node):
        passThrough = True
        for i in self.constantValues:
            if i[0]==self.__current_variable:
                passThrough = False
                self.__record_instruction(f'LDWA {node.value},i')
                break
        if passThrough:
            self.constantValues.append([self.__current_variable, node.value])
            self.store = False
    
    def visit_Name(self, node):
        if not isinstance(self.root.body[-1], ast.Return):

            self.__record_instruction(f'LDWA m{node.id},s')
            self.localVariables.add(node.id)

    def visit_BinOp(self, node):
        self.__access_memory(node.left, 'LDWA')
        if isinstance(node.op, ast.Add):
            self.__access_memory(node.right, 'ADDA')
        elif isinstance(node.op, ast.Sub):
            self.__access_memory(node.right, 'SUBA')
        else:
            raise ValueError(f'Unsupported binary operator: {node.op}')

    def visit_Call(self, node):
        match node.func.id:
            case 'int': 
                # Let's visit whatever is casted into an int
                self.visit(node.args[0])
            case 'input':
                # We are only supporting integers for now
                self.__record_instruction(f'DECI m{self.__current_variable},s')
                self.__should_save = False # DECI already save the value in memory
                self.localVariables.add(self.__current_variable)

            case 'print':
                # We are only supporting integers for now
                self.__record_instruction(f'DECO m{node.args[0].id},s')
            case _:
                pass
            
    ####
    ## Handling While loops (only variable OP variable)
    ####

    def visit_While(self, node):
        loop_id = self.__identify()
        inverted = {
            ast.Lt:  'BRGE', # '<'  in the code means we branch if '>=' 
            ast.LtE: 'BRGT', # '<=' in the code means we branch if '>' 
            ast.Gt:  'BRLE', # '>'  in the code means we branch if '<='
            ast.GtE: 'BRLT', # '>=' in the code means we branch if '<'
        }
        # left part can only be a variable
        self.__access_memory(node.test.left, 'LDWA', label = f'test_{loop_id}')
        # right part can only be a variable
        self.__access_memory(node.test.comparators[0], 'CPWA')
        # Branching is condition is not true (thus, inverted)
        self.__record_instruction(f'{inverted[type(node.test.ops[0])]} end_l_{loop_id}')
        # Visiting the body of the loop
        for contents in node.body:
            self.visit(contents)
        self.__record_instruction(f'BR test_{loop_id}')
        # Sentinel marker for the end of the loop
        self.__record_instruction(f'NOP1', label = f'end_l_{loop_id}')

    ####
    ## Not handling function calls 
    ####

    def visit_FunctionDef(self, node):
        """We do not visit function definitions, they are not top level"""
        for contents in node.body:
            self.visit(contents)
        pass
    ####
    ## Helper functions to 
    ####

    def __record_instruction(self, instruction, label = None):
        self.__instructions.append((label, instruction))

    def __access_memory(self, node, instruction, label = None):
        if isinstance(node, ast.Constant):
            self.__record_instruction(f'{instruction} {node.value},i', label)
        elif node.id[0] == '_' and node.id.strip('_').isupper():
                self.__record_instruction(f'{instruction} {node.id},i', label)
        else:
            self.__record_instruction(f'{instruction} m{node.id},s', label)

    def __identify(self):
        result = self.__elem_id
        self.__elem_id = self.__elem_id + 1
        return result