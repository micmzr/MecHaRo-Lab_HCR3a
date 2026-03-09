Very basic and unofficial Hanwha HCR3a ROS2/MoveIt driver. 
For limited use only with system installed in MecHaRo-Lab at Technical University of Gdańsk.  

**PC**

Everything presented here is mean to be run on the PC.
 
_Install_

``` bash
sudo apt install -y libasio-dev libcurlpp-dev
git clone --recursive -b jazzy https://github.com/micmzr/MecHaRo-Lab_HCR3a.git
cd MecHaRo-Lab_ROSBot2Pro/ws_ros2_hanwha
rosdep install --ignore-src --from-path src/ -y --rosdistro $ROS_DISTRO
colcon build
source install/setup.bash
```

**_Simulation_**

Generally each command should be run in separate terminal tab. Please remember to run source command. 

_Control_
``` bash
ros2 launch hcr3a hcr_control.launch.py use_fake_hardware:=true
```
_MoveIT_
``` bash
ros2 launch hcr3a hcr_moveit.launch.py 
```

**_Real Robot_ - required plugin and running deamon on HCR Control System.**

_Control_
``` bash
ros2 launch hcr3a hcr_control.launch.py use_fake_hardware:=false hcr_ip:=192.168.1.5 hcr_port:=6667 use_ft:=false
```
_MoveIT_
``` bash
ros2 launch hcr3a hcr_moveit.launch.py 
```

**_Gazebo_**

_Control_
``` bash
ros2 launch hcr3a hcr_gz_control.launch.py
```
_MoveIT_
``` bash
ros2 launch hcr3a hcr_moveit.launch.py use_sim_time:=true 
```

**_Python MoveIT example_**

``` bash
ros2 launch hcr3a hcr_moveit.launch.py use_sim_time:=true 
```
