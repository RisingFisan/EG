from lark import Lark, Token, Transformer
from collections import defaultdict
from operator import itemgetter

grammar = '''
start : INIT lista PONTO
lista : elemento (VIR elemento)*
elemento : NUMERO | PALAVRA
INIT : "Lista"i
PONTO : "."
VIR : ","
NUMERO : "0".."9"+
PALAVRA : /\w/+
%ignore /\s/
'''

class TransformaLista(Transformer):
    def __init__(self):
        self.comp = 0
        self.soma = 0
        self.count = False
        self.ocurrences = defaultdict(lambda: 0)
        self.mais_comum = None
        self.output = {}

    def start(self, item):
        self.comp = len(item[1])
        self.mais_comum = max(self.ocurrences.items(), key=itemgetter(1))[0]
        self.output = {
            'soma' : self.soma,
            'comp' : self.comp,
            'mais_comum' : self.mais_comum
        }
        return self.output

    def lista(self, lista):
        return [x for x in lista if x != ',']
    
    def elemento(self, elemento):
        self.ocurrences[elemento[0]] += 1
        return elemento[0]

    def NUMERO(self, n):
        n = int(n)
        if self.count:
            self.soma += n
        return n

    def PALAVRA(self, p):
        match(p):
            case "agora":
                self.count = True
            case "fim":
                self.count = False
        return p.value

    def INIT(self, pd):
        return pd.value

    def VIR(self, vir):
        return vir.value

    def PONTO(self, ponto):
        return ponto.value

    

l = Lark(grammar)

lista = input("Insira uma lista: ")
if not lista: lista = "Lista 1, 2, agora, 3, 4, fim, 2, 8 ."
tree = l.parse(lista)

# tokens = tree.scan_values(lambda v: isinstance(v, Token))
# elems = [str(x) for x in tokens if x.type in {"NUMERO", "PALAVRA"}]
# print(f"Elementos da lista ({len(elems)}):")
# print(*elems)

# ocurrences = dict()
# for elem in elems:
#     ocurrences.setdefault(elem,0)
#     ocurrences[elem] += 1

# print("Elemento mais comum:", "{} - aparece {} vezes".format(*max(ocurrences.items(), key=lambda x: x[1])))

# total = -1
# for elem in elems:
#     match(elem):
#         case "agora":
#             total = 0
#         case "fim":
#             break
#         case x:
#             n = int(x)
#             if n >= 0:
#                 total += n

# print(f"Soma entre \"agora\" e \"fim\": {total}")
    
data = TransformaLista().transform(tree)
print(data)