const path = require('path');
const PluginActivator = require('rodix_api').PluginActivator;
const ROS2ProgramNodeService = require(path.join(__dirname, 'ROS2ProgramNodeService'));
const ROS2DaemonSvc = require(path.join(__dirname, 'ROS2DaemonService'));

class Activator extends PluginActivator {
    constructor() {
        super();
    }

    start(context) {
        let ROS2DaemonService = new ROS2DaemonSvc();

        context.registerService('ROS2DaemonService', ROS2DaemonService);
        
        context.registerService('ROS2ProgramNodeService', new ROS2ProgramNodeService(ROS2DaemonService));
        // context.registerService('ROS2ProgramNodeService', new ROS2ProgramNodeService());
    }

    stop() {
    }
}

module.exports = Activator;
