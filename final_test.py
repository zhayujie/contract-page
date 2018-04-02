# -*- coding: utf-8 -*
import requests
import json
import hashlib
import rsa
import base64

'''
# sudo easy_install pycrypto
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
'''

URL = 'http://localhost:4000/'
#CREATE_TIME = '2018-03-21 09:41:30'
CREATE_TIME = '2018-03-23 18:10:00'
#CHANNEL_NAME = 'airtrip-union'
CHANNEL_NAME = 'mychannel'

#CHAINCODE_NAME = ‘airtrip’
CHAINCODE_NAME = '500'

#ORG_NAME = 'jetair'
ORG_NAME = 'org1'

#CHAINCODE_PATH = 'airtrip.com'
CHAINCODE_PATH = 'github.com/asset'

HEADER = ''


def enroll_admin():
    payload = {"username": "admin", "orgName": ORG_NAME, "pass": "123"}
    r = requests.post(URL+'users', data=payload)
    return r.json()['token']

def install_chaincode(): 
    payload = {"peers": ["peer1", "peer2"], "chaincodeName": CHAINCODE_NAME, "chaincodePath": CHAINCODE_PATH,
               "chaincodeVersion": "v0"}
    data = json.dumps(payload)
    r = requests.post(URL+"chaincodes", data=data, headers=HEADER)


def instantiate_chaincode():
    payload = {"chaincodeName": CHAINCODE_NAME, "chaincodeVersion": "v0", "fcn": "Init", "args": ""}
    data = json.dumps(payload)
    r = requests.post(URL+"channels/"+CHANNEL_NAME+"/chaincodes", data=data, headers=HEADER)


def create_org_certificate(data):
    r = requests.post(URL+"channels/"+CHANNEL_NAME+"/chaincodes/"+CHAINCODE_NAME+"/createOrgCertificate", data=data, headers=HEADER)
    return r.json()  


def create_individual_certificate(data):
    r = requests.post(URL+"channels/"+CHANNEL_NAME+"/chaincodes/"+CHAINCODE_NAME+"/createIndividualCertificate", data=data, headers=HEADER)
    return r.json()


def create_asset(data):
    url = URL + "channels/"+CHANNEL_NAME+"/chaincodes/"+ CHAINCODE_NAME + "/asset"
    r = requests.post(url, data=data, headers=HEADER)
    return r.text

def transaction(tx_args):
    url = URL + 'channels/'+CHANNEL_NAME+'/chaincodes/'+ CHAINCODE_NAME + '/transaction'
    r = requests.post(url, data=tx_args, headers=HEADER)
    return r.text

def hash(data):
    return hashlib.sha256(hashlib.sha256(data.encode()).hexdigest().encode()).hexdigest()


if __name__ == '__main__':
    # enroll admin
    token = enroll_admin()
    print('Admin eroll sucessfully!\ntoken:\n' + token + '\n')
    # print(token)
    HEADER = {"authorization": "Bearer "+token, "content-type": "application/json"}

    # create the cert of EastAL  
    args1 = {"certType":"1","account":"EastAL","desc1":"East Airline","desc2":"","createTime":CREATE_TIME}
    args1 = json.dumps({"fcn":"createAsset","args":json.dumps(args1)})    
    d1 = create_org_certificate(args1)
    pubkey1 = d1['pubKey']
    prikey1 = d1['privateKeyPEM']
    cert1 = d1["certPEM"]
    print('EastAL pubkey:\n' + pubkey1)
    print('\nEastAL privateKey:\n' + prikey1)
    print('EastAL cert:\n' + cert1)

    # create the cert of Market  
    args2 ={"certType": "2", "account": "Market", "desc1": "A Market",
        "desc2": "", "createTime": CREATE_TIME}
    args2 = json.dumps({"fcn": "createAsset", "args": json.dumps(args2)})    
    d2 = create_org_certificate(args2)
    pubkey2 = d2['pubKey']
    prikey2 = d2['privateKeyPEM']
    cert2 = d2["certPEM"]
    print('Market pubkey:\n' + pubkey2)
    print('\nMarket privateKey:\n' + prikey2)
    print('Market cert:\n' + cert2)

    # create the cert of User
    args3 = {"account":"Zhangsan","desc1":"Zhangsan’s certificate","desc2":"", 
        "createTime": CREATE_TIME}
    args3 = json.dumps({"fcn": "createAsset", "args": json.dumps(args3)})    
    d3 = create_individual_certificate(args3)    
    print(d3)
    pubkey3 = d3['pubKey']
    prikey3 = d3['privateKeyPEM']
    cert3 = d3['certPEM']
    print('User pubkey:\n' + pubkey3)
    print('\nUser privateKey:\n' + prikey3)
    print('User cert:\n' + cert3)
    
    # EastAL creates the asset
    originalNo = "1"
    desc = "10"
    expiry_date = "2019-03-21 09:30:30"
    asset_id = hash(pubkey1 + originalNo + desc + expiry_date)
    # sign
    #priKey = rsa.PrivateKey.load_pkcs1(eastal_private_key.encode())
    #signature = base64.b64encode(rsa.sign(asset_id.encode(), priKey, 'SHA-256'))
    args5 = {"assetID":asset_id,"issuerPK":pubkey1,"originalNo":"1","desc":"10","expiryDate":"2019-03-21 09:30:30","privateKeyPEM":prikey1}
    args5 = json.dumps({"fcn":"createAsset","args":json.dumps(args5)})
    r1 = create_asset(args5)
    print("Create the asset sucessfully!\n" + r1)

    # EastAl issues the asset (->institution)
    version = "1"
    desc = "0"
    tx_type = "1"
    prev_out = ""
    tx_id = hash(asset_id + version + desc + tx_type + prev_out + pubkey1)

    # sign
    # tx_signature = base64.b64encode(sa.sign(tx_id.encode(), priKey, 'SHA-256'))
    tx_args = {"assetID":asset_id,"tx_id":tx_id,"version":version,"desc":desc,"txType":tx_type,"in":{"prev_out":prev_out},"out":pubkey1,"privateKeyPEM":prikey1}
    tx_args = json.dumps({"fcn": "createTransaction", "args": json.dumps(tx_args)})
    r2 = transaction(tx_args)
    print("\nIssues the asset sucessfully!\n" + r2)



    # asset enter in market（institution->market）
    












