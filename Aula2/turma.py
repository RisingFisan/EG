from lark import Lark, Token

grammar = '''
start : INIT LETRA alunos PONTO
alunos : aluno (SEP aluno)*
aluno : NOME AP notas FP
notas : NOTA (VIR NOTA)*
INIT : "Turma"i
PONTO : "."
SEP : ";"
VIR : ","
LETRA : "A".."Z"
NOME : /\w/+
%import common.DIGIT
NOTA : "0"? DIGIT | "1" DIGIT | "20"
AP : "("
FP : ")"
%ignore /\s/
'''

l = Lark(grammar)

frase = """TURMA A
ana (12, 13, 15, 12, 13, 15, 14);
joao (9,7,3,6,9);
xico (12,16)."""

tree = l.parse(frase)
print(tree)