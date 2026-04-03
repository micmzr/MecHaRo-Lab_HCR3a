const path = require('path');
const DaemonService = require('rodix_api').DaemonService;

class ROS2DaemonService extends DaemonService{
    constructor() {
      super();

      this.executablePath = path.join(__dirname, 'exec', 'hcr_controller_sfs.exe');
      this.daemonContribution = null;
    }

    init(daemonContribution) {
        this.daemonContribution = daemonContribution;
        // this.daemonContribution.start();
        // this.daemonContribution.showWindow();
    }
    getTitle(){
        return 'ROS2';
    }
    eventOnWidget(){

    }
    getExecutable() {
      return this.executablePath;
    }
}

module.exports = ROS2DaemonService;
