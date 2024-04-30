from nomor_5 import DFA, make_svg

def remove_unreachable_states(automaton, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    
    for neighbor in automaton.transitions[start]:
        if automaton.transitions[start][neighbor] not in visited:
            remove_unreachable_states(automaton, automaton.transitions[start][neighbor], visited)
    
    return list(sorted(visited))

def minimize_dfa(dfa):
    def get_next_state(current_state, symbol, transitions):
        return transitions.get(current_state, {}).get(symbol)

    def are_states_equivalent(state1, state2):
        return equivalence_classes[state1][state2]

    # 1. remove unreachable states
    reachable_states = remove_unreachable_states(dfa, dfa.initial_state)
    
    # 2. mark accepting states ≠ non accepting states,
    # disini diibaratkan semua state equivalent terlebih dahulu
    equivalence_classes = {}
    for state1 in reachable_states:
        equivalence_classes[state1] = {}
        for state2 in reachable_states:
            equivalence_classes[state1][state2] = (state1 in dfa.final_states) == (state2 in dfa.final_states)
    
    print("table filing accepting states ≠ non accepting states : ")
    for state1 in sorted(reachable_states):
        print(state1, end=" ")
        for state2 in sorted(reachable_states):
            print(str(equivalence_classes[state1][state2]), end=" ")
            if (state1 == state2): break
        print("\n")
    for state in sorted(reachable_states): print(" st " + state, end=" ")
    print("")

    # cek jika terdapat dua final states
    # if (len(dfa.final_states) > 1):
    #     for final_state1 in dfa.final_states:
    #         for final_state2 in dfa.final_states:

    # Iteratively refine equivalence table
    # table filling algorithm
    while True:
        changed = False
        for state1 in reachable_states:
            for state2 in reachable_states:
                # jika tidak ekuivalent pada table awal (false),
                # karena nilai false sudah diisikan dari accepting state ≠ non accepting state
                if not equivalence_classes[state1][state2]:
                    continue
                for symbol in dfa.input_symbols:
                    next_state1 = get_next_state(state1, symbol, dfa.transitions)
                    next_state2 = get_next_state(state2, symbol, dfa.transitions)
                    # next tidak equivalent = salah satu next state adalah final state
                    # maka kedua state tidak equivalent
                    if not are_states_equivalent(next_state1, next_state2):
                        equivalence_classes[state1][state2] = False
                        changed = True
                        break
                    # jika sama sama menuju non accepting state
                    elif (set(next_state1) not in dfa.final_states & set(next_state2) not in dfa.final_states):
                        for symbol1 in dfa.input_symbols:
                            next_state1_1 = get_next_state(state1, symbol1, dfa.transitions)
                            next_state2_1 = get_next_state(state2, symbol1, dfa.transitions)
                            for symbol2 in dfa.input_symbols:
                                next_state1_2 = get_next_state(next_state1_1, symbol2, dfa.transitions)
                                next_state2_2 = get_next_state(next_state2_1, symbol2, dfa.transitions)
                                # next tidak equivalent = salah satu next state adalah final state
                                # maka kedua state tidak equivalent
                                if not are_states_equivalent(next_state1_2, next_state2_2):
                                    equivalence_classes[state1][state2] = False
                                    changed = True
                                    break

            if changed:
                break
        if not changed:
            break

    print("table filling result : ")
    for state1 in sorted(reachable_states):
        print(state1, end=" ")
        for state2 in sorted(reachable_states):
            print(str(equivalence_classes[state1][state2]), end=" ")
            if (state1 == state2): break
        print("\n")
    for state in sorted(reachable_states): print(" st " + state, end=" ")
    print("")

    # 3. equivalence group
    equivalence_group = {}
    for state1 in reachable_states:
        if state1 not in equivalence_group.keys():
            equivalence_group[state1] = state1
        for state2 in reachable_states:
            if state1 != state2 and equivalence_classes[state1][state2]:
                equivalence_group[state2] = equivalence_group[state1]
    print ("equivalence group: ", end="")
    print(equivalence_group)

    new_states = set()
    new_final_states = set()
    new_transitions = {}

    for state in reachable_states:
        new_states.add(equivalence_group[state])
        if state in dfa.final_states:
            new_final_states.add(equivalence_group[state])
    print("new_states", end="")
    print(new_states)

    for state in reachable_states:
        for symbol in dfa.input_symbols:
            next_state = dfa.transitions[state][symbol]
            if equivalence_group[state] not in new_transitions:
                new_transitions[equivalence_group[state]] = {}
            next_state_new = equivalence_group[next_state]
            new_transitions[equivalence_group[state]][symbol] = next_state_new
    
    new_dfa = DFA(
        states=new_states,
        input_symbols=dfa.input_symbols,
        transitions=new_transitions,
        initial_state=str(equivalence_group[dfa.initial_state]),
        final_states=new_final_states
    )

    return new_dfa

def nomor_3_run(input_dfa):
    initial_dfa = input_dfa
    minimized_dfa = minimize_dfa(initial_dfa)
    return minimized_dfa