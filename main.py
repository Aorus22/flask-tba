from nomor_1 import nomor_1_run
from nomor_2 import nomor_2_run
from nomor_3 import nomor_3_run
from nomor_4 import nomor_4_run
from nomor_5 import create_automata, make_svg, draw_path, DFA, ENFA
from flask import Flask, request, jsonify
from flask_cors import CORS
import re


app = Flask(__name__)
CORS(app)


@app.route('/draw_diagram', methods=['POST'])
def draw_diagram():
    data = request.json
    automata = create_automata(data)
    svg_result = make_svg(automata)
    return jsonify({'svgResult': svg_result})


@app.route('/nomor_1', methods=['POST'])
def nomor_1():
    data = request.json
    svg1, svg2 = nomor_1_run(data)
    return jsonify({'result1': f'{svg1}', 'result2': f'{svg2}'})


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

    initial_dfa = create_automata(data)
    result1 = initial_dfa.accepts_input(strings)
    svg_result1 = draw_path(initial_dfa)

    minimized_dfa = nomor_3_run(initial_dfa)
    result2 = minimized_dfa.accepts_input(strings)
    svg_result2 = draw_path(minimized_dfa)

    return jsonify({'svgResult1': f'{svg_result1}', 'svgResult2': f'{svg_result2}', 'result1': f'{result1}', 'result2': f'{result2}'})


@app.route('/nomor_4', methods=['POST'])
def nomor_4():
    data = request.json
    dfa1 = data["dfa1"]
    dfa2 = data["dfa2"]
    result = nomor_4_run(dfa1, dfa2)
    return jsonify({'result': f'{result}'})


@app.route('/nomor_5', methods=['POST'])
def nomor_5():
    data = request.json
    if data['type'] == "REGEX":
        regex = data['start_state']
        strings = data['strings']
        regex = re.compile(regex)
        result = ""
        if regex.fullmatch(strings):
            result = True
        else:
            result = False
        return jsonify({'result': f'{result}'})
    else:
        automata = create_automata(data)
        strings = data['strings']
        result= automata.accepts_input(strings)
        svg_result = ""
        if isinstance(automata, ENFA):
            svg_result = make_svg(automata)
        else:
            svg_result = draw_path(automata)
        return jsonify({'svgResult': svg_result, 'result': f'{result}'})


if __name__ == '__main__':
    app.run(debug=True)
