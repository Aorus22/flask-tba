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
        self.path_mentah = []
        self.path = []

    def accepts_input(self, input_string):
        current_states = {self.initial_state}
        self.path = []
        index = 0
        while index < len(input_string):
            for length in range(1, len(input_string) - index + 1):
                symbol = input_string[index:index + length]

                if symbol in self.input_symbols:
                    index += length
                    next_states = {}
                    for state in current_states:
                        next_states[state] = self.transitions[state].get(symbol, set())
                    current_states = set()
                    for states_set in next_states.values():
                        current_states.update(states_set)
                    self.path_mentah.append(next_states)
                    break
                else:
                    return False

            if not current_states:
                return False

        print(self.path_mentah)
        self.track_path()
        return any(state in self.final_states for state in current_states)

    def track_path(self):
        def cek_accepting(cek_dict, finish_set):
            selected_child = ""
            for child_set in cek_dict.values():
                for child in child_set:
                    if child in finish_set:
                        selected_child = child
            if selected_child == "":
                for children_set in cek_dict.values():
                    children_list = list(children_set)
                    if not children_list:
                        continue
                    selected_child = children_list[0]
                    break
            return selected_child

        def cari_key(d, nilai):
            for k, v in d.items():
                if nilai in v:
                    return k
            return None

        last_path = self.path_mentah[-1]
        current = cek_accepting(last_path, self.final_states)
        self.path.append(current)
        for element in reversed(self.path_mentah):
            current = cari_key(element, current)
            self.path.append(current)

        self.path = self.path[::-1]
        print(self.path)
        return self.path


class ENFA:
    def __init__(self, states, input_symbols, transitions, initial_state, final_states):
        self.states = states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
        self.path_mentah = []
        self.path = []

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

                    next_states = {}
                    for state in current_states:
                        transitions = self.transitions[state].get(symbol, set())
                        transitions_with_epsilon = set()
                        for transition_state in transitions:
                            transitions_with_epsilon.update(self.epsilon_closure({transition_state}))
                        next_states[state] = transitions_with_epsilon
                    current_states = set().union(*next_states.values())

                    self.path_mentah.append(next_states)
                    break
                else:
                    return False

            if not current_states:
                return False
            
        self.track_path()
        return any(state in self.final_states for state in current_states)

    def track_path(self):
        def cek_accepting(cek_dict, finish_set):
            selected_child = ""
            for child_set in cek_dict.values():
                for child in child_set:
                    if child in finish_set:
                        selected_child = child
            if selected_child == "":
                for children_set in cek_dict.values():
                    children_list = list(children_set)
                    if not children_list:
                        continue
                    selected_child = children_list[0]
                    break
            return selected_child

        def cari_key(d, nilai):
            for k, v in d.items():
                if nilai in v:
                    return k
            return None

        last_path = self.path_mentah[-1]
        current = cek_accepting(last_path, self.final_states)
        self.path.append(current)
        for element in reversed(self.path_mentah):
            current = cari_key(element, current)
            self.path.append(current)

        self.path = self.path[::-1]
        print(self.path)
        return self.path


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

    prev_value = ""
    for i, value in enumerate(automata.path):
        if i == 0:
            prev_value = value
            continue
        langkah_ke = "[" + str(i) + "]"
        graph.edge(prev_value, value, label=langkah_ke, color='green', fontcolor='blue')
        prev_value = value

    svg_data = graph.pipe(format='svg').decode("utf-8")
    soup = BeautifulSoup(svg_data, 'html.parser')
    for tag in soup.find_all():
        tag.attrs = {key.split(':')[-1]: value for key, value in tag.attrs.items()}
        tag.name = tag.name.split(':')[-1]
    cleaned_svg = str(soup)
    return cleaned_svg
