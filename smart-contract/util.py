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
import datetime
import hashlib
from datetime import datetime

def get_config():
    with open('./config.json', 'r') as f:
        str_config = f.read()
    config = json.loads(str_config)
    return config

def get_id(username ,contract_name):
    str_now = datetime.now().strftime("%Y%m%d%H%M%S")
    str_id = username + contract_name + str_now
    str_hash = hashlib.sha256(str_id.encode()).hexdigest()
    return str_hash[-8:]

if __name__ == '__main__':
    print(get_config())
    print(get_id("zyj", "hangkong"))