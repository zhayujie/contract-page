# -*- coding:utf-8 -*-
# config.json
'''
{
    "host": "0.0.0.0",
    "port": "5100",
    "debug": "False",
    "user": "root",
    "password": "md",
    "database": "contract"
}
'''

import json

def get_config():
    with open('./config.json', 'r') as f:
        str_config = f.read()
    config = json.loads(str_config)
    return config

if __name__ == '__main__':
    print(get_config())