import argparse
import ast
from visitors.GlobalVariables import GlobalVariableExtraction
from visitors.TopLevelProgram import TopLevelProgram
from generators.StaticMemoryAllocation import StaticMemoryAllocation
from generators.EntryPoint import EntryPoint

def main():
    input_file, print_ast = process_cli()
    with open(input_file) as f:
        source = f.read()
    node = ast.parse(source)
    if print_ast:
        print(ast.dump(node, indent=2))
    else:
        process(input_file, node)
    
def process_cli():
    """"Process Command Line Interface options"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='filename to compile (.py)')
    parser.add_argument('--ast-only', default=False, action='store_true')
    args = vars(parser.parse_args())
    return args['f'], args['ast_only']

def process(input_file, root_node):
    print(f'; Translating {input_file}')
    extractor = GlobalVariableExtraction() 
    extractor.visit(root_node)
    top_level = TopLevelProgram('tl')
    top_level.visit(root_node)
    memory_alloc = StaticMemoryAllocation(extractor.results, top_level.constantValues, top_level.functionParameters)
    print('; Branching to top level (tl) instructions')
    print('\t\tBR tl')
    avoidSL = memory_alloc.generate()
    ep = EntryPoint(top_level.finalize(), avoidSL)
    ep.generate() 

if __name__ == '__main__':
    main()
