const ProgramNodeContribution = require('rodix_api').ProgramNodeContribution;

class ROS2ProgramNodeContribution extends ProgramNodeContribution {
    constructor(rodiAPI, dataModel){
        super();
        this.rodiAPI = rodiAPI;
        this.dataModel = dataModel;
        this.uiHandler = rodiAPI.getUIHandler();
        this.uiInteraction = rodiAPI.getUserInteraction();
        this.components = this.uiHandler.getAllUIComponents();

        this.ROS2Port = "6669";
        this.ROS2IP = "192.168.1.240";

        this.uiHandler.on('inpROS2IP', this.oninpROS2IP.bind(this));
        this.uiHandler.on('inpROS2Port', this.oninpROS2Port.bind(this));

    }

    initializeNode(thisNode, callback) {
        callback(null, thisNode);
    }

    openView(){
        this.updatePage();
    }

    closeView(){

    }

    generateScript(enterWriter, exitWriter){
        // Information about socket server.
        enterWriter.appendLine("var SERVER_INFO = {");
        enterWriter.appendLine("    NAME: 'RODI_ROS2',");
        enterWriter.appendLine(`    IP: '${this.ROS2IP}',`);
        enterWriter.appendLine(`    PORT: ${this.ROS2Port}`);
        enterWriter.appendLine("};");

        enterWriter.appendLine("var connected = true;");

        enterWriter.appendLine("function Init() {");

            // // Gripper homing 
            // setGeneralDigitalOutput(0, 0);
            // setGeneralDigitalOutput(1, 0);
            // setGeneralDigitalOutput(2, 1);

        enterWriter.appendLine("    externalMoveBegin();");
        enterWriter.appendLine("    sleep(1000);");

            // // Gripper  
            // setGeneralDigitalOutput(2, 0);

        enterWriter.appendLine("    socketCreate(SERVER_INFO.NAME, SERVER_INFO.IP, SERVER_INFO.PORT);");

            // register connect callback
        enterWriter.appendLine("    socketAddListener(SERVER_INFO.NAME, 'connection', function () {");
        enterWriter.appendLine("        message('>> connected');");
        enterWriter.appendLine("    });");

            // register close callback
        enterWriter.appendLine("    socketAddListener(SERVER_INFO.NAME, 'close', function () {");
        enterWriter.appendLine("        message('>> disconnected');");
        enterWriter.appendLine("        connected = false;");
        enterWriter.appendLine("    });");

        enterWriter.appendLine("    socketOpen(SERVER_INFO.NAME);");
        enterWriter.appendLine("    socketWaitConnection(SERVER_INFO.NAME, 50000000);");
        enterWriter.appendLine("}");

        enterWriter.appendLine("        function StateSend()");
        enterWriter.appendLine("{");
        enterWriter.appendLine("	let J = getCurrentJoint();");
	
        enterWriter.appendLine("	var result = 'JNT ' + J[0].toPrecision(5) + ' ' + J[1].toPrecision(5) + ' ' + J[2].toPrecision(5) + ' ' + J[3].toPrecision(5) + ' ' + J[4].toPrecision(5) + ' ' + J[5].toPrecision(5) + getGeneralDigitalInput(0 ) + ' '+ getGeneralDigitalInput(1 ) + ' ' +getGeneralDigitalInput(2 ) + ' ' + getGeneralDigitalInput(3 ) + ' ' + getGeneralDigitalInput(4 ) + ' ' + getGeneralDigitalInput(5 ) + ' ' + getGeneralDigitalInput(6) + ' ' + getGeneralDigitalInput(7) + '/n';");
	
        enterWriter.appendLine("	socketSend(SERVER_INFO.NAME, result);");
        enterWriter.appendLine("}");

        enterWriter.appendLine("function ProgramStart() {");
	
        enterWriter.appendLine("	  var ROS_JNTS = getCurrentJoint();");
	 
        enterWriter.appendLine("    while (connected) {");
        enterWriter.appendLine("        var arr = socketReadLine(SERVER_INFO.NAME,1);");
				
        enterWriter.appendLine("        if (arr.length < 1) {");
        enterWriter.appendLine("            continue;");
        enterWriter.appendLine("        }");
			
        enterWriter.appendLine("				if (arr == 'JNT') {");
        enterWriter.appendLine("					StateSend();");
        enterWriter.appendLine("        }");
        enterWriter.appendLine("        else if (arr.slice(0,3) == 'MOV') {");
        enterWriter.appendLine("          ROS_JNTS[0] = parseFloat(arr.slice(4, 10));");
        enterWriter.appendLine("          ROS_JNTS[1] = parseFloat(arr.slice(12, 18));");
        enterWriter.appendLine("          ROS_JNTS[2] = parseFloat(arr.slice(20, 26));");
        enterWriter.appendLine("          ROS_JNTS[3] = parseFloat(arr.slice(28, 34));");
        enterWriter.appendLine("          ROS_JNTS[4] = parseFloat(arr.slice(36, 42));");
        enterWriter.appendLine("          ROS_JNTS[5] = parseFloat(arr.slice(44, 51));");

        enterWriter.appendLine("          externalMoveJoint(ROS_JNTS, 50);");
					
        enterWriter.appendLine("					StateSend();");
        enterWriter.appendLine("        }");			
        enterWriter.appendLine("				else if (arr.slice(0,3) == 'GPO')");
        enterWriter.appendLine("        {");
        enterWriter.appendLine("					setGeneralDigitalOutput(0, parseInt(arr.slice(4,5)));");
        enterWriter.appendLine("					setGeneralDigitalOutput(1, parseInt(arr.slice(6,7)));");
        enterWriter.appendLine("					setGeneralDigitalOutput(2, parseInt(arr.slice(8,9)));");
        enterWriter.appendLine("					setGeneralDigitalOutput(3, parseInt(arr.slice(10,11)));");
        enterWriter.appendLine("					setGeneralDigitalOutput(4, parseInt(arr.slice(12,13)));");
        enterWriter.appendLine("					setGeneralDigitalOutput(5, parseInt(arr.slice(14,15)));");
        enterWriter.appendLine("					setGeneralDigitalOutput(6, parseInt(arr.slice(16,17)));");
        enterWriter.appendLine("					setGeneralDigitalOutput(7, parseInt(arr.slice(18,19)));");
					
        enterWriter.appendLine("					StateSend();");
        enterWriter.appendLine("				}");
        enterWriter.appendLine("    }");
        enterWriter.appendLine("}");

        enterWriter.appendLine("function Finish() {");
        enterWriter.appendLine("    socketDisconnect(SERVER_INFO.NAME);");
        enterWriter.appendLine("    sleep(100);");
        enterWriter.appendLine("    externalMoveEnd();");
        enterWriter.appendLine("    sleep(100);");
        enterWriter.appendLine("}");

        enterWriter.appendLine("Init();");
        enterWriter.appendLine("ProgramStart();");
        enterWriter.appendLine("Finish();");
    }

