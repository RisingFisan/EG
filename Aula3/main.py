from lark import Lark, Token
from lark.visitors import Interpreter

def stringify(tree):
    result = ""
    for elem in tree:
        if isinstance(elem, tuple):
            result += "if (" + elem[0] + ") {\n\t" + '\n\t'.join(stringify(elem[1]).splitlines()) + "\n}\n"
            if len(elem) == 3:
                result += "else {\n\t" + '\n\t'.join(stringify(elem[1]).splitlines()) + "\n}\n"
        else:
            result += elem + ";\n"
    return result

class MyInterpreter(Interpreter):

    def __init__(self):
        self.initialized = set()

    def start(self, tree):
        attribs = self.visit(tree.children[0])
        r = self.visit(tree.children[1])
        if isinstance(attribs, str):
            return attribs
        else:
            return '\n'.join(attribs) +'\n\n' + stringify(r)

    def commands(self, tree):
        result = list()
        for child in tree.children:
            result.append(self.visit(child))
        # r = dict()
        # for child in tree.children:
        #     if child.data in ("if_","if_else"):
        #         rr = self.visit(child)
        #         for f in rr:
        #             r[f] = rr[f] + 1
        # return r
        
        return result

    def cond(self, tree):
        result = ' '.join(self.visit(x) if not isinstance(x,Token) else x for x in tree.children)
        return result

    def assign(self, tree):
        result = ' '.join(self.visit(x) if not isinstance(x,Token) else x for x in tree.children)
        return result

    def operation(self, tree):
        result = ' '.join(self.visit(x) if not isinstance(x,Token) else x for x in tree.children)
        return result

    def if_(self, tree):
        for child in tree.children:
            if child.data == "cond":
                cond = self.visit(child)
            elif child.data == "commands":
                d = self.visit(child)

        if len(d) == 1 and isinstance(d[0], tuple) and len(d[0]) == 2:
            return (cond + ' && ' + d[0][0], d[0][1])
        else:
            return (cond, d)

        # r = dict()
        # for child in tree.children:
        #     if child.data in ("if_", "if_else"):
        #         rr = self.visit(child)
        #         for f in rr:
        #             r[f] = rr[f] + 1 
        # r[tree] = 0 
        # return r

    def if_else(self, tree):
        for child in tree.children:
            if child.data == "if_":
                if_ = self.visit(child)
            elif child.data == "commands":
                else_c = self.visit(child)

        if len(if_[1]) == 1 and isinstance(if_[1][0], tuple) and len(if_[1][0]) == 2:
            return (if_[0] + ' && ' + if_[1][0][0], if_[1][0][1], else_c)
        else:
            return (if_[0], if_[1], else_c)

    def attribs(self, tree):
        result = list()
        errors = list()
        for child in tree.children:
            v = self.visit(child)
            if isinstance(v, tuple):
                errors.append(v[1])
            else:
                result.append(v)
        if len(errors) > 0:
            return "ERRO: " + ', '.join(errors) + " não atribuído(s)"
        return result

    def attrib_int(self, tree):
        if len(tree.children) == 1:
            return ("error", tree.children[0])
        return "int " + ' '.join(x.value for x in tree.children) + ";"

grammar = '''
start : attribs commands
attribs : (attrib_int | attrib_float)*
attrib_int : "int" VAR (EQ VALUE)? ";"
attrib_float : "float" VAR (EQ VALUEF)? ";"
commands : (assign | if_ | if_else)* 
assign : VAR EQ operation ";"
operation : "("? (VAR | VALUE | operation) ((PLUS | MINUS | TIMES | DIV | MOD) operation)? ")"?
VAR : /[a-zA-Z_][a-zA-Z_0-9]*/
VALUE : /\d+/
VALUEF : /\d*\.\d+/
EQ : "="
PLUS : "+"
MINUS : "-"
TIMES : "*"
DIV : "/"
MOD : "%"

if_ : "if" cond "{" commands "}"
if_else : if_ "else" "{" commands "}"

!cond : NOT? operation (("==" | "<" | ">" | "<=" | ">=") operation)?
NOT : "!" | "not"

%ignore /\s/
'''

with open("exemplo1.lgbti") as f:
    frase = f.read()

p = Lark(grammar)
parse_tree = p.parse(frase)

data = MyInterpreter().visit(parse_tree)
print(data)