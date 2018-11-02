//BCMETH means Blockchain Match Ethereum 
pragma solidity ^0.4.24;

contract BCMETH {
    String currentStatus;
    constructor () public {
        currentStatus="[1]";
    }

    function timeout0(String actionStr) public returns(bool){
        if(currentStatus=="[1]" && action=="timeout0"){
            currentStatus="[5]";
            return true;
        }
        else
            return false;
    }

    function sf(String actionStr) public returns(bool){
        if(currentStatus=="[1]" && action=="timeout0"){
            currentStatus="[5]";
            return true;
        }
        else
            return false;
    }

    function ssf(String actionStr) public returns(bool){
        if(currentStatus=="[1]" && action=="timeout0"){
            currentStatus="[5]";
            return true;
        }
        else
            return false;
    }

    function vio2018-10-05(String actionStr) public returns(bool){
        if(currentStatus=="[1]" && action=="timeout0"){
            currentStatus="[5]";
            return true;
        }
        else
            return false;
    }

}