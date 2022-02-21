from lark import Lark, Token, Transformer
from lark.tree import pydot__tree_to_png

grammar = '''
start : PE elemento PD
elemento : NUMERO (VIR NUMERO)*
PE : "["
PD : "]"
VIR : ","
NUMERO : "0".."9"+
'''

l = Lark(grammar)
frase = "[1,2,3]"
tree = l.parse(frase)
# print(tree)

for element in tree.children:
    print(element)

tokens = tree.scan_values(lambda x: isinstance(x, Token))
print(*tokens)

pydot__tree_to_png(tree,"tree.png")