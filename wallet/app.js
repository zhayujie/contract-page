/**
 * Copyright 2017 IBM All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the 'License');
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an 'AS IS' BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
'use strict';
var log4js = require('log4js');
var iconv = require('iconv-lite')
var logger = log4js.getLogger('SampleWebApp');
var express = require('express');
var sleep = require('sleep');
var session = require('express-session');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var http = require('http');
var util = require('util');
var app = express();
var expressJWT = require('express-jwt');
var jwt = require('jsonwebtoken');
var bearerToken = require('express-bearer-token');
var cors = require('cors');
var date = require('date-and-time');
var sd = require('silly-datetime');
require('./config.js');
var hfc = require('fabric-client');

var helper = require('./app/helper.js');
var channels = require('./app/create-channel.js');
var join = require('./app/join-channel.js');
var install = require('./app/install-chaincode.js');
var instantiate = require('./app/instantiate-chaincode.js');
var invoke = require('./app/invoke-transaction.js');
var crypto = require('./app/cryptoTools.js');
var cryptos = require('crypto');
var query = require('./app/query.js');
var host = process.env.HOST || hfc.getConfigSetting('host');
var port = process.env.PORT || hfc.getConfigSetting('port');
var fs = require('fs-extra');
//var sleep = require('sleep');
var peerName = 'peer1'



function signer(algorithm,key,data){
    var sign = cryptos.createSign(algorithm);
    sign.update(data);
    var sig = sign.sign(key, 'hex');
    return sig;
}

function verify(algorithm,pubkey,sig,data){
    var verify = cryptos.createVerify(algorithm);
    verify.update(data);
    return verify.verify(pubkey, sig, 'hex')
}







    
//TODO  we need to use pub_key and private_key to replace req
function packageAsset(assetID, issuerPK, originalNo, desc, expiryDate,issuerSIG, req){
 	
	var cryptoContent = helper.getKey(req.username, req.orgname);
	var json_asset = {
                "docType":"",
     		"assetID": "",
     		"issuerPK": "",
     		"originalNo": "",
     		"desc": "",     	
		"expiryDate": "", 
    		"issuerSIG": "", 
                "assetTime":"",  	
    	};
	var assetTime = sd.format(new Date(), 'YYYY-MM-DD HH:mm:ss');
	json_asset["docType"] = "asset";
	json_asset["assetID"] = assetID; 
	json_asset["issuerPK"] = issuerPK;
	json_asset["originalNo"] = originalNo;
	json_asset["desc"] = desc;
	json_asset["expiryDate"] = expiryDate;
	json_asset["issuerSIG"] = issuerSIG;
	json_asset["assetTime"] = assetTime;
	logger.debug("the full asset is :" + JSON.stringify(json_asset));
	return JSON.stringify(json_asset);
}

function packageTx(assetID,tx_id, version,desc,txType,prev_out,scriptSig, tx_out,TxTime, req){	
	//var cryptoContent = helper.getKey(req.username, req.orgname);
	var json_Tx = {
                "docType":"",
     		"tx_id": "",
     		"assetID": "",
     		"version": "",
     		"txType": "",
     		"desc": "",     	
		"tx_in": "", 
    		"tx_out": "", 
                "tx_time":"",  	
    	};

	var TxTime = sd.format(new Date(), 'YYYY-MM-DD HH:mm:ss');
	json_Tx["docType"] = "transaction";
	json_Tx["assetID"] = assetID; 
	json_Tx["tx_id"] = tx_id;
	json_Tx["version"] = version;
	json_Tx["desc"] = desc;
	json_Tx["txType"] = txType;
	json_Tx["tx_in"] = {"prev_out":prev_out,"scriptSig":scriptSig};
	json_Tx["tx_out"] = tx_out;
	json_Tx["tx_time"] = TxTime;

	logger.debug("the full asset is :" + JSON.stringify(json_Tx));
	return JSON.stringify(json_Tx);
} 

///////////////////////////////////////////////////////////////////////////////
//////////////////////////////// SET CONFIGURATONS ////////////////////////////
///////////////////////////////////////////////////////////////////////////////
app.options('*', cors());
app.use(cors());
//support parsing of application/json type post data
app.use(bodyParser.json());
//support parsing of application/x-www-form-urlencoded post data
app.use(bodyParser.urlencoded({
	extended: false
}));
// set secret variable
app.set('secret', 'thisismysecret');
app.use(expressJWT({
	secret: 'thisismysecret'
}).unless({
	path: ['/users']
}));
app.use(bearerToken());
app.use(function(req, res, next) {
	if (req.originalUrl.indexOf('/users') >= 0) {
		return next();
	}

	var token = req.token;
	jwt.verify(token, app.get('secret'), function(err, decoded) {
		if (err) {
			res.send({
				success: false,
				message: 'Failed to authenticate token. Make sure to include the ' +
					'token returned from /users call in the authorization header ' +
					' as a Bearer token'
			});
			return;
		} else {
			// add the decoded user name and org name to the request object
			// for the downstream code to use
			req.username = decoded.username;
			req.orgname = decoded.orgName;
			logger.debug(util.format('Decoded from JWT token: username - %s, orgname - %s', decoded.username, decoded.orgName));
			return next();
		}
	});
});

///////////////////////////////////////////////////////////////////////////////
//////////////////////////////// START SERVER /////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
var server = http.createServer(app).listen(port, function() {});
logger.info('****************** SERVER STARTED ************************');
logger.info('**************  http://' + host + ':' + port +
	'  ******************');
server.timeout = 240000;

function getErrorMessage(field) {
	var response = {
		success: false,
		message: field + ' field is missing or Invalid in the request'
	};
	return response;
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////// REST ENDPOINTS START HERE ///////////////////////////
///////////////////////////////////////////////////////////////////////////////
// Register and enroll user
app.post('/users', function(req, res) {
	var username = req.body.username;
	var orgName = req.body.orgName;
        //var args = req.body.args;
     var password = req.body.password;
	logger.debug('End point : /users');
	logger.debug('User name : ' + username);
	logger.debug('Org name  : ' + orgName);
        if (password!='123') {
                res.json(getErrorMessage('\'password\''));
                return;
        }
	if (!username) {
		res.json(getErrorMessage('\'username\''));
		return;
	}
	if (!orgName) {
		res.json(getErrorMessage('\'orgName\''));
		return;
	}
	var token = jwt.sign({
		exp: Math.floor(Date.now() / 1000) + parseInt(hfc.getConfigSetting('jwt_expiretime')),
		username: username,
		orgName: orgName
	}, app.get('secret'));
	helper.getRegisteredUsers(username, orgName, true).then(function(response) {
		//if (response && typeof response !== 'string') {
			var json_res = JSON.parse(response);
			json_res.token = token;
			res.status(200).send(JSON.stringify(json_res));
		//} else {
		//	res.json({
		//		success: false,
		//		message: response
		//	});
		//}
	});
});

// Create Channel
app.post('/channels', function(req, res) {
	logger.info('<<<<<<<<<<<<<<<<< C R E A T E  C H A N N E L >>>>>>>>>>>>>>>>>');
	logger.debug('End point : /channels');
	var channelName = req.body.channelName;
	var channelConfigPath = req.body.channelConfigPath;
	logger.debug('Channel name : ' + channelName);
	logger.debug('channelConfigPath : ' + channelConfigPath); //../artifacts/channel/mychannel.tx
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
	}
	if (!channelConfigPath) {
		res.json(getErrorMessage('\'channelConfigPath\''));
		return;
	}

	channels.createChannel(channelName, channelConfigPath, req.username, req.orgname)
	.then(function(message) {
		res.send(message);
	});
});
// Join Channel
app.post('/channels/:channelName/peers', function(req, res) {
	logger.info('<<<<<<<<<<<<<<<<< J O I N  C H A N N E L >>>>>>>>>>>>>>>>>');
	var channelName = req.params.channelName;
	var peers = req.body.peers;
	logger.debug('channelName : ' + channelName);
	logger.debug('peers : ' + peers);
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
	}
	if (!peers || peers.length == 0) {
		res.json(getErrorMessage('\'peers\''));
		return;
	}

	join.joinChannel(channelName, peers, req.username, req.orgname)
	.then(function(message) {
		res.send(message);
	});
});
// Install chaincode on target peers
app.post('/chaincodes', function(req, res) {
	logger.debug('==================== INSTALL CHAINCODE ==================');
	var peers = req.body.peers;
	var chaincodeName = req.body.chaincodeName;
	var chaincodePath = req.body.chaincodePath;
	var chaincodeVersion = req.body.chaincodeVersion;
	logger.debug('peers : ' + peers); // target peers list
	logger.debug('chaincodeName : ' + chaincodeName);
	logger.debug('chaincodePath  : ' + chaincodePath);
	logger.debug('chaincodeVersion  : ' + chaincodeVersion);
	if (!peers || peers.length == 0) {
		res.json(getErrorMessage('\'peers\''));
		return;
	}
	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!chaincodePath) {
		res.json(getErrorMessage('\'chaincodePath\''));
		return;
	}
	if (!chaincodeVersion) {
		res.json(getErrorMessage('\'chaincodeVersion\''));
		return;
	}

	install.installChaincode(peers, chaincodeName, chaincodePath, chaincodeVersion, req.username, req.orgname)
	.then(function(message) {
		res.send(message);
	});
});
// Instantiate chaincode on target peers
app.post('/channels/:channelName/chaincodes', function(req, res) {
	logger.debug('==================== INSTANTIATE CHAINCODE ==================');
	var chaincodeName = req.body.chaincodeName;
	var chaincodeVersion = req.body.chaincodeVersion;
	var channelName = req.params.channelName;
	var fcn = req.body.fcn;
	logger.debug('channelName  : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	logger.debug('chaincodeVersion  : ' + chaincodeVersion);
	logger.debug('fcn  : ' + fcn);
	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!chaincodeVersion) {
		res.json(getErrorMessage('\'chaincodeVersion\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
	}
	instantiate.instantiateChaincode(channelName, chaincodeName, chaincodeVersion, fcn, req.username, req.orgname)
	.then(function(message) {
		res.send(message);
	});
});

//createOrgCertificate
app.post('/channels/:channelName/chaincodes/:chaincodeName/createOrgCertificate', function(req, res) {
         logger.debug('==================== CREATE CERTIFICATE ==================');
	 var peers = req.body.peers;
	 var chaincodeName = req.params.chaincodeName;
	 var channelName = req.params.channelName;
         var args = req.body;
         // console.dir(args)
         // var args =JSON.parse(args);
         var certType = args["certType"];	
         var account = args["account"];
         var desc1 = args["desc1"];
         var desc2 = args["desc2"];
         var createTime = args["createTime"];
         logger.debug('account : ' + account);
         logger.debug('certType : ' + certType);
         logger.debug('desc1 : ' + desc1);
         logger.debug('desc2 : ' + desc2);
         logger.debug('createTime : ' + createTime);
         logger.debug('channelName : ' + channelName);
         var userName = account;
         var userOrg = req.orgname; 
         helper.getRegisteredUsers(userName, userOrg, true).then(function(response) {
             var json_user = JSON.parse(response);
             var signingIdentity = json_user.enrollment.signingIdentity;
             var cert =json_user.enrollment.identity.certificate.toString();
            query.queryChaincode(peers, channelName, chaincodeName, cert, "getPubKey", req.username, req.orgname)
                 .then(function(certs){
                        var org = userOrg;
                        var pubKey  = iconv.decode(certs, 'hex');	
                        var keyPath = "/tmp/fabric-client-kvs_peer" + org + "\/" + signingIdentity + '-priv';
                        var keyPEM = fs.readFileSync(keyPath).toString();
                        var cryptoContent = {
                                    pubKey: pubKey,
                                    privateKeyPEM: keyPEM,
                                    certPEM: cert,
                                    };
                        logger.debug('getUserKey: cryptoContent : ' + JSON.stringify(cryptoContent));
                        var certs =JSON.stringify(cryptoContent);
                      return certs;    
               }).then(function(certs){
                  var json_certs = JSON.parse(certs)
                  var keyData = "ORG-certificate####" + account;
                  var certData =　{
                            cert:json_certs["certPEM"],
                            pubkey:json_certs["pubKey"],
                            certType:certType,
                            account:account,
   	                    desc1:desc1,
                            desc2:desc2,
                            createTime:createTime,
                           };
                    var args = JSON.stringify(certData);
                   invoke.invokeChaincode(peers, channelName, chaincodeName, "saveCertificate", args, userName, userOrg)
                         .then(function(message) {	
                                res.status(200).send(certs); 	
                           });
              });                 
        }); 
});

//createIndividualCertificate
app.post('/channels/:channelName/chaincodes/:chaincodeName/createIndividualCertificate', function(req, res) {
         logger.debug('==================== CREATE IndividualCertificate ==================');
	 var peers = req.body.peers;
	 var chaincodeName = req.params.chaincodeName;
	 var channelName = req.params.channelName;
         var args = req.body;
         // var args =JSON.parse(args);
         var certType = '3';	
         var account = args["account"];
         var desc1 = args["desc1"];
         var desc2 = args["desc2"];
         var createTime = args["createTime"];
         logger.debug('account : ' + account);
         logger.debug('certType : ' + certType);
         logger.debug('desc1 : ' + desc1);
         logger.debug('desc2 : ' + desc2);
         logger.debug('createTime : ' + createTime);
         logger.debug('channelName : ' + channelName);
         var userName = account;
         var userOrg = req.orgname; 
         helper.getRegisteredUsers( userName, userOrg, true).then(function(response) {
             var json_user = JSON.parse(response);
             var signingIdentity = json_user.enrollment.signingIdentity;
             var cert =json_user.enrollment.identity.certificate.toString();
            query.queryChaincode(peers, channelName, chaincodeName, cert, "getPubKey", req.username, req.orgname)
                 .then(function(certs){
                        var org = userOrg;
                        var pubKey  = iconv.decode(certs, 'hex');	
                        var keyPath = "/tmp/fabric-client-kvs_peer" + org + "\/" + signingIdentity + '-priv';
                        var keyPEM = fs.readFileSync(keyPath).toString();
                        var cryptoContent = {
                                    pubKey: pubKey,
                                    privateKeyPEM: keyPEM,
                                    certPEM: cert,
                                    };
                        logger.debug('getUserKey: cryptoContent : ' + JSON.stringify(cryptoContent));
                        var certs =JSON.stringify(cryptoContent);
                      return certs;    
               }).then(function(certs){
                  var json_certs = JSON.parse(certs)
                  var keyData = "ORG-certificate####" + account;
                  var certData =　{
                            cert:json_certs["certPEM"],
                            pubkey:json_certs["pubKey"],
                            certType:'3',
                            account:account,
   	                    desc1:desc1,
                            desc2:desc2,
                            createTime:createTime,
                           };
                    var args = JSON.stringify(certData);
                   invoke.invokeChaincode(peers, channelName, chaincodeName, "saveCertificate", args, userName, userOrg)
                         .then(function(message) {	
                                res.status(200).send(certs); 	
                           });
              });                 
        }); 
});

// 获取证书
app.get('/channels/:channelName/chaincodes/:chaincodeName/getCertificate', function(req, res) {
	logger.debug('==================== GetCertificate ==================');
	var channelName = req.params.channelName;
	var chaincodeName = req.params.chaincodeName;
	let args = req.query.account;
	logger.debug('channelName : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	logger.debug('args : ' + args);

	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
        }
	if (!args) {
		res.json(getErrorMessage('\'args\''));
		return;
	}
	logger.debug(args);

	query.queryChaincode(peerName, channelName, chaincodeName, args, 'getCertificate', req.username, req.orgname)
	.then(function(message) {
                logger.debug("result message is:" + message);
		res.status(200).send(message);
	});
});

// 创建资产
app.post('/channels/:channelName/chaincodes/:chaincodeName/asset', function(req, res) {
	logger.debug('==================== Create asset ==================');
	var peers = req.body.peers;
	var chaincodeName = req.params.chaincodeName;
	var channelName = req.params.channelName;
	var args = req.body.assetData;
    var args =JSON.parse(args);
	logger.debug('channelName  : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	logger.debug('args  : ' + args);
	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
	}
	if (!args) {
		res.json(getErrorMessage('\'args\''));
		return;
	}
	var assetID  = args["assetID"];
	var originalNo  = args["originalNo"];
	var desc  = args["desc"];
	var expiryDate  = args["expiryDate"];
        var issuerPK = args["issuerPK"];
        var issuerSIG =args["issuerSIG"];
        //验证assetID
        var data= issuerPK+originalNo+desc+expiryDate;
        var sha256=crypto.createHASH(crypto.createHASH(data));
        logger.debug('sha256  : ' + sha256);
	if (sha256 !== assetID){
		res.status(500).json((getErrorMessage('assetID: wrong hash value'))); 
		return;
	}
	query.queryChaincode(peers, channelName, chaincodeName, issuerPK, 'getCertificateByPK', req.username, req.orgname)
	.then(function(issuercert) {
              //用公钥进行验证签名
              var algorithm = 'ecdsa-with-SHA1';
              var result = verify(algorithm,issuercert,issuerSIG,assetID);       
	      if (!result){
		      res.status(500).json((getErrorMessage('verify false')));
                      logger.debug('sha256  : ' + result);
		      return;
	         }
	      var str_asset = packageAsset(assetID, issuerPK, originalNo, desc, expiryDate,issuerSIG, req); 
              logger.debug('str_asset:'+str_asset);
	      invoke.invokeChaincode(peers, channelName, chaincodeName, "createAsset", str_asset, req.username, req.orgname)
	             .then(function(message) {
		         res.status(200).send(message);
	      });
	});                
});

//Transaction
app.post('/channels/:channelName/chaincodes/:chaincodeName/transaction', function(req, res) {
	logger.debug('==================== Transaction ==================');
	var peers = req.body.peers;
	var chaincodeName = req.params.chaincodeName;
	var channelName = req.params.channelName;
	var args = req.body.txData;
    var args =JSON.parse(args);
	logger.debug('channelName  : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	logger.debug('args  : ' + args);
	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
	}
	if (!args) {
		res.json(getErrorMessage('\'args\''));
		return;
	}
	var assetID  = args["assetID"];
	var tx_id  = args["tx_id"]; 
	var version  = args["version"];
	var desc  = args["desc"];
    var txType = args["txType"];
	var prev_out  = args["in"]["prev_out"];
	var tx_out  = args["out"];
    var scriptSig =args["in"]["scriptSig"];
    var data=assetID+version+desc+txType+prev_out+tx_out;
    var sha256=crypto.createHASH(crypto.createHASH(data));
    logger.debug('sha256  : ' + sha256);
	if (sha256 !== tx_id){
		res.status(500).send('tx_id: Wrong hash value'); 
		return;
	}
        if (prev_out != ""){
	query.queryChaincode(peers, channelName, chaincodeName, prev_out, 'getTX', req.username, req.orgname)
	.then(function(Tx) {
		      var Tx = JSON.parse(Tx)
              var outPK = Tx["tx_out"];
	query.queryChaincode(peers, channelName, chaincodeName, outPK, 'getCertificateByPK', req.username, req.orgname)
	     .then(function(Certificate) {
              //用公钥进行验证签名
              var algorithm = 'ecdsa-with-SHA1';
              var result = verify(algorithm,Certificate,scriptSig,tx_id);       
	      if (!result){
		      res.status(500).json((getErrorMessage('verify false')));
                      logger.debug('sha256  : ' + result);
		      return;
	         }
	      var str_tx = packageTx(assetID,tx_id, version,desc,txType,prev_out,scriptSig, tx_out, req);
	     invoke.invokeChaincode(peers, channelName, chaincodeName, "createTransaction", str_tx, req.username, req.orgname)
	             .then(function(message) {
		               res.send(message);
	     });
       });
    });
       }else{
	     var str_tx = packageTx(assetID,tx_id, version,desc,txType,prev_out,scriptSig, tx_out, req);
	     invoke.invokeChaincode(peers, channelName, chaincodeName, "createTransaction", str_tx, req.username, req.orgname)
	             .then(function(message) {
		        res.status(200).send(message);
	     });
      }
});


// GetAsset
app.get('/channels/:channelName/chaincodes/:chaincodeName/getAsset', function(req, res) {
	logger.debug('==================== GetAsset ==================');
	var channelName = req.params.channelName;
	var chaincodeName = req.params.chaincodeName;
	let args = req.query.assetID;
	// let peer = req.query.peer;
	logger.debug('channelName : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	logger.debug('args : ' + args);

	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
        }
	if (!args) {
		res.json(getErrorMessage('\'args\''));
		return;
	}
	logger.debug(args);

	query.queryChaincode(peerName, channelName, chaincodeName, args, 'getAsset', req.username, req.orgname)
	.then(function(message) {
        logger.debug("result message is:" + message);
        if (message[0] == 'E')
			res.status(500).send(message);
		else
			res.status(200).send(message);
	});
});

// GetAssetTX
app.get('/channels/:channelName/chaincodes/:chaincodeName/getAssetTX', function(req, res) {
	logger.debug('==================== GetAssetTX ==================');
	var channelName = req.params.channelName;
	var chaincodeName = req.params.chaincodeName;
	let args = req.query.assetID;
	// let peer = req.query.peer;
	logger.debug('channelName : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	logger.debug('args : ' + args);

	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
        }
	if (!args) {
		res.json(getErrorMessage('\'args\''));
		return;
	}
	logger.debug(args);

	query.queryChaincode(peerName, channelName, chaincodeName, args, 'getAssetTX', req.username, req.orgname)
	.then(function(message) {
        logger.debug("result message is:" + message);
 //		if (message == '[]')
//			res.status(500).send(message);
//		else
			res.status(200).send(message);
	});
});


// GetAssetLastTX
app.get('/channels/:channelName/chaincodes/:chaincodeName/getAssetLastTX', function(req, res) {
	logger.debug('==================== GetAssetLastTX ==================');
	var channelName = req.params.channelName;
	var chaincodeName = req.params.chaincodeName;
	let args = req.query.assetID;
	// let peer = req.query.peer;
	logger.debug('channelName : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	logger.debug('args : ' + args);

	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
        }
	if (!args) {
		res.json(getErrorMessage('\'args\''));
		return;
	}
	logger.debug(args);

	query.queryChaincode(peerName, channelName, chaincodeName, args, 'getAssetLastTX', req.username, req.orgname)
	.then(function(message) {
        logger.debug("result message is:" + message);
  //  	if (message == '')
//			res.status(500).send(message);
//		else
			res.status(200).send(message);
	});
});




// GetAssetStatus
app.get('/channels/:channelName/chaincodes/:chaincodeName/getAssetStatus', function(req, res) {
	logger.debug('==================== GetAssetStatus ==================');
	var channelName = req.params.channelName;
	var chaincodeName = req.params.chaincodeName;
	let args = req.query.assetID;
	// let peer = req.query.peer;
	logger.debug('channelName : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	logger.debug('args : ' + args);

	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
        }
	if (!args) {
		res.json(getErrorMessage('\'args\''));
		return;
	}
	logger.debug(args);

	query.queryChaincode(peerName, channelName, chaincodeName, args, 'getAssetStatus', req.username, req.orgname)
	.then(function(message) {
                logger.debug("result message is:" + message);
            
		if (message[0] == 'E')
			res.status(500).send(message);
		else
			res.status(200).send(message);
	});
});


// GetAssetByOrgTime
app.get('/channels/:channelName/chaincodes/:chaincodeName/getAssetByOrgTime', function(req, res) {
	logger.debug('==================== GetAssetByOrgTime ==================');
	var channelName = req.params.channelName;
	var chaincodeName = req.params.chaincodeName;
	let issuerPK = req.query.issuerPK;
	let startDate = req.query.startDate;
	let endDate = req.query.endDate;
	let args = [issuerPK, startDate, endDate]
	// let args = req.query.args;
	// let peer = req.query.peer;
	logger.debug('channelName : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	// logger.debug('args : ' + args);

	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
        }
	if (!args) {
		res.json(getErrorMessage('\'args\''));
		return;
	}
	logger.debug(args);
        //var publicPem = fs.readFileSync('cert.pem');//获取公钥
        //var issuerPK = publicPem.toString();//获取公钥
        //args[0] =issuerPK;
        //console.log(args[0])
	query.queryChaincode(peerName, channelName, chaincodeName, args, 'getAssetByOrgTime', req.username, req.orgname)
	.then(function(message) {
        logger.debug("result message is:" + message);
    //    if (message == '[]')
//			res.status(500).send(message);
//		else
			res.status(200).send(message);
	});
});



// GetAssetByOrgExpiry
app.get('/channels/:channelName/chaincodes/:chaincodeName/getAssetByOrgExpiry', function(req, res) {
	logger.debug('==================== GetAssetByOrgExpiry ==================');
	var channelName = req.params.channelName;
	var chaincodeName = req.params.chaincodeName;
	let issuerPK = req.query.issuerPK;
	let optCode = req.query.optCode;
	let expiryDate = req.query.expiryDate;
	let args = [issuerPK, optCode, expiryDate];
	// let peer = req.query.peer;
	logger.debug('channelName : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	// logger.debug('args : ' + args);

	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
        }
	if (!args) {
		res.json(getErrorMessage('\'args\''));
		return;
	}
	logger.debug(args);

	query.queryChaincode(peerName, channelName, chaincodeName, args, 'getAssetByOrgExpiry', req.username, req.orgname)
	.then(function(message) {
                logger.debug("result message is:" + message);
  //    	if (message == '[]')
//			res.status(500).send(message);
//		else
			res.status(200).send(message);
	});
});




// GetAssetsByUser
app.get('/channels/:channelName/chaincodes/:chaincodeName/getAssetsByUser', function(req, res) {
	logger.debug('==================== GetAssetsByUser ==================');
	var channelName = req.params.channelName;
	var chaincodeName = req.params.chaincodeName;
	let args = req.query.pubKey;
	// let peer = req.query.peer;
	logger.debug('channelName : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	logger.debug('args : ' + args);

	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
        }
	if (!args) {
		res.json(getErrorMessage('\'args\''));
		return;
	}
	logger.debug(args);

	query.queryChaincode(peerName, channelName, chaincodeName, args, 'getAssetsByUser', req.username, req.orgname)
	.then(function(message) {
                logger.debug("result message is:" + message);
        
		res.status(200).send(message);
	});
});

// GetTXNum
app.get('/channels/:channelName/chaincodes/:chaincodeName/getTXNum', function(req, res) {
	logger.debug('==================== GetTXNum ==================');
	var channelName = req.params.channelName;
	var chaincodeName = req.params.chaincodeName;
	let u = req.query.unit;
	let n = req.query.num;
	let args = [u, n];
	// let peer = req.query.peer;
	logger.debug('channelName : ' + channelName);
	logger.debug('chaincodeName : ' + chaincodeName);
	// logger.debug('args : ' + args);

	if (!chaincodeName) {
		res.json(getErrorMessage('\'chaincodeName\''));
		return;
	}
	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
        }
	if (!args) {
		res.json(getErrorMessage('\'args\''));
		return;
	}
	logger.debug(args);
        var unit =args[0];
        var num =args[1];
        var timeArr = [];
        timeArr[1] = new Date()
        if (unit==1){
             timeArr[0] = date.addHours(timeArr[1], -num);
             timeArr[1] = sd.format(new Date(timeArr[1]), 'YYYY-MM-DD HH:mm:ss');
             timeArr[0] = sd.format(new Date(timeArr[0]), 'YYYY-MM-DD HH:mm:ss');
        }
        else{
             timeArr[0] = date.addDays(timeArr[1], -num);
             timeArr[1] = sd.format(new Date(timeArr[1]), 'YYYY-MM-DD HH:mm:ss');
             timeArr[0] = sd.format(new Date(timeArr[0]), 'YYYY-MM-DD HH:mm:ss');
        }
        console.log(timeArr)
	query.queryChaincode(peerName, channelName, chaincodeName, timeArr, 'getTXNum', req.username, req.orgname)
	.then(function(message) {
        logger.debug("result message is:" + message);
         
		res.status(200).send(message);
	});
});

//GetBlkNum
app.get('/channels/:channelName', async function(req, res) {
	logger.debug(
		'================ GetBlkNum ======================');
	logger.debug('channelName : ' + req.params.channelName);
	// let peer = req.query.peer;
	/*
	query.getChainInfo(peerName, req.username, req.orgname).then(
		function(message) {
            var BlockHeight =message["height"]["low"];       
			res.status(200).send((BlockHeight).toString());
		});
		*/
	var message = await query.getChainInfo(peerName, req.username, req.orgname)
	let BlockHeight = message["height"]["low"]; 
	res.send(BlockHeight.toString())
});

// GetPeersInfo
/*E.g. 
{
	"number": 2,
	"peers": [{
		"name": "peer0.jetair.example.com",
		"addr": "localhost:7051"
	}, 
	{
		"name": "peer1.jetair.example.com",
		"addr": "localhost:7056"
	}]
}
*/
app.get('/channels/:channelName/getPeersInfo', function(req, res) {
	logger.debug('================ GetPeersInfo ======================');

	var channelName = req.params.channelName;
	logger.debug('channelName : ' + channelName);

	if (!channelName) {
		res.json(getErrorMessage('\'channelName\''));
		return;
    }

	var channel = helper.getChannelForOrg(req.orgname);
	let peers = channel.getPeers(channelName)
	
	if (!peers) {
		res.status(500).send('No peers!');
		return;
	}

	var peers_info = []
	for (let peer of peers) { 
		let addr = peer['_endpoint']['addr']
		let name = peer['_options']['grpc.default_authority'];
		peers_info.push({'name':name, 'addr':addr})
	}
	var peers_res = {"number":peers_info.length, "peers":peers_info}

	logger.debug("Get peers info successfully");
	     
	res.status(200).send(JSON.stringify(peers_res));
	
});


// Get the number of blocks generated over a period of time
app.get('/channels/:channelName/GetBlockNumByTime', async function(req, res) {
	logger.debug('================ GetBlockNumByTime ======================');

	var channelName = req.params.channelName;
	let startDate = req.query.startDate;
	let endDate = req.query.endDate;
	logger.debug('channelName : ' + channelName);

	if (!channelName) {
		res.status(500).json(getErrorMessage('\'channelName\''));
		return;
    }
    if (!startDate || !endDate) {
    	res.status(500).json(getErrorMessage('\'lack args\''));
		return;
    }
    if (startDate >= endDate) {
    	res.status(500).json(getErrorMessage('\'Invalid args\''));
		return;
    }
    startDate = Date.parse(startDate)
    endDate = Date.parse(endDate)
    if (isNaN(startDate) || isNaN(endDate)) {
    	res.status(500).json(getErrorMessage('\'Invalid args\''));
		return;
    }
  	/*
    query.getBlockNumByTime(peerName, startDate, endDate, req.username, req.orgname).then(function(num) {
        logger.debug("Block number is: " + num);
        res.status(200).send(num.toString());
	});
	*/
	var num = await query.getBlockNumByTime(peerName, startDate, endDate, req.username, req.orgname);
	res.status(200).send(num.toString());
});