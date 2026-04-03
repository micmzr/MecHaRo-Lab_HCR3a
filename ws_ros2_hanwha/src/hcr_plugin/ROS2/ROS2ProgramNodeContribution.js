const ProgramNodeContribution = require('rodix_api').ProgramNodeContribution;

class ROS2ProgramNodeContribution extends ProgramNodeContribution {
    constructor(rodiAPI, dataModel, daemonService){
        super();
        this.rodiAPI = rodiAPI;
        this.daemonSvc = daemonService;
        this.dataModel = dataModel;
        this.uiHandler = rodiAPI.getUIHandler();
        this.uiInteraction = rodiAPI.getUserInteraction();
        this.components = this.uiHandler.getAllUIComponents();

        this.HCRPort = "6668";
        this.HCRIP = "192.168.100.241";
        this.ROS2Port = "6669";
        this.ROS2IP = "192.168.1.5";

        this.uiHandler.on('btnSTART', this.onbtnSTART.bind(this));
        this.uiHandler.on('btnSTOP', this.onbtnSTOP.bind(this));
        this.uiHandler.on('inpHCRIP', this.oninpHCRIP.bind(this));
        this.uiHandler.on('inpHCRPort', this.oninpHCRPort.bind(this));
        this.uiHandler.on('inpROS2IP', this.oninpROS2IP.bind(this));
        this.uiHandler.on('inpROS2Port', this.oninpROS2Port.bind(this));

        /* Update daemon status to UI */
        this.timer = setInterval(function() {
            // this.components['labelDaemon'].setText('Daemon status : '+this.daemonSvc.getDaemon().getState());
            this.components['labelDaemon'].setText('Daemon status : '+this.daemonSvc.daemonContribution.getState());
            this.uiHandler.render();
        }.bind(this), 500);
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
        enterWriter.appendLine(`    IP: '${this.HCRIP}',`);
        enterWriter.appendLine(`    PORT: ${this.HCRPort}`);
        enterWriter.appendLine("};");

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
        enterWriter.appendLine("    });");

        enterWriter.appendLine("    socketOpen(SERVER_INFO.NAME);");
        enterWriter.appendLine("    socketWaitConnection(SERVER_INFO.NAME, 5000);");
        enterWriter.appendLine("}");

        enterWriter.appendLine("function ProgramStart() {");
        enterWriter.appendLine("    while (true) {");
        enterWriter.appendLine("        var arr = socketReadLine(SERVER_INFO.NAME);");

        enterWriter.appendLine("        if (arr.length < 1) {");
        enterWriter.appendLine("            continue;");
        enterWriter.appendLine("        }");
        enterWriter.appendLine("        var JNT_command = arr.search('JNT') * 1;");
        enterWriter.appendLine("        var MOV_command = arr.search('MOV') * 1;");
        enterWriter.appendLine("        var GPI_command = arr.search('GPI')*1;");
		enterWriter.appendLine("        var GPO_command = arr.search('GPO')*1;");
        enterWriter.appendLine("        var ROS_JNTS = getCurrentJoint();");

        enterWriter.appendLine("        if (JNT_command == 0) {");
        enterWriter.appendLine("            let J = getCurrentJoint();");

        enterWriter.appendLine("            var result = 'JNT ' + J[0].toPrecision(5) + ' ' + J[1].toPrecision(5) + ' ' + J[2].toPrecision(5) + ' ' + J[3].toPrecision(5) + ' ' + J[4].toPrecision(5) + ' ' + J[5].toPrecision(5);");

        enterWriter.appendLine("            socketSendLine(SERVER_INFO.NAME, result);");
        enterWriter.appendLine("        }");

        enterWriter.appendLine("        if (MOV_command == 0) {");
        enterWriter.appendLine("            ROS_JNTS[0] = parseFloat(arr.slice(4, 10));");
        enterWriter.appendLine("            ROS_JNTS[1] = parseFloat(arr.slice(12, 18));");
        enterWriter.appendLine("            ROS_JNTS[2] = parseFloat(arr.slice(20, 26));");
        enterWriter.appendLine("            ROS_JNTS[3] = parseFloat(arr.slice(28, 34));");
        enterWriter.appendLine("            ROS_JNTS[4] = parseFloat(arr.slice(36, 42));");
        enterWriter.appendLine("            ROS_JNTS[5] = parseFloat(arr.slice(44, 51));");

        enterWriter.appendLine("            externalMoveJoint(ROS_JNTS, 50);");
        enterWriter.appendLine("        }");

		enterWriter.appendLine("        if (GPI_command == 0)");
        enterWriter.appendLine("        {");
				
		enterWriter.appendLine("        	var result  = 'GPI ' + 		getGeneralDigitalInput(0 ) + ' '+ getGeneralDigitalInput(1 ) + ' ' +getGeneralDigitalInput(2 ) + ' ' + getGeneralDigitalInput(3 ) + ' ' + getGeneralDigitalInput(4 ) + ' ' + getGeneralDigitalInput(5 ) + ' ' + getGeneralDigitalInput(6) + ' ' + getGeneralDigitalInput(7);");
				
		enterWriter.appendLine("        	socketSendLine(SERVER_INFO.NAME, result);");
			
  	    enterWriter.appendLine("        }");
			
		enterWriter.appendLine("        if (GPO_command == 0)");
        enterWriter.appendLine("        {");
		enterWriter.appendLine("        	setGeneralDigitalOutput(0, parseInt(arr.slice(4,5)));");
		enterWriter.appendLine("        	setGeneralDigitalOutput(1, parseInt(arr.slice(6,7)));");												
		enterWriter.appendLine("        	setGeneralDigitalOutput(2, parseInt(arr.slice(8,9)));");												
		enterWriter.appendLine("        	setGeneralDigitalOutput(3, parseInt(arr.slice(10,11)));");
		enterWriter.appendLine("        	setGeneralDigitalOutput(4, parseInt(arr.slice(12,13)));");
		enterWriter.appendLine("        	setGeneralDigitalOutput(5, parseInt(arr.slice(14,15)));");												
		enterWriter.appendLine("        	setGeneralDigitalOutput(6, parseInt(arr.slice(16,17)));");												
		enterWriter.appendLine("        	setGeneralDigitalOutput(7, parseInt(arr.slice(18,19)));");
    	enterWriter.appendLine("        }");


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

    isDefined(){
        return true;
    }

    updatePage() {
        // var DisplayMessage = this.dataModel.get('DisplayMessage', "Waiting for your confirmation.");
        // var WaitSeconds = this.dataModel.get('WaitSeconds', 15);

        this.components.inpHCRIP.setText(this.HCRIP);
        this.components.inpHCRPort.setText (this.HCRPort);

        this.components.inpROS2IP.setText(this.ROS2IP);
        this.components.inpROS2Port.setText (this.ROS2Port);

        this.uiHandler.render();
    }

    onbtnSTART(type) {
        if (type !== 'click') {
            return;
        }

        if (type === 'click') {
            var args = [`-hcr_ip`,`${this.HCRIP}`,`-hcr_port`,`${this.HCRPort}`,`-ros2_ip`,`${this.ROS2IP}`,`-ros2_port`,`${this.ROS2Port}`];
            // this.daemonSvc.getDaemon().start(args);
            this.daemonSvc.daemonContribution.start(args);
        }

        this.updatePage();
    }

    onbtnSTOP(type) {
        if (type !== 'click') {
            return;
        }

        if (type === 'click') {
            // this.daemonSvc.getDaemon().stop();
            this.daemonSvc.daemonContribution.stop();
        }

        this.updatePage();
    }

    oninpHCRIP(type, data){
        if(type === 'change'){
            // this.dataModel.set('HCRIP', data.value);
            this.HCRIP = data.value;
        }
    }

    oninpHCRPort(type, data){
        if(type === 'change'){
            this.HCRPort = data.value;
        }
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
