search_mode=OPTIMIZE_MAX_JOINT
srdf_filename=hcr3a.srdf
robot_name_in_srdf=hcr3a
moveit_config_pkg=hcr3a_moveit_config
robot_name=hcr3a
planning_group_name=manipulator
ikfast_plugin_pkg=hcr3a_manipulator_ikfast_plugin
base_link_name=base_link
eef_link_name=tool0
ikfast_output_path=/home/mmazur/Prace/Imie_N/MecHaRo-Lab_HCR3a/ws_ros2_hanwha/src/hcr3a/urdf/hcr3a_manipulator_ikfast_plugin/src/hcr3a_manipulator_ikfast_solver.cpp

rosrun moveit_kinematics create_ikfast_moveit_plugin.py\
  --search_mode=$search_mode\
  --srdf_filename=$srdf_filename\
  --robot_name_in_srdf=$robot_name_in_srdf\
  --moveit_config_pkg=$moveit_config_pkg\
  $robot_name\
  $planning_group_name\
  $ikfast_plugin_pkg\
  $base_link_name\
  $eef_link_name\
  $ikfast_output_path
