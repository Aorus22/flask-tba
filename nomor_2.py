import graphviz
from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


# Mendefinisikan tipe-tipe ekspresi
class Type:
    SYMBOL = 1
    CONCAT = 2
    UNION  = 3
    KLEENE = 4

# Kelas untuk merepresentasikan node dalam pohon ekspresi
class ExpressionTree:

    def __init__(self, _type, value=None):
        self._type = _type
        self.value = value
        self.left = None
        self.right = None

# Fungsi untuk membangun pohon ekspresi dari ekspresi reguler
def constructTree(regexp):
    global z
    stack = []
    for c in regexp:
        if c.isalpha() or c.isdigit():
            stack.append(ExpressionTree(Type.SYMBOL, c))
        else:
            if c == "+":
                z = ExpressionTree(Type.UNION)
                z.right = stack.pop()
                z.left = stack.pop()
            elif c == ".":
                z = ExpressionTree(Type.CONCAT)
                z.right = stack.pop()
                z.left = stack.pop()
            elif c == "*":
                z = ExpressionTree(Type.KLEENE)
                z.left = stack.pop()
            stack.append(z)

    return stack[0]

# Fungsi untuk melakukan traversal inorder pada pohon ekspresi
def inorder(et):
    if et._type == Type.SYMBOL:
        print(et.value)
    elif et._type == Type.CONCAT:
        inorder(et.left)
        print(".")
        inorder(et.right)
    elif et._type == Type.UNION:
        inorder(et.left)
        print("+")
        inorder(et.right)
    elif et._type == Type.KLEENE:
        inorder(et.left)
        print("*")

# Fungsi untuk menentukan precedensi operator
def higherPrecedence(a, b):
    p = ["+", ".", "*"]
    return p.index(a) > p.index(b)

# Fungsi untuk mengonversi ekspresi reguler ke dalam notasi postfix
def postfix(regexp):
    # Menambahkan titik "." antara simbol-simbol berturut-turut
    temp = []
    for i in range(len(regexp)):
        if i != 0\
            and (regexp[i-1].isalpha() or regexp[i-1] == ")" or regexp[i-1] == "*")\
            and (regexp[i].isalpha() or regexp[i] == "("):
            temp.append(".")
        temp.append(regexp[i])
    regexp = temp
    
    stack = []
    output = ""

    for c in regexp:
        if c.isalpha() or c.isdigit():
            output = output + c
            continue

        if c == ")":
            while len(stack) != 0 and stack[-1] != "(":
                output = output + stack.pop()
            stack.pop()
        elif c == "(":
            stack.append(c)
        elif c == "*":
            output = output + c
        elif len(stack) == 0 or stack[-1] == "(" or higherPrecedence(c, stack[-1]):
            stack.append(c)
        else:
            while len(stack) != 0 and stack[-1] != "(" and not higherPrecedence(c, stack[-1]):
                output = output + stack.pop()
            stack.append(c)

    while len(stack) != 0:
        output = output + stack.pop()

    return output

# Kelas untuk merepresentasikan keadaan dalam otomata terbatas
class FiniteAutomataState:
    def __init__(self):
        self.next_state = {}

# Fungsi untuk mengevaluasi pohon ekspresi dan menghasilkan otomata terbatas yang setara
def evalRegex(et):
    if et._type == Type.SYMBOL:
        return evalRegexSymbol(et)
    elif et._type == Type.CONCAT:
        return evalRegexConcat(et)
    elif et._type == Type.UNION:
        return evalRegexUnion(et)
    elif et._type == Type.KLEENE:
        return evalRegexKleene(et)

# Fungsi untuk mengevaluasi node ekspresi tipe SYMBOL
def evalRegexSymbol(et):
    start_state = FiniteAutomataState()
    end_state   = FiniteAutomataState()
    
    start_state.next_state[et.value] = [end_state]
    return start_state, end_state

# Fungsi untuk mengevaluasi node ekspresi tipe CONCAT
def evalRegexConcat(et):
    left_nfa  = evalRegex(et.left)
    right_nfa = evalRegex(et.right)

    left_nfa[1].next_state['e'] = [right_nfa[0]]
    return left_nfa[0], right_nfa[1]

# Fungsi untuk mengevaluasi node ekspresi tipe UNION
def evalRegexUnion(et):
    start_state = FiniteAutomataState()
    end_state   = FiniteAutomataState()

    up_nfa   = evalRegex(et.left)
    down_nfa = evalRegex(et.right)

    start_state.next_state['e'] = [up_nfa[0], down_nfa[0]]
    up_nfa[1].next_state['e'] = [end_state]
    down_nfa[1].next_state['e'] = [end_state]

    return start_state, end_state

# Fungsi untuk mengevaluasi node ekspresi tipe KLEENE
def evalRegexKleene(et):
    start_state = FiniteAutomataState()
    end_state   = FiniteAutomataState()

    sub_nfa = evalRegex(et.left)

    start_state.next_state['e'] = [sub_nfa[0], end_state]
    sub_nfa[1].next_state['e'] = [sub_nfa[0], end_state]

    return start_state, end_state

# Fungsi untuk mencetak transisi keadaan otomata terbatas
def printStateTransitions(state, states_done, symbol_table):
    if state in states_done:
        return

    states_done.append(state)

    for symbol in list(state.next_state):
        line_output = "q" + str(symbol_table[state]) + "\t\t" + symbol + "\t\t\t"
        for ns in state.next_state[symbol]:
            if ns not in symbol_table:
                symbol_table[ns] = 1 + sorted(symbol_table.values())[-1]
            line_output = line_output + "q" + str(symbol_table[ns]) + " "

        print(line_output)

        for ns in state.next_state[symbol]:
            printStateTransitions(ns, states_done, symbol_table)

# Fungsi untuk visualisasi diagram transisi otomata terbatas
def visualizeTransitionGraph(finite_automata):
    dot = graphviz.Digraph(comment='Finite Automata Transition Diagram')

    symbol_table = {}
    state_count = 0

    def addState(state):
        nonlocal state_count
        if state not in symbol_table:
            symbol_table[state] = "q" + str(state_count)
            state_count += 1

    def addTransition(state, next_state, symbol):
        dot.node(symbol_table[state], symbol_table[state])
        dot.node(symbol_table[next_state], symbol_table[next_state])
        dot.edge(symbol_table[state], symbol_table[next_state], label=symbol)

    def exploreState(state):
        if state in explored_states:
            return
        explored_states.add(state)

        for symbol, next_states in state.next_state.items():
            for next_state in next_states:
                addState(next_state)
                addTransition(state, next_state, symbol)
                exploreState(next_state)

    start_state, _ = finite_automata
    explored_states = set()
    addState(start_state)
    exploreState(start_state)

    return dot


def nomor_2_run(input_regex):
    pr = postfix(input_regex)
    et = constructTree(pr)
    fa = evalRegex(et)
    transition_diagram = visualizeTransitionGraph(fa)
    svg_result = transition_diagram.pipe(format='svg').decode('utf-8')

    return svg_result