    /*

Example script for testing

var SERVER_INFO = {
    NAME: 'RODI_ROS2',
    IP: '172.31.117.121',
    PORT: 26669
};

var connected = true;

function Init() {

    externalMoveBegin();
    sleep(1000);

    socketCreate(SERVER_INFO.NAME, SERVER_INFO.IP, SERVER_INFO.PORT);

    socketAddListener(SERVER_INFO.NAME, 'connection', function () {
        message('>> connected');
    });

    socketAddListener(SERVER_INFO.NAME, 'close', function () {
        message('>> disconnected');
			  connected = false;
    });

    socketOpen(SERVER_INFO.NAME);
    socketWaitConnection(SERVER_INFO.NAME, 50000000);
}

function StateSend()
{
	let J = getCurrentJoint();
	
	var result = 'JNT ' + J[0].toPrecision(5) + ' ' + J[1].toPrecision(5) + ' ' + J[2].toPrecision(5) + ' ' + J[3].toPrecision(5) + ' ' + J[4].toPrecision(5) + ' ' + J[5].toPrecision(5) + getGeneralDigitalInput(0 ) + ' '+ getGeneralDigitalInput(1 ) + ' ' +getGeneralDigitalInput(2 ) + ' ' + getGeneralDigitalInput(3 ) + ' ' + getGeneralDigitalInput(4 ) + ' ' + getGeneralDigitalInput(5 ) + ' ' + getGeneralDigitalInput(6) + ' ' + getGeneralDigitalInput(7) + '/n';
	
	socketSend(SERVER_INFO.NAME, result);
}

function ProgramStart() {
	
	var ROS_JNTS = getCurrentJoint();
	 
    while (connected) {
        var arr = socketReadLine(SERVER_INFO.NAME,1);
				
        if (arr.length < 1) {
            continue;
        }
			
				if (arr == 'JNT') {
					StateSend();	
        }
        else if (arr.slice(0,3) == 'MOV') {
          ROS_JNTS[0] = parseFloat(arr.slice(4, 10));
          ROS_JNTS[1] = parseFloat(arr.slice(12, 18));
          ROS_JNTS[2] = parseFloat(arr.slice(20, 26));
          ROS_JNTS[3] = parseFloat(arr.slice(28, 34));
          ROS_JNTS[4] = parseFloat(arr.slice(36, 42));
          ROS_JNTS[5] = parseFloat(arr.slice(44, 51));

          externalMoveJoint(ROS_JNTS, 50);
					
					StateSend();
        }			
				else if (arr.slice(0,3) == 'GPO')
        {
					setGeneralDigitalOutput(0, parseInt(arr.slice(4,5)));
					setGeneralDigitalOutput(1, parseInt(arr.slice(6,7)));
					setGeneralDigitalOutput(2, parseInt(arr.slice(8,9)));
					setGeneralDigitalOutput(3, parseInt(arr.slice(10,11)));
					setGeneralDigitalOutput(4, parseInt(arr.slice(12,13)));
					setGeneralDigitalOutput(5, parseInt(arr.slice(14,15)));
					setGeneralDigitalOutput(6, parseInt(arr.slice(16,17)));
					setGeneralDigitalOutput(7, parseInt(arr.slice(18,19)));
					
					StateSend();
				}
    } 
}

function Finish() {
    socketDisconnect(SERVER_INFO.NAME);
    sleep(100);
    externalMoveEnd();
    sleep(100);
}

Init();
ProgramStart();
Finish();

    */

    isDefined(){
        return true;
    }

    updatePage() {
        // var DisplayMessage = this.dataModel.get('DisplayMessage', "Waiting for your confirmation.");
        // var WaitSeconds = this.dataModel.get('WaitSeconds', 15);

        this.components.inpROS2IP.setText(this.ROS2IP);
        this.components.inpROS2Port.setText (this.ROS2Port);

        this.uiHandler.render();
    }

    oninpROS2IP(type, data){
        if(type === 'change'){
            this.ROS2IP = data.value;
        }
    }

    oninpROS2Port(type, data){
        if(type === 'change'){
            this.ROS2Port = data.value;
        }
    }
}

module.exports = ROS2ProgramNodeContribution;
