import requests
import json
import hashlib
import execjs
import io

URL = 'http://localhost:4000/'
CHAINCODE_NAME = '500'
CHANNEL_NAME = 'mychannel'
HEADER = ''


def enroll():
    payload = {'username': 'Jim', 'orgName': 'org1'}
    r = requests.post("http://localhost:4000/users", data=payload)
    return r.json()['token']


def get_assets(pubkey):
    token = enroll()
    global HEADER
    HEADER = {"authorization": "Bearer " + token, "content-type": "application/json"}
    payload = {'peer': 'peer1', 'args': pubkey}
    r = requests.get(URL + "channels/" + CHANNEL_NAME + "/chaincodes/" + CHAINCODE_NAME + "/getAssetsByUser",
                     params=payload, headers=HEADER)
    return r.text


def get_asset_last_tx(asset_id):
    payload = {'peer': 'peer1', 'args': asset_id}
    r = requests.get(URL + "channels/" + CHANNEL_NAME + "/chaincodes/" + CHAINCODE_NAME + "/getAssetLastTX",
                     params=payload, headers=HEADER)
    return r.text


def hash(*args):
    data = ''
    for st in args:
        data = data + st
    res = hashlib.sha256(hashlib.sha256(data.encode()).hexdigest().encode()).hexdigest()
    return res


def get_js():
    f = io.open('../signer.js', 'r', encoding='UTF-8')
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    return htmlstr


def sign(data, private_key):
    jsstr = get_js()
    ctx = execjs.compile(jsstr)
    args = ['RSA-SHA256', private_key, data]
    return ctx.call('signer', args)


def transaction(asset_id, version, desc, tx_type, prev_out, out, prikey):
    tx_id = hash(asset_id, version, desc, tx_type, prev_out, out)
    signature = sign(tx_id, prikey)
    tx_args = {"assetID": asset_id, "tx_id": tx_id, "version": version, "desc": desc, "txType": tx_type,
               "in": {"prev_out": prev_out, "scriptSig": signature}, "out": out}
    tx_args = json.dumps({"fcn": "createTransaction", "args": json.dumps(tx_args)})
    url = URL + 'channels/' + CHANNEL_NAME + '/chaincodes/' + CHAINCODE_NAME + '/transaction'
    r = requests.post(url, data=tx_args, headers=HEADER)
    return r.text, tx_id
