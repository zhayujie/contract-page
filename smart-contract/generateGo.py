import json
def resolveJson(path):
    file = open(path,'r')
    fileJson = json.load(file)
    InitStatus = fileJson['InitStatus']
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
def transferGo(path, fileName):
    file = open(fileName + ".go", 'w')
    result = resolveJson(path)
    initStatus = result[0]
    currentStatus = result[1]
    action = result[2]
    newStatus = result[3]
    str1 = '//status.go\n\n\n'
    strPackage = 'package main\n\n'
    strImport = 'import (\n  "fmt"\n  "reflect"\n  "io/ioutil"\n  "encoding/json"\n  "github.com/looplab/fsm"\n\n' \
               + '  "github.com/hyperledger/fabric/core/chaincode/shim"\n  pb "github.com/hyperledger/fabric/protos/peer"\n)\n\n\n'
    strInitFSM = 'func InitFSM() *fsm.FSM {\n  var events []fsm.EventDesc = make([]fsm.EventDesc, 0)\n  for i := 0; i < termNum; i ++ {'\
               + '\n    events = append(events, fsm.EventDesc{Name: action[i], Src: []string{currentStatus[i]}, Dst: newStatus[i]})\n  '\
               + '}\n  f := fsm.NewFSM(\n    initStatus,\n    events,\n    fsm.Callbacks{},\n  )\n  return f;\n}\n\n\n'
    strInit = '// =========================================\n//       Init - initializes chaincode\n// =========================================\n'\
               + 'func (c *ContractChaincode) Init(stub shim.ChaincodeStubInterface) pb.Response {\n  return shim.Success(nil)\n}\n\n\n'
    strMain = '// ============\n//     Main\n// ============\nfunc main() {\n  err := shim.Start(new(ContractChaincode))\n  if err != nil {\n'\
               + '    fmt.Printf("Error starting Contract chaincode: %s", err)\n  }\n}\n\n\n'

    invokeArray = []
    invokeStr = ''
    invokeTitle = '// ======================================================\n//       Invoke - Our entry point for Invocations\n'\
               + '// ======================================================\nfunc (c *ContractChaincode) Invoke(stub shim.ChaincodeStubInterface) pb.Response {\n  '\
               + 'function, args := stub.GetFunctionAndParameters()\n\n  '
    for k in range(len(action)):
        invokeArray.append('if function == "' + action[k] + '" {\n    return FsmEvent(stub, args, "' + action[k] + \
               '")\n  } else ')
        invokeStr = invokeStr + invokeArray[k]
    strError = '{\n    return shim.Error("Function doesn\'t exits, make sure function is right!")\n  }\n\n  return shim.Success(nil)\n}\n\n\n'
    strInvoke = invokeTitle + invokeStr + strError

    strFsmEvent = 'func FsmEvent(stub shim.ChaincodeStubInterface, args []string, event string) pb.Response{\n  var ruTest Routers\n'\
               + '  var str string\n  var resError string\n\n  crMap := make(ControllerMapsType, 0)\n  vf := reflect.ValueOf(&ruTest)\n'\
               + '  vft := vf.Type()\n  //读取方法数量\n  mNum := vf.NumMethod()\n\n  //遍历路由器的方法，并将其存入控制器映射变量中\n  for i := 0; i < mNum; i++ {\n'\
               + '    mName := vft.Method(i).Name\n    crMap[mName] = vf.Method(i)\n  }\n\n  policyID := args[0]\n  bstatus, err := stub.GetState(policyID)\n'\
               + '  if err != nil{\n    return shim.Error("Query policy status fail, policy ID: " + policyID)\n  }\n\n  status := string(bstatus)\n'\
               + '  fmt.Println("Policy[" + policyID + "] status:" + status)\n  f := fMap[policyID]\n  err = f.Event(event)\n  if err != nil {\n'\
               + '    return shim.Error("Current status is " + status + " not support envent:" + event)\n  } else if event == "TimeOut" {\n'\
               + '    str = "Done"\n  } else {\n    parms := []reflect.Value{reflect.ValueOf(stub), reflect.ValueOf(args)}\n'\
               + '    result := crMap[event].Call(parms)\n    resError = reflect.Value.String(result[0])\n'\
               + '    str = reflect.Value.String(result[1])\n  }\n\n  if str != "Done" {\n    return shim.Error(resError)\n'\
               + '  }\n\n  stub.PutState(policyID, []byte(status))\n  status = f.Current()\n  fmt.Println("New status:" + status)\n'\
               + '  return shim.Success([]byte(status))\n}\n\n\n'

    funcArray = []
    funcStr = ''
    for i in range(len(action)):
        funcArray.append('func (this *Routers) ' + action[i] + '((stub shim.ChaincodeStubInterface,\nargs []string) (pb.Response, string) {\n'\
                       + '  return shim.Success(nil), "Done"\n}\n\n\n')
        funcStr = funcStr + funcArray[i]

    strSol = strPackage + strImport + strInit + strMain + strInvoke + strInitFSM + strFsmEvent + funcStr
    file.write(strSol)
    file.close()



if __name__ == '__main__':
    transferGo('./term.json','status')
