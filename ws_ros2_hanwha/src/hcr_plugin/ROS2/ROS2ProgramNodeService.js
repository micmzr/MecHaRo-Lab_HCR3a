const path = require('path');
const ProgramNodeService = require('rodix_api').ProgramNodeService;
const ROS2ProgramNodeContribution = require(path.join(__dirname, 'ROS2ProgramNodeContribution'));

class ROS2ProgramNodeService extends ProgramNodeService{
    constructor(myDaemonSvc){
        super();
        this.myDaemonSvc = myDaemonSvc;
    }

    getIcon() {
        return path.join(__dirname, "htmlStore/resource/ico-rodi-x.png");
    }

    getTitle(){
        return 'ROS2';
    }

    getHTML(){
        return path.join(__dirname, "htmlStore/ROS2ProgramNode.html");
    }

    isDeprecated(){
        return false;
    }

    isChildrenAllowed(){
        return false;
    }
    isThreadAllowed(){
        return false;
    }

    createContribution(rodiAPI, dataModel){
        return new ROS2ProgramNodeContribution(rodiAPI, dataModel, this.myDaemonSvc);
    }

}

module.exports = ROS2ProgramNodeService;
