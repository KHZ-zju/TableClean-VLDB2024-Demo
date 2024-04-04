from flask import Flask, request, render_template, jsonify
import pandas as pd
import utils

app = Flask(__name__)


table_data_from_server = None
coordinate_from_server = None

# default method:GET
@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('upload.html',  table_data_from_server=table_data_from_server)


@app.route('/process', methods=['POST', 'GET'])
def process():
    global table_data_from_server
    global coordinate_from_server
    global mode_from_server
    if request.method == 'POST':
        if request.content_type == 'application/json':
            table_data_from_server = request.json
            table_str = utils.table_to_str(table_data_from_server)
            with open('./static/txt/prompt_detect.txt', 'r', encoding='utf-8') as file:
                prompt = file.read()
            prompt += table_str
            if table_data_from_server['advice'] is not None:
                prompt += 'Additional message: '
                prompt += str(table_data_from_server['advice'])
            print(prompt)

            response = utils.get_answer_from_gpt(prompt)
            response = response + '\n'
            # print(response)
            coordinate_from_server = utils.extract_coordinate(response)
            # print(coordinate_from_server)

            return 'success'
        else:
            return "Unsupported Media Type", 415

    return render_template('process.html', table_data_from_server=table_data_from_server, coordinate_from_server=coordinate_from_server, mode_from_server='Detection')

@app.route('/process/repair', methods=['POST', 'GET'])
def process_repair():
    global table_data_from_server
    global coordinate_from_server

    if request.method == 'POST':
        if request.content_type == 'application/json':
            coordinate_from_server = request.json['coordinate']
            print(coordinate_from_server)
            table_data_from_server = {key: value for key, value in request.json.items() if key != 'coordinate'}
            table_str = utils.table_to_str(table_data_from_server)
            coordinate_str = utils.coordinate_to_str(coordinate_from_server)
            with open('./static/txt/prompt_repair.txt', 'r', encoding='utf-8') as file:
                prompt = file.read()
            prompt = prompt + table_str + 'Here is the coordinate I provide.\n' + coordinate_str
            if table_data_from_server['advice'] is not None:
                prompt += '\nAdditional message: '
                prompt += str(table_data_from_server['advice'])
            print(prompt)
            response = utils.get_answer_from_gpt(prompt)
            response = response + '\n'
            # print(response)
            coordinate_from_server = utils.extract_coordinate_repair(response)
            # print(coordinate_from_server)

            return 'success'
        else:
            return "Unsupported Media Type", 415

    return render_template('process.html', table_data_from_server=table_data_from_server, coordinate_from_server=coordinate_from_server, mode_from_server='Repair')


if __name__ == '__main__':
    app.run(debug=True)

