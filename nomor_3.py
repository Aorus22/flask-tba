from automata.fa.dfa import DFA
from nomor_5 import create_automata
from nomor_5 import make_svg

def minimize_dfa(dfa):
    def get_next_state(current_state, symbol, transitions):
        return transitions.get(current_state, {}).get(symbol)

    def are_states_equivalent(state1, state2):
        return equivalence_classes[state1][state2]
    # Step 1: Inisialisasi DFA Awal
    minimal_dfa = dfa.copy()
    
    # Initialize equivalence table (abe)
    equivalence_classes = {}
    for state1 in dfa.states:
        equivalence_classes[state1] = {}
        for state2 in dfa.states:
            equivalence_classes[state1][state2] = (state1 in dfa.final_states) == (state2 in dfa.final_states)

    
    # Check for unreachable states and mark them as non-equivalent (abe)
    for state1 in dfa.states:
        for state2 in dfa.states:
            for symbol in dfa.input_symbols:
                next_state1 = get_next_state(state1, symbol, dfa.transitions)
                next_state2 = get_next_state(state2, symbol, dfa.transitions)
                if (next_state1 is None and next_state2 is not None) or (next_state1 is not None and next_state2 is None):
                    equivalence_classes[state1][state2] = False

    # Iteratively refine equivalence table (abe)
    while True:
        changed = False
        for state1 in dfa.states:
            for state2 in dfa.states:
                if not equivalence_classes[state1][state2]:
                    continue
                for symbol in dfa.input_symbols:
                    next_state1 = get_next_state(state1, symbol, dfa.transitions)
                    next_state2 = get_next_state(state2, symbol, dfa.transitions)
                    if not are_states_equivalent(next_state1, next_state2):
                        equivalence_classes[state1][state2] = False
                        changed = True
                        break
            if changed:
                break
        if not changed:
            break

    # Step 4: Konstruksi DFA Minimal
    equivalence_group = {}
    group_counter = 0
    for state1 in minimal_dfa.states:
        if state1 not in equivalence_group:
            group_counter += 1
            equivalence_group[state1] = group_counter
        for state2 in minimal_dfa.states:
            if state1 != state2 and equivalence_classes[state1][state2]:
                equivalence_group[state2] = equivalence_group[state1]

    # Update DFA dengan state baru
    new_states = {}
    for state in minimal_dfa.states:
        new_states[state] = "q" + str(equivalence_group[state])

    very_new_states = set()
    new_final_state = set()
    new_transition = set()
    for state in minimal_dfa.states:
        very_new_states.add(new_states[state])
        # new_dfa.add_state(new_states[state])
        if state in minimal_dfa.final_states:
            new_final_state.add(new_states[state])
            # new_dfa.add_final_state(new_states[state])

    # new_dfa.add_start_state(new_states[minimal_dfa.start_state])

    for state in minimal_dfa.states:
        for symbol in minimal_dfa.input_symbols:
            next_state = minimal_dfa.transitions[state][symbol]
            # next_state = minimal_dfa(state, symbol)
            if next_state:
                next_state_new = new_states[next_state]
                transition = (new_states[state], symbol, next_state_new)
                new_transition.add(transition)
                # new_dfa.add_transition(new_states[state], symbol, next_states[0])

    converted_transitions = {}

    for transition in new_transition:
        start_state, symbol, next_state = transition
        if start_state not in converted_transitions:
            converted_transitions[start_state] = {}
        converted_transitions[start_state][symbol] = next_state
    
    new_dfa = DFA(
        states=very_new_states,         # Set keadaan kosong
        input_symbols=minimal_dfa.input_symbols,  # Set simbol input kosong
        transitions=converted_transitions,   # Kamus transisi kosong
        initial_state=str(new_states[minimal_dfa.initial_state]),   # Keadaan awal tidak ditentukan
        final_states=new_final_state    # Set keadaan akhir kosong
    )

    return new_dfa

# main function
def nomor_3_run(input_dfa):
    dfa = create_automata(input_dfa)
    minimized_dfa = minimize_dfa(dfa)
    svgResult = make_svg(minimized_dfa)
    return svgResult

# contoh soal
# dfa = DFA(
#     states = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6'],
#     input_symbols = ['0', '1'],
#     transitions = {'q1' : {'0' : ['q2'], '1' : ['q3']},
#                     'q2' : {'0' : ['q1'], '1' : ['q4']},
#                     'q3' : {'0' : ['q3'], '1' : ['q4']},
#                     'q4' : {'0' : ['q2'], '1' : ['q3']},
#                     'q5' : {'0' : ['q5'], '1' : ['q3']},
#                     'q6' : {'0' : ['q5'], '1' : ['q3']}
#                     },
#     initial_state = 'q1',
#     final_states = ['q3', 'q4']
# )

input_dfa = {
    "type": "DFA",
    "states": ["q0", "q1"],
    "alphabet": ["0", "1"],
    "transitions": {
        "q0": {"0": ["q0"], "1": ["q1"]},
        "q1": {"0": ["q0"], "1": ["q1"]}
    },
    "start_state": "q0",
    "accepting_states": ["q1"],
    "strings": "000101"
}

nomor_3_run(input_dfa)