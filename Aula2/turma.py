from lark import Discard, Lark, Token, Transformer
import datetime

class TransformaTurma(Transformer):
    def __init__(self):
        self.n_alunos = 0
        self.acc = None
        self.medias = dict()
        self.notas_alunos = dict()
        self.queries = list()
        self.letra_turma = None

    def start(self, item):
        return {
            'n_alunos': self.n_alunos,
            'media': self.medias,
            'notas_alunos': self.notas_alunos,
            'queries': self.queries
        }

    def LETRA(self, letra):
        self.letra_turma = letra.value

    def aluno(self, aluno):
        self.n_alunos += 1
        return aluno

    def notas(self, notas):
        self.medias[self.acc] = round(self.medias[self.acc] / len(notas), 2)
        return notas

    def NOME(self, nome):
        self.acc = nome.value
        self.medias[self.acc] = 0
        return nome.value

    def VIR(self, _):
        return Discard

    def NOTA(self, nota):
        nota = int(nota)
        self.medias[self.acc] += nota
        self.notas_alunos.setdefault(nota, set()).add(self.acc)
        self.queries.append(f"INSERT INTO Resultado (nomeAluno, nota, dataInsercao, turma) VALUES ({self.acc}, {nota}, {datetime.date.today()}, {self.letra_turma})")
        return nota

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
data = TransformaTurma().transform(tree)
print(data)