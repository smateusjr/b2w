import json
import os
import yaml


def yaml_to_json(
        yaml_dir,
        json_dir,
        directory="",
        url_base=None,
        response_messages=None
):
    combined = {}
    yaml_path = os.path.join(yaml_dir, directory)
    json_path = os.path.join(json_dir, directory)
    dir_list = []
    for item in os.listdir(os.path.join(yaml_dir, directory)):
        if '.yml' in item:
            with open(os.path.join(yaml_path, item), 'r', encoding='utf-8') as\
                    yamlfile:
                data = yaml.safe_load(yamlfile)
                # Troca o endpoint da aplicacao
                if url_base and item == 'root.yml' and 'basePath' in\
                        data.keys():
                    data['basePath'] = url_base

                # Pega os retornos de erro do conf
                if response_messages and item == 'apis.yml':
                    # Pega todos codigos/msgs do conf
                    http_codes = list()
                    for codes in response_messages:
                        http_codes.append(response_messages[codes])

                    for apis in data:
                        for ib, blocks in enumerate(data[apis]):
                            if 'operations' in blocks:
                                for ip, block in\
                                        enumerate(blocks['operations']):
                                    if 'response_messages' in block:
                                        data[apis][ib]['operations'][ip]\
                                            ['response_messages'] = http_codes

                combined.update(data)
        else:
            dir_list.append(item)
    if not os.path.isdir(json_path):
        os.mkdir(json_path)
    with open(os.path.join(json_path, 'docs.json'), 'w') as json_file:
        json.dump(combined, json_file)
    for new_directory in dir_list:
        yaml_to_json(
            yaml_dir,
            json_dir,
            new_directory,
            url_base,
            response_messages
        )
