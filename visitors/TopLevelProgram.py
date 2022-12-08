import ast
from visitors.FunctionLevelProgram import FunctionLevelProgram

LabeledInstruction = tuple[str, str]

class TopLevelProgram(ast.NodeVisitor):
    """We supports assignments and input/print calls"""
    
    def __init__(self, entry_point) -> None:
        super().__init__()
        self.__instructions = list()
        self.__record_instruction('NOP1', label=entry_point) #label.EQUATE entry_point
        self.__should_save = True
        self.__current_variable = None
        self.__elem_id = 0
        self.constantValues = []
        self.functionParameters = []
        self.functionInstructions = []
        self.numOfArgs = 0
        self.store = True
        self.finalInstructions = list()
        

    def finalize(self):

        if self.numOfArgs != 0:
            self.__record_instruction('ADDSP '+ str(self.numOfArgs*2) + ',i')

        self.__instructions.append((None, '.END'))
        for eachFunction in self.functionInstructions:
            self.finalInstructions.append(eachFunction[-1])
            for eachInstruction in eachFunction:
                self.finalInstructions.append(eachInstruction)
            self.finalInstructions.pop()
        
        for eachInstruction in self.__instructions:
            self.finalInstructions.append(eachInstruction)
        #print(self.__instructions)
        return self.finalInstructions

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
                self.__record_instruction(f'STWA {self.__current_variable},d')

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
        self.__record_instruction(f'LDWA {node.id},d')

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
                self.__record_instruction(f'DECI {self.__current_variable},d')
                self.__should_save = False # DECI already save the value in memory
            case 'print':
                # We are only supporting integers for now
                self.__record_instruction(f'DECO {node.args[0].id},d')
            case _:
                count = 0
                for arguement in node.args:
                    self.__record_instruction(f'LDWA {arguement.id},d')
                    self.__record_instruction(f'STWA {str(count)},s')
                    count +=2
    
                self.__record_instruction(f'CALL {node.func.id}')
                self.__record_instruction(f'LDWA {str(count)},s')

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
        #check for a return statement
        existsReturnStatement = False
        if isinstance(node.body[-1], ast.Return):
            self.numOfArgs +=1
            existsReturnStatement = True


        self.numOfArgs += len(node.args.args)
        self.__record_instruction('SUBSP '+ str(self.numOfArgs*2) + ',i')
        starter = FunctionLevelProgram(self.numOfArgs,node)
        starter.visit(node)
        self.functionInstructions.append(starter.finalize())

        count = 0
        for variable in starter.allocateMemory:
            self.functionParameters.append((f'm{variable}',count))
            count +=2
        count +=2
        for arguements in node.args.args:
            self.functionParameters.append((f'm{arguements.arg}', count))
            count +=2
        if existsReturnStatement:
            self.functionParameters.append((f'm{node.body[-1].value.id}', count))


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
            self.__record_instruction(f'{instruction} {node.id},d', label)

    def __identify(self):
        result = self.__elem_id
        self.__elem_id = self.__elem_id + 1
        return result