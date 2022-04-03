from enum import Enum
from lark import Lark, Token, Tree
from lark.visitors import Interpreter
from functools import reduce

class If:
    def __init__(self, condition, commands, level, else_ = None):
        self.condition = condition
        self.commands = commands
        self.else_ = else_
        self.level = level

    def concat(self):
        if len(self.commands) == 1:
            child = self.commands[0]
            if isinstance(child, If) and child.else_ == None:
                child.concat()
                cmds = child.commands
                self.condition = self.condition + ' && ' + child.condition
                self.commands = cmds

    def __str__(self) -> str:
        cmds = lambda c : reduce(lambda acc, x: acc + [x] if isinstance(x, str) else acc + str(x).splitlines(), c, list())
        c = f"if ({self.condition}) {{ // nível {self.level}" + "\n" + '\n'.join('\t' + x for x in cmds(self.commands)) + "\n}"
        if self.else_ != None:
            if isinstance(self.else_, If):
                c += " else " + str(self.else_)
            else:
                c += " else {\n" + '\n'.join('\t' + str(x) for x in cmds(self.else_)) + "\n}"
        return c

class Types(Enum):
    INT = 0
    FLOAT = 1
    ARRAY = 2

class MyInterpreter(Interpreter):

    def __init__(self):
        self.initialized = dict()
        self.level = -1

    def start(self, tree):
        decls = self.visit(tree.children[0])
        r = self.visit(tree.children[1])
        if isinstance(decls, str):
            return decls
        else:
            return '\n'.join(decls) +'\n\n' + '\n'.join(str(x) for x in r)

    def commands(self, tree):
        self.level += 1
        result = list()
        for child in tree.children:
            visited = self.visit(child)
            if isinstance(visited, If):
                visited.concat()
            result.append(visited)
        
        self.level -= 1
        return result

    def cond(self, tree):
        result = ' '.join(self.visit(x) if not isinstance(x,Token) else x for x in tree.children)
        return result

    def assign(self, tree):
        result = ' '.join(self.visit(x) if not isinstance(x,Token) else x for x in tree.children) + ';'
        return result

    def operation(self, tree):
        result = ' '.join(self.visit(x) if not isinstance(x,Token) else x for x in tree.children)
        return result

    def factor(self, tree):
        result = ' '.join(self.visit(x) if not isinstance(x,Token) else x for x in tree.children)
        return result

    def term(self, tree):
        result = ' '.join(self.visit(x) if not isinstance(x,Token) else x for x in tree.children)
        return result

    def if_(self, tree):
        for child in tree.children:
            if child.data == "cond":
                cond = self.visit(child)
            elif child.data == "commands":
                d = self.visit(child)

        return If(cond, d, self.level)

    def if_else(self, tree):
        if_ = None
        for child in tree.children:
            if child.data == "if_":
                if if_ == None:
                    if_ : If = self.visit(child)
                else:
                    else_c = self.visit(child)
            elif child.data == "commands":
                else_c = self.visit(child)

        if_.else_ = else_c
        return if_

    def decls(self, tree):
        result = list()
        errors = list()
        for child in tree.children:
            v = self.visit(child)
            if isinstance(v, tuple):
                errors.append(v[1])
            else:
                result.append(v)
        if len(errors) > 0:
            return "ERRO: " + ', '.join(errors) + " não declarado(s)"
        return result

    def decl_int(self, tree):
        if len(tree.children) == 1:
            return ("error", tree.children[0])
        return "int " + ' '.join(x.value for x in tree.children) + ";"

    def decl_float(self, tree):
        if len(tree.children) == 1:
            return ("error", tree.children[0])
        return "float " + ' '.join(x.value for x in tree.children) + ";"

    def decl_array(self, tree : Tree):
        var = None
        size = None
        elems = None
        for child in tree.children:
            if isinstance(child, Token):
                if child.type == "VAR":
                    var = child.value
                elif child.type == "INT":
                    size = int(child.value)
            else:
                v = self.visit(child)
                elems = v
        return f"int {var}[{size if size else ''}]{' = ' + elems if elems else ''};"

    def array(self, tree):
        return "[" + ','.join(self.visit(tree.children[0])) + "]"

grammar = '''
start : decls commands
decls : (decl_int | decl_float | decl_array)*
decl_int : "int" VAR (EQ VALUE)? ";"
decl_float : "float" VAR (EQ VALUEF)? ";"
decl_array : "int" VAR "[" INT? "]" (EQ array)? ";"
commands : (assign | if_ | if_else)* 
assign : VAR EQ operation ";"
operation : (operation (PLUS | MINUS))* term
term : (term (TIMES | DIV | MOD))* factor
factor : VALUE | "(" operation ")"
VAR : /[a-zA-Z_][a-zA-Z_0-9]*/
VALUEI : INT | VAR
VALUEF : FLOAT | VAR
VALUE : VALUEF | VALUEI
INT : /\d+/
FLOAT : /\d*\.\d+/
EQ : "="
PLUS : "+"
MINUS : "-"
TIMES : "*"
DIV : "/"
MOD : "%"

if_ : "if" "(" cond ")" "{" commands "}"
if_else : if_ "else" ("{" commands "}" | if_)

!cond : NOT? operation (("==" | "<" | ">" | "<=" | ">=") operation)? ((AND | OR) cond)?
AND : "&&" | "and"
OR : "||" | "or"
NOT : "!" | "not"

array : "[" values "]"
values : VALUE ("," VALUE)*

%ignore /\s/
'''

with open("exemplo1.lgbti") as f:
    frase = f.read()

p = Lark(grammar)
parse_tree = p.parse(frase)

data = MyInterpreter().visit(parse_tree)
print(data)