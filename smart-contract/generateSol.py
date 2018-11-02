import json

def resolveJson(path):
    file = open(path,'r')
    fileJson = json.load(file)
    InitStatus = ''.join(map(str,fileJson['InitStatus']))
    FsmArray=fileJson['FsmArray']
    #print(FsmArray)
    CurrentStatus=[]
    Action=[]
    NewStatus=[]
    for array in FsmArray:
        strCurrentStatus = ''.join(map(str,array['CurrentStatus']))
        CurrentStatus.append(strCurrentStatus)
        Action.append(array['Action'])
        strNewStatus = ''.join(map(str,array['NewStatus']))
        NewStatus.append(strNewStatus)
    return (InitStatus,CurrentStatus,Action,NewStatus)

def transferSolidity(path,fileName):
    file = open(fileName+".sol",'w')
    result=resolveJson(path)
    InitStatus=result[0]
    CurrentStatus=result[1]
    Action=result[2]
    NewStatus=result[3]
    strConfirm='//BCMETH means Blockchain Match Ethereum \npragma solidity ^0.4.24;'+'\n\n'+'contract BCMETH {'+'\n'
    strCurrentStatus='    String currentStatus;\n'
    strConstructor='    constructor () public {\n        currentStatus='+'"'+InitStatus+'"'+';\n    }\n\n'
    strEnd="}"
    strFun='';
    for index in range(len(Action)):
        strFun +='    function '+Action[index]+'(String actionStr) public returns(bool){\n        if(currentStatus=='+'"'+CurrentStatus[0]+'"'+' && action=='+'"'+Action[0]+'"'+'){\n            currentStatus='+'"'+NewStatus[0]+'"'+';\n            return true;\n        }\n        else\n            return false;\n    }\n\n'
    strSol=strConfirm+strCurrentStatus+strConstructor+strFun+strEnd;
    file.write(strSol)
    file.close()

if __name__ == '__main__':
    transferSolidity('./term.json','BCH')


