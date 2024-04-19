from bs4 import BeautifulSoup
from graphviz import Digraph

class NFA:
    def __init__(self, data):
        self.states = data["states"]
        self.alphabets = data["alphabet"]
        self.start = data["start_state"]
        self.finals = data["accepting_states"]
        self.transition_table = {}

        # Initialize transition table
        for state, transitions in data["transitions"].items():
            self.transition_table[state] = {}
            for symbol, next_states in transitions.items():
                self.transition_table[state][symbol] = next_states

    def getEpsilonClosure(self, state):
        closure = set()
        stack = [state]

        while stack:
            current = stack.pop()
            closure.add(current)

            if "" in self.transition_table[current]:
                epsilon_transitions = self.transition_table[current][""]
                for next_state in epsilon_transitions:
                    if next_state not in closure:
                        stack.append(next_state)

        return closure

    def getStateName(self, state_list):
        return ''.join(sorted(state_list))

    def isFinalDFA(self, state_list):
        return any(state in self.finals for state in state_list)

def convertToDFA(input_nfa):

    data_test = {
        "type": "NFA",
        "states": ["q0", "q1", "q2"],
        "alphabet": ["0", "1"],
        "transitions": {
            "q0": {"": ["q1", "q2"], "0": ["q1"], "1": ["q0"]},
            "q1": {"1": ["q2"]},
            "q2": {"0": [], "1": []}
        },
        "start_state": "q0",
        "accepting_states": ["q2"],
        "strings": "110"
    }

    nfa = NFA(input_nfa)

    nfa.graph = Digraph()

    for state in nfa.states:
        if state in nfa.finals:
            nfa.graph.attr('node', shape='doublecircle')
        else:
            nfa.graph.attr('node', shape='circle')
        nfa.graph.node(state)

    nfa.graph.attr('node', shape='none')
    nfa.graph.node('')
    nfa.graph.edge('', nfa.start)

    for state, transitions in nfa.transition_table.items():
        for symbol, next_states in transitions.items():
            for next_state in next_states:
                if symbol:
                    nfa.graph.edge(state, next_state, label=symbol)
                else:
                    nfa.graph.edge(state, next_state, label='ε')

    svg_nfa = nfa.graph.pipe(format='svg').decode('utf-8')
    print(svg_nfa)

    dfa = Digraph()

    epsilon_closure = {}
    for state in nfa.states:
        epsilon_closure[state] = nfa.getEpsilonClosure(state)

    dfa_stack = [epsilon_closure[nfa.start]]

    if nfa.isFinalDFA(dfa_stack[0]):
        dfa.attr('node', shape='doublecircle')
    else:
        dfa.attr('node', shape='circle')
    dfa.node(nfa.getStateName(dfa_stack[0]))

    dfa.attr('node', shape='none')
    dfa.node('')
    dfa.edge('', nfa.getStateName(dfa_stack[0]))

    dfa_states = [epsilon_closure[nfa.start]]

    while dfa_stack:
        cur_state = dfa_stack.pop(0)

        for symbol in nfa.alphabets:
            from_closure = set()
            for state in cur_state:
                if symbol in nfa.transition_table[state]:
                    from_closure.update(nfa.transition_table[state][symbol])

            if from_closure:
                to_state = set()
                for state in from_closure:
                    to_state.update(epsilon_closure[state])

                if to_state not in dfa_states:
                    dfa_stack.append(to_state)
                    dfa_states.append(to_state)

                    if nfa.isFinalDFA(list(to_state)):
                        dfa.attr('node', shape='doublecircle')
                    else:
                        dfa.attr('node', shape='circle')
                    dfa.node(nfa.getStateName(list(to_state)))

                dfa.edge(nfa.getStateName(cur_state), nfa.getStateName(list(to_state)), label=symbol)
            else:
                if (-1) not in dfa_states:
                    dfa.attr('node', shape='circle')
                    dfa.node('ϕ')

                    for alpha in nfa.alphabets:
                        dfa.edge('ϕ', 'ϕ', label=alpha)

                    dfa_states.append(-1)

                dfa.edge(nfa.getStateName(cur_state), 'ϕ', label=symbol)


    svg_dfa = dfa.pipe(format='svg').decode('utf-8')
    print(svg_dfa)

    soup = BeautifulSoup(svg_nfa, 'html.parser')
    for tag in soup.find_all():
        tag.attrs = {key.split(':')[-1]: value for key, value in tag.attrs.items()}
        tag.name = tag.name.split(':')[-1]
    cleaned_svg_nfa = str(soup)

    soup = BeautifulSoup(svg_dfa, 'html.parser')
    for tag in soup.find_all():
        tag.attrs = {key.split(':')[-1]: value for key, value in tag.attrs.items()}
        tag.name = tag.name.split(':')[-1]
    cleaned_svg_dfa = str(soup)

    return cleaned_svg_nfa, cleaned_svg_dfa


def nomor_1_run(input_nfa):
    return convertToDFA(input_nfa)
