from bs4 import BeautifulSoup
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from automata.fa.gnfa import GNFA
from graphviz import Digraph
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


def create_automata(data):
    type_automata = data['type']

    states = set(data['states'])
    input_symbols = set(data['alphabet'])
    transitions = data['transitions']
    initial_state = data['start_state']
    final_states = set(data['accepting_states'])
    strings = data['strings']

    if type_automata == 'DFA':
        dfa_transitions = {}
        for from_state, transition in transitions.items():
            dfa_transitions[from_state] = {}
            for symbol, next_states in transition.items():
                next_states = next_states[0]
                dfa_transitions[from_state][symbol] = next_states
        print(dfa_transitions)
        automata = DFA(states=states,
                       input_symbols=input_symbols,
                       transitions=dfa_transitions,
                       initial_state=initial_state,
                       final_states=final_states)
        return automata, strings

    elif type_automata == 'NFA':
        nfa_transitions = {}
        for from_state, transition in transitions.items():
            nfa_transitions[from_state] = {}
            for symbol, next_states in transition.items():
                if isinstance(next_states, str):
                    next_states = {next_states}
                nfa_transitions[from_state][symbol] = set(next_states)

        automata = NFA(states=states,
                       input_symbols=input_symbols,
                       transitions=nfa_transitions,
                       initial_state=initial_state,
                       final_states=final_states)
        return automata, strings


def make_svg(automata):
    graph = Digraph(format='svg')

    print(automata)
    for state in automata.states:
        if state in automata.final_states:
            graph.node(state, shape='doublecircle')
        else:
            graph.node(state)

    for from_state, transitions in automata.transitions.items():
        for symbol, to_states in transitions.items():
            if isinstance(automata, DFA):
                graph.edge(from_state, to_states, label=symbol)
            else:
                for to_state in to_states:
                    graph.edge(from_state, to_state, label=symbol)

    svg_data = graph.pipe(format='svg').decode("utf-8")
    soup = BeautifulSoup(svg_data, 'html.parser')
    for tag in soup.find_all():
        tag.attrs = {key.split(':')[-1]: value for key, value in tag.attrs.items()}
        tag.name = tag.name.split(':')[-1]
    cleaned_svg = str(soup)
    return cleaned_svg


@app.route('/')
def home():
    data_test = {
        "type": "NFA",
        "states": ["q0", "q1", "q2"],
        "alphabet": ["0", "1"],
        "transitions": {
            "q0": {"0": ["q0", "q1"], "1": ["q0"]},
            "q1": {"0": ["q2"], "1": ["q1"]},
            "q2": {"0": [], "1": []}
        },
        "start_state": "q0",
        "accepting_states": ["q2"],
        "strings": "00111"
    }

    automata, strings = create_automata(data_test)
    result = automata.accepts_input(strings)
    svg_result = make_svg(automata)
    regex = GNFA.from_nfa(automata).to_regex()
    print(regex)
    return jsonify({'svgResult': svg_result, 'result': f'{result}'})


@app.route('/test_input', methods=['POST'])
def test_input():
    data = request.json
    automata, strings = create_automata(data)
    result = automata.accepts_input(strings)
    svg_result = make_svg(automata)
    return jsonify({'svgResult': svg_result, 'result': f'{result}'})


if __name__ == '__main__':
    app.run(debug=True)

# test