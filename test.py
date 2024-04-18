class DFA:
    def __init__(self, states, input_symbols, transitions, initial_state, final_states):
        self.states = states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states

    def make_table(self):
        # Inisialisasi tabel dengan header
        table = [[''] + list(self.input_symbols)]  # Ubah input_symbols menjadi list

        # Tambahkan baris untuk setiap state
        for state in self.states:
            row = [state]
            for symbol in self.input_symbols:
                # Cari transisi dari state saat ini dengan input symbol
                next_state = self.transitions.get((state, symbol), None)
                if next_state:
                    row.append(next_state)
                else:
                    row.append('-')  # Jika tidak ada transisi, tandai dengan '-'
            table.append(row)

        return table

# Contoh penggunaan:
states = {'q0', 'q1', 'q2'}
input_symbols = {'0', '1'}
transitions = {('q0', '0'): 'q1', ('q0', '1'): 'q2', ('q1', '0'): 'q2', ('q1', '1'): 'q0', ('q2', '0'): 'q0', ('q2', '1'): 'q1'}
initial_state = 'q0'
final_states = {'q0'}

dfa = DFA(states, input_symbols, transitions, initial_state, final_states)
table = dfa.make_table()

# Cetak tabel
for row in table:
    print(' '.join(row))
