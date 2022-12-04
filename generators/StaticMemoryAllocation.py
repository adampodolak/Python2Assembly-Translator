
class StaticMemoryAllocation():

    def __init__(self, global_vars: dict(), constantValues) -> None:
        self.__global_vars = global_vars
        self.constantValues = constantValues

    def generate(self):
        keepGoing = True
        avoidSL = []
        print('; Allocating Global (static) memory')
        for n in self.__global_vars:
            for vars in self.constantValues:
                if vars[0] == n:
                    if "_" == n[0] and n.strip("_").isupper():
                        print(f'{str(n+":"):<9}\t.EQUATE ' + str(vars[1]))
                        keepGoing = False
                        avoidSL.append(vars)
                        break
                    
                    elif (vars[1] != None):
                        print(f'{str(n+":"):<9}\t.WORD ' + str(vars[1]))
                        keepGoing = False
                        avoidSL.append(vars)
                        break
            if keepGoing:
                print(f'{str(n+":"):<9}\t.BLOCK 2') # reserving memory
                                        #change ".BLOCK 2" into ".WORD n?"
            keepGoing = True
        return avoidSL

