import re
import pandas as pd
import json
import openai
import os


def table_to_str(table_dict):
    df = pd.DataFrame(table_dict['data'], columns=table_dict['columnnames'])

    result_string = ""

    column_names = df.columns

    result_string += "|" + "|".join(column_names) + "|" + "\n"

    for row in df.values:
        result_string += "|"
        row_strings = ["None" if cell == "" else str(cell) for cell in row]
        row_string = "|".join(row_strings)
        result_string += row_string + "|"
        result_string += "\n"
    return result_string


def coordinate_to_str(coordinate_list):
    desired_list = [[item[0], item[1]] for item in coordinate_list]
    coordinate_str = str(desired_list)
    return coordinate_str


def extract_coordinate(response):
    pattern = r'\[(\d+),\s*(\d+)\] - Reason:\s*(.*?)\n'
    result_list = []
    result_dict = {}

    matches = re.findall(pattern, response)
    for match in matches:
        row = int(match[0])
        column = int(match[1])
        reason = match[2].strip()
        result_list.append([row, column, reason])
    result_dict['coordinate'] = result_list
    result_json = json.dumps(result_dict, ensure_ascii=False)
    return result_json


def extract_coordinate_repair(response):
    pattern = r'\[\[.*?\]\]'
    result_dict = {}
    target_list = re.findall(pattern, response)
    if target_list:
        target_list = eval(target_list[0])
    result_dict['coordinate'] = target_list
    result_json = json.dumps(result_dict, ensure_ascii=False)
    return result_json


def get_answer_from_gpt(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "You are a general knowledge expert, proficient in cleaning dirty data."},
            {"role": "user", "content": prompt}
        ]
    )
    response = completion["choices"][0]["message"]["content"]
    return response

