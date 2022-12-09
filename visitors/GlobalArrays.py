import ast


class GlobalArrayTranslator(ast.NodeVisitor):

    def __init__(self) -> None:
        super().__init__()
        self.__instructions = list()
        self.__array_index_exists = False
        self.__current_while_id = None

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Subscript):
            self.__array_index_exists = True
        
        if self.__array_index_exists:
            self.__record_instruction('ASLX')
            self.visit(node.value)
            self.__array_index_exists = False
        
    def visit_Call(self, node):
        match node.func.id:
            case 'int': 
                # Let's visit whatever is casted into an int
                self.visit(node.args[0])
            case 'input':
                # We are only supporting integers for now
                self.__record_instruction(f'DECI {self.__current_variable},x')
                self.__should_save = False # DECI already save the value in memory
            case 'print':
                # We are only supporting integers for now
                self.__record_instruction(f'DECO {node.args[0].id},x')
            case _:
                pass

    def visit_BinOp(self, node):
        self.__access_memory(node.left, 'LDWX')
        if isinstance(node.op, ast.Add):
            self.__access_memory(node.right, 'ADDX')
        elif isinstance(node.op, ast.Sub):
            self.__access_memory(node.right, 'SUBX')
        else:
            raise ValueError(f'Unsupported binary operator: {node.op}')

    def visit_While(self, node):
        loop_id = self.__identify()
        self.__current_while_id = loop_id
        inverted = {
            ast.Lt:  'BRGE', # '<'  in the code means we branch if '>=' 
            ast.LtE: 'BRGT', # '<=' in the code means we branch if '>' 
            ast.Gt:  'BRLE', # '>'  in the code means we branch if '<='
            ast.GtE: 'BRLT', # '>=' in the code means we branch if '<'
            ast.NotEq: 'BREQ', # '!=' in the code means we branch if '=='
            ast.Eq: 'BRNE' # '==' in the code means we branch if '!='
        }

        self.__access_memory(node.test.left, 'LDWX', label = f'test_{loop_id}')

        self.__access_memory(node.test.comparators[0], 'CPWX')

        self.__record_instruction(f'{inverted[type(node.test.ops[0])]} end_l_{loop_id}')

        for contents in node.body:
            self.visit(contents)
            
        self.__record_instruction(f'BR test_{loop_id}')

        self.__record_instruction(f'NOP1', label = f'end_l_{loop_id}')

    def visit_If(self, node):
        
        conditional_id = self.__identify()
        
        inverted = {
            ast.Lt:  'BRGE', # '<'  in the code means we branch if '>=' 
            ast.LtE: 'BRGT', # '<=' in the code means we branch if '>' 
            ast.Gt:  'BRLE', # '>'  in the code means we branch if '<='
            ast.GtE: 'BRLT', # '>=' in the code means we branch if '<'
            ast.NotEq: 'BREQ', # '!=' in the code means we branch if '=='
            ast.Eq: 'BRNE' # '==' in the code means we branch if '!='
        }

        self.__access_memory(node.test.left, 'LDWX', label = f'cond_{conditional_id}')
        self.__access_memory(node.test.comparators[0], 'CPWX')

        elseif_exists = False

        for n in node.orelse:
            if isinstance(n, ast.If):
                elseif_exists = True

        if elseif_exists:
            self.__record_instruction(f'{inverted[type(node.test.ops[0])]} cond_{conditional_id + 1}')
        else:
            self.__record_instruction(f'{inverted[type(node.test.ops[0])]} else_{conditional_id}')

        elseif_exists = False

        self.__record_instruction('NOP1', label = f'if_{conditional_id}')
        
        for contents in node.body:
            self.visit(contents)
            if self.__current_while_id != None:
                self.__record_instruction(f'BR test_{self.__current_while_id}')
            
        self.__record_instruction(f'BR end_if_{conditional_id}')
        self.__record_instruction('NOP1', label = f'else_{conditional_id}')
            
        for contents in node.orelse:
            self.visit(contents)
        
        self.__record_instruction(f'NOP1', label=f'end_if_{conditional_id}')
    

    def visit_FunctionDef(self, node):
        pass


    def __record_instruction(self, instruction, label = None):
        self.__instructions.append((label, instruction))

    def __access_memory(self, node, instruction, label = None):
        if isinstance(node, ast.Constant):
            self.__record_instruction(f'{instruction} {node.value},i', label)
        elif node.id[0] == '_' and node.id.strip('_').isupper():
                self.__record_instruction(f'{instruction} {node.id},i', label)
        else:
            self.__record_instruction(f'{instruction} {node.id},x', label)

    def __identify(self):
        result = self.__elem_id
        self.__elem_id = self.__elem_id + 1
        return result