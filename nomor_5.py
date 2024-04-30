from bs4 import BeautifulSoup
from graphviz import Digraph
import copy


class DFA:
    def __init__(self, states, input_symbols, transitions, initial_state, final_states):
        self.states = states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
        self.path = [self.initial_state]

    def accepts_input(self, input_string):
        current_state = self.initial_state

        for symbol in input_string:
            if symbol not in self.input_symbols:
                return False
            current_state = self.transitions[current_state].get(symbol)
            if current_state is None:
                return False
            self.path.append(current_state)
        return current_state in self.final_states

    def copy(self):
        return copy.deepcopy(self)


class NFA:
    def __init__(self, states, input_symbols, transitions, initial_state, final_states):
        self.states = states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states

    def accepts_input(self, input_string):
        current_states = {self.initial_state}
        index = 0
        while index < len(input_string):
            for length in range(1, len(input_string) - index + 1):
                symbol = input_string[index:index + length]

                if symbol in self.input_symbols:
                    index += length
                    next_states = set()
                    for state in current_states:
                        next_states.update(self.transitions[state].get(symbol, set()))
                    current_states = next_states
                    break
            else:
                return False

            if not current_states:
                return False

        return any(state in self.final_states for state in current_states)


class ENFA:
    def __init__(self, states, input_symbols, transitions, initial_state, final_states):
        self.states = states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states

    def epsilon_closure(self, states):
        closure = set(states)
        stack = list(states)
        while stack:
            state = stack.pop()
            epsilon_transitions = self.transitions[state].get('', set())
            for epsilon_state in epsilon_transitions:
                if epsilon_state not in closure:
                    closure.add(epsilon_state)
                    stack.append(epsilon_state)
        return closure

    def transition_with_epsilon(self, states, symbol):
        result = set()
        for state in states:
            epsilon_closure_states = self.epsilon_closure({state})
            for epsilon_state in epsilon_closure_states:
                next_states = self.transitions[epsilon_state].get(symbol, set())
                result.update(next_states)
        return result

    def accepts_input(self, input_string):
        current_states = self.epsilon_closure({self.initial_state})

        index = 0
        while index < len(input_string):
            for length in range(1, len(input_string) - index + 1):
                symbol = input_string[index:index + length]

                if symbol in self.input_symbols:
                    index += length
                    next_states = set()
                    for state in current_states:
                        next_states.update(self.transition_with_epsilon(current_states, symbol))
                        current_states = next_states
                        break
        # for symbol in input_string:
        #     next_states = self.transition_with_epsilon(current_states, symbol)
        #     current_states = next_states
        return any(state in self.final_states for state in current_states)


def create_automata(data):
    type_automata = data['type']

    states = set(data['states'])
    input_symbols = set(data['alphabet'])
    transitions = data['transitions']
    initial_state = data['start_state']
    final_states = set(data['accepting_states'])

    if type_automata == 'DFA':
        dfa_transitions = {}
        for from_state, transition in transitions.items():
            dfa_transitions[from_state] = {}
            for symbol, next_states in transition.items():
                if next_states:
                    next_state = next_states[0]
                    dfa_transitions[from_state][symbol] = next_state
        automata = DFA(states=states,
                       input_symbols=input_symbols,
                       transitions=dfa_transitions,
                       initial_state=initial_state,
                       final_states=final_states)
        return automata

    elif type_automata == 'NFA':
        nfa_transitions = {}
        for from_state, transition in transitions.items():
            nfa_transitions[from_state] = {}
            for symbol, next_states in transition.items():
                if isinstance(next_states, str):
                    next_states = {next_states}
                if next_states:
                    nfa_transitions[from_state][symbol] = set(next_states)

        automata = NFA(states=states,
                       input_symbols=input_symbols,
                       transitions=nfa_transitions,
                       initial_state=initial_state,
                       final_states=final_states)
        return automata

    elif type_automata == 'ENFA':
        nfa_transitions = {}
        for from_state, transition in transitions.items():
            nfa_transitions[from_state] = {}
            for symbol, next_states in transition.items():
                if isinstance(next_states, str):
                    next_states = {next_states}
                if next_states:
                    nfa_transitions[from_state][symbol] = set(next_states)

        automata = ENFA(states=states,
                       input_symbols=input_symbols,
                       transitions=nfa_transitions,
                       initial_state=initial_state,
                       final_states=final_states)
        return automata


def make_svg(automata):
    graph = Digraph(format='svg')

    for state in automata.states:
        if state in automata.final_states:
            graph.node(state, shape='doublecircle')
        else:
            graph.node(state)

    for from_state, transitions in automata.transitions.items():
        for symbol, to_states in transitions.items():
            if symbol == "":
                symbol = "ε"
            if isinstance(automata, DFA):
                graph.edge(from_state, to_states, label=symbol)
            else:
                for to_state in to_states:
                    graph.edge(from_state, to_state, label=symbol)

    if automata.initial_state:
        graph.attr('node', shape='none')
        graph.node('')
        graph.edge('', automata.initial_state, label="start")

    svg_data = graph.pipe(format='svg').decode("utf-8")
    soup = BeautifulSoup(svg_data, 'html.parser')
    for tag in soup.find_all():
        tag.attrs = {key.split(':')[-1]: value for key, value in tag.attrs.items()}
        tag.name = tag.name.split(':')[-1]
    cleaned_svg = str(soup)
    return cleaned_svg


def draw_path(automata):
    graph = Digraph(format='svg')

    for state in automata.states:
        if state in automata.final_states:
            graph.node(state, shape='doublecircle')
        else:
            graph.node(state)

    for from_state, transitions in automata.transitions.items():
        for symbol, to_states in transitions.items():
            if symbol == "":
                symbol = "ε"
            if isinstance(automata, DFA):
                graph.edge(from_state, to_states, label=symbol)
            else:
                for to_state in to_states:
                    graph.edge(from_state, to_state, label=symbol)

    if automata.initial_state:
        graph.attr('node', shape='none')
        graph.node('')
        graph.edge('', automata.initial_state, label="start")

    prevValue = ""
    for i, value in enumerate(automata.path):
        if i == 0:
            prevValue = value
            continue
        langkahKe = "[" + str(i) + "]"
        graph.edge(prevValue, value, label=langkahKe, color='green', fontcolor='blue')
        prevValue = value
    
    svg_data = graph.pipe(format='svg').decode("utf-8")
    soup = BeautifulSoup(svg_data, 'html.parser')
    for tag in soup.find_all():
        tag.attrs = {key.split(':')[-1]: value for key, value in tag.attrs.items()}
        tag.name = tag.name.split(':')[-1]
    cleaned_svg = str(soup)
    return cleaned_svg
