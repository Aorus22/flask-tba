from nomor_1 import nomor_1_run
from nomor_2 import nomor_2_run
from nomor_3 import nomor_3_run
from nomor_4 import nomor_4_run
from nomor_5 import create_automata, make_svg
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/nomor_1', methods=['POST'])
def nomor_1():
    data = request.json

    svg1, svg2 = nomor_1_run(data)

    return jsonify({'result1': f'{svg1}', 'result2': f'{svg2}'})


@app.route('/draw_diagram', methods=['POST'])
def draw_diagram():
    data = request.json
    automata = create_automata(data)
    svg_result = make_svg(automata)
    return jsonify({'svgResult': svg_result})


@app.route('/nomor_2', methods=['POST'])
def nomor_2():
    data = request.json
    input_regex = data['regexp']
    svg_result = nomor_2_run(input_regex)

    return jsonify({'svgResult': svg_result})


@app.route('/nomor_3', methods=['POST'])
def nomor_3():
    data = request.json
    strings = data['strings']
    svg_result = nomor_3_run(data)
    result1 = create_automata(data).accepts_input(strings)
    result2 = False

    return jsonify({'svgResult': f'{svg_result}', 'result1': f'{result1}', 'result2': f'{result2}'})


@app.route('/nomor_4', methods=['POST'])
def nomor_4():
    data = request.json

    dfa1 = data["dfa1"]
    dfa2 = data["dfa2"]

    print(dfa1)
    print(dfa2)

    result = nomor_4_run(dfa1, dfa2)

    return jsonify({'result': f'{result}'})


@app.route('/nomor_5', methods=['POST'])
def nomor_5():
    data = request.json
    automata = create_automata(data)
    strings = data['strings']
    result = automata.accepts_input(strings)
    # svg_result = automata.show_diagram(input_string="1111")
    svg_result = make_svg(automata)
    return jsonify({'svgResult': svg_result, 'result': f'{result}'})


@app.route('/test_nomor_4')
def test_nomor_4():
    data = request.json
    print(data)

    dfa1 = {
        "type": "DFA",
        "states": ["q0", "q1"],
        "alphabet": ["0", "1"],
        "transitions": {
            "q0": {"0": ["q0"], "1": ["q1"]},
            "q1": {"0": ["q0"], "1": ["q1"]}
        },
        "start_state": "q0",
        "accepting_states": ["q1"],
        "strings": "000201"
    }

    dfa2 = {
        "type": "DFA",
        "states": ["q0", "q1"],
        "alphabet": ["0", "1"],
        "transitions": {
            "q0": {"0": ["q0"], "1": ["q1"]},
            "q1": {"0": ["q0"], "1": ["q1"]}
        },
        "start_state": "q0",
        "accepting_states": ["q1"],
        "strings": "000201"
    }

    result = nomor_4_run(dfa1, dfa2)

    return jsonify({'result': f'{result}'})


@app.route('/test_NFA')
def test_NFA():
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

    automata = create_automata(data_test)
    strings = data_test["strings"]
    result = automata.accepts_input(strings)
    svg_result = make_svg(automata)
    # svg_result = automata.show_diagram(input_string="1111")
    return jsonify({'svgResult': svg_result, 'result': f'{result}'})


@app.route('/test_ENFA')
def test_ENFA():
    data_test = {
        "type": "ENFA",
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

    automata = create_automata(data_test)
    strings = data_test["strings"]
    result = automata.accepts_input(strings)
    svg_result = make_svg(automata)
    return jsonify({'svgResult': svg_result, 'result': f'{result}'})


@app.route('/test_DFA')
def test_DFA():
    data_test = {
        "type": "DFA",
        "states": ["q0", "q1"],
        "alphabet": ["0", "1"],
        "transitions": {
            "q0": {"0": ["q0"], "1": ["q1"]},
            "q1": {"0": ["q0"], "1": ["q1"]}
        },
        "start_state": "q0",
        "accepting_states": ["q1"],
        "strings": "000201"
    }

    automata = create_automata(data_test)
    strings = data_test["strings"]
    result = automata.accepts_input(strings)
    svg_result = make_svg(automata)
    automata.show_diagram(input_string="1111")
    return jsonify({'svgResult': svg_result, 'result': f'{result}'})


@app.route('/test_nomor_1')
def test_nomor_1():
    svg1, svg2 = "nomor_1_run()", ""

    return jsonify({'result1': f'{svg1}', 'result2': f'{svg2}'})


@app.route('/test_nomor_3')
def test_nomor_3():
    minimized_dfa = "nomor_3_run()"
    svg_result = make_svg(minimized_dfa)

    return jsonify({'result1': f'{svg_result}'})


if __name__ == '__main__':
    app.run(debug=True)
