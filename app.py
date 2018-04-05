from flask import Flask, request, render_template
import bridge
import json
import requests

app = Flask(__name__)
# institution public key
#PUBLIC_KEY = ''
# user private key
USER_PRIVATE_KEY = ''
# user public key
USER_PUB_KEY = ''

asset_list = []

@app.route('/', methods=['GET'])
def signin_form():
    return render_template('form.html'), 200


@app.route('/', methods=['POST'])
def signin():
    global USER_PUB_KEY
    global USER_PRIVATE_KEY
    print(123456)
    USER_PUB_KEY = request.form['pubkey'].strip()
    USER_PRIVATE_KEY = request.form['prikey'].strip()
    try:
        res = bridge.get_assets(USER_PUB_KEY)
        if isinstance(res, str):
            res = json.loads(res)
        else:
            res = json.loads(res.encode())
    except Exception:
        return render_template('error.html'), 500

    else:
        if res:
          #  global PUBLIC_KEY
           # PUBLIC_KEY = res[0]['IssuerPK']
            for a in res:
                asset_list.append(a)
            return render_template('asset.html', list=asset_list), 200
        else:
            return render_template('error.html', message='No assets'), 500


@app.route('/exercise', methods=['GET'])
def exercise():
    index = int(request.args.get('index'))
    print(asset_list)
    asset_id = asset_list[index]['AssetID']
    prev_out = bridge.get_asset_last_tx(asset_id)
    if not isinstance(prev_out, str):
        prev_out = prev_out.encode()
    prev_out = json.loads(prev_out)['tx_id']
    public_key = asset_list[index]['IssuerPK']
    # exercise right
    r, tx_id = bridge.transaction(asset_id, '1', 'exercises rights', '4', prev_out, public_key, USER_PRIVATE_KEY)
    asset_list[index]['Status'] = 2
    return render_template('success.html'), 200


@app.route('/jump', methods=['GET'])
def jump():
   # key = {'pubkey': USER_PUB_KEY, 'prikey': USER_PRIVATE_KEY}
    #print(key)
   # requests.post("http://localhost:5000/", data=key)
    return render_template('asset.html', list=asset_list), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)
