class EntryPoint():

    def __init__(self, instructions, avoidSL) -> None:
        self.__instructions = instructions
        self.avoidSL = avoidSL
        self.occurance = []

    def generate(self):
        print('; Top Level instructions')
        for label, instr in self.__instructions:
            s = f'\t\t{instr}' if label == None else f'{str(label+":"):<9}\t{instr}'
            print(s)