const path = require('path');
const PluginActivator = require('rodix_api').PluginActivator;
const ROS2ProgramNodeService = require(path.join(__dirname, 'ROS2ProgramNodeService'));

class Activator extends PluginActivator {
    constructor() {
        super();
    }

    start(context) {
        context.registerService('ROS2ProgramNodeService', new ROS2ProgramNodeService());
    }

    stop() {
    }
}

module.exports = Activator;
