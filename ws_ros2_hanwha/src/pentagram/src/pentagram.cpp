#include <chrono>
#include <thread>
#include <memory>

#include <rclcpp/rclcpp.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <moveit_visual_tools/moveit_visual_tools.h>
#include <moveit/planning_scene_interface/planning_scene_interface.hpp>

#define _USE_MATH_DEFINES
#include <cmath>

int main(int argc, char *argv[])
{
  // Initialize ROS and create the Node
  rclcpp::init(argc, argv);
  auto const node = std::make_shared<rclcpp::Node>(
      "pentagram",
      rclcpp::NodeOptions().automatically_declare_parameters_from_overrides(true));

  // Create a ROS logger
  auto const logger = rclcpp::get_logger("Pentagram burns");

  rclcpp::executors::SingleThreadedExecutor executor;
  executor.add_node(node);
  auto spinner = std::thread([&executor]()
                             { executor.spin(); });

  // Next step goes here
  // Create the MoveIt MoveGroup Interface
  using moveit::planning_interface::MoveGroupInterface;
  auto move_group_interface = MoveGroupInterface(node, "manipulator");
  move_group_interface.setGoalPositionTolerance(1e-3);
  move_group_interface.setGoalOrientationTolerance(0.01);

  // Construct and initialize MoveItVisualTools
  auto moveit_visual_tools = moveit_visual_tools::MoveItVisualTools{
      node, "base_link", rviz_visual_tools::RVIZ_MARKER_TOPIC,
      move_group_interface.getRobotModel()};
  moveit_visual_tools.deleteAllMarkers();
  moveit_visual_tools.loadRemoteControl();

  // Create closures for visualization
  auto const draw_title = [&moveit_visual_tools](auto text)
  {
    auto const text_pose = []
    {
      auto msg = Eigen::Isometry3d::Identity();
      msg.translation().z() = 1.0; // Place text 1m above the base link
      return msg;
    }();
    moveit_visual_tools.publishText(text_pose, text, rviz_visual_tools::WHITE,
                                    rviz_visual_tools::XLARGE);
  };
  
  auto const prompt = [&moveit_visual_tools](auto text)
  {
   moveit_visual_tools.prompt(text);
  };

  auto const draw_trajectory_tool_path =
      [&moveit_visual_tools,
       jmg = move_group_interface.getRobotModel()->getJointModelGroup(
//           "irb360")](auto const trajectory) // delta
           "manipulator")](auto const trajectory)
  {
    moveit_visual_tools.publishTrajectoryLine(trajectory, jmg);
  };

  const double pi = M_PI;
  const double r_p = 0.2l;

  geometry_msgs::msg::Pose target_pose;
  int ipp[] = {0, 3, 1, 4, 2};
    
  std::string end_effector_link = "tool0";

  auto start_pose = move_group_interface.getCurrentPose(end_effector_link);

  RCLCPP_INFO(logger, "Starting pose orientation qx %g qy %g qz %g qw %g", start_pose.pose.orientation.x, start_pose.pose.orientation.y, start_pose.pose.orientation.z, start_pose.pose.orientation.w);
  RCLCPP_INFO(logger, "Starting pose orientation x %g y %g z %g", start_pose.pose.position.x, start_pose.pose.position.y, start_pose.pose.position.z);

  move_group_interface.setMaxVelocityScalingFactor(1.l);
  move_group_interface.setMaxAccelerationScalingFactor(1.l);

  auto const collision_object = [frame_id =
                                     move_group_interface.getPlanningFrame()]
  {
    moveit_msgs::msg::CollisionObject collision_object;
    collision_object.header.frame_id = frame_id;
    collision_object.id = "box1";
    shape_msgs::msg::SolidPrimitive primitive;

    // Define the size of the box in meters
    primitive.type = primitive.BOX;
    primitive.dimensions.resize(3);
    primitive.dimensions[primitive.BOX_X] = 2.0;
    primitive.dimensions[primitive.BOX_Y] = 2.0;
    primitive.dimensions[primitive.BOX_Z] = 0.1;

    // Define the pose of the box (relative to the frame_id)
    geometry_msgs::msg::Pose box_pose;
    box_pose.orientation.w = 1.0; // We can leave out the x, y, and z components of the quaternion since they are initialized to 0
    box_pose.position.x = 0.0;
    box_pose.position.y = 0.0;
    box_pose.position.z = -0.05;

    collision_object.primitives.push_back(primitive);
    collision_object.primitive_poses.push_back(box_pose);
    collision_object.operation = collision_object.ADD;

    return collision_object;
  }();

  std::vector<double> joint_values;

  // HCR3a Home position 
  joint_values.push_back(0);
  joint_values.push_back(-90*pi/180.);
  joint_values.push_back(-90*pi/180.);
  joint_values.push_back(-90*pi/180.);
  joint_values.push_back(90*pi/180.);
  joint_values.push_back(0);

  move_group_interface.setJointValueTarget(joint_values);

  std::vector<geometry_msgs::msg::Pose> waypoints;

  // HCR3a home pose 
  // qx 0.26787 qy -0.654076 qz 0.654841 qw -0.267606
  // x 0.430377 y -0.150136 z 0.0177264
  auto const home_pose = []
  {
    geometry_msgs::msg::Pose msg;
    msg.orientation.x = 0.26787;
    msg.orientation.y = -0.654076;
    msg.orientation.z = 0.65484;
    msg.orientation.w = -0.267606;
    msg.position.x = 0.430377;
    msg.position.y = -0.150136;
    msg.position.z = 0.0177264;
    return msg;
  }();
  
  draw_title("Planning");
  moveit_visual_tools.trigger();
  auto const [success_h, plan_h] = [&move_group_interface]
  {
    moveit::planning_interface::MoveGroupInterface::Plan msg;
    auto const ok = static_cast<bool>(move_group_interface.plan(msg));
    return std::make_pair(ok, msg);
  }();

  // Execute the plan
  if (success_h)
  {
    draw_trajectory_tool_path(plan_h.trajectory);
    moveit_visual_tools.trigger();
    prompt("Press 'Next' in the RvizVisualToolsGui window to go home postion");
    draw_title("Executing");
    moveit_visual_tools.trigger();
    move_group_interface.execute(plan_h);
  }
  else
  {
    draw_title("Planning Failed!");
    moveit_visual_tools.trigger();
    RCLCPP_ERROR(logger, "Planning failed!");
  }

  moveit::planning_interface::PlanningSceneInterface planning_scene_interface;
  planning_scene_interface.applyCollisionObject(collision_object);

  for (int ip = 0; ip < 10; ip++)
  {
    // HCR3a 

    // HOME POSE -> x 0.430377 y -0.150136 z 0.0177264   

    target_pose.orientation.x = home_pose.orientation.x;
    target_pose.orientation.y = home_pose.orientation.y;
    target_pose.orientation.z = home_pose.orientation.z; 
    target_pose.orientation.w = home_pose.orientation.w;	  
    target_pose.position.x = 0.330 + r_p * cos(2.l * pi * ipp[ip % 5] / 5 + pi / 2.l);
    target_pose.position.y = 0.150 + r_p * sin(2.l * pi * ipp[ip % 5] / 5 + pi / 2.l);
    target_pose.position.z = 0.050;

    waypoints.push_back(target_pose);
  }

  draw_title("Planning");
  moveit_visual_tools.trigger();
  auto const [success, plan] = [&move_group_interface]
  {
    moveit::planning_interface::MoveGroupInterface::Plan msg;
    auto const ok = static_cast<bool>(move_group_interface.plan(msg));
    return std::make_pair(ok, msg);
  }();

  // Execute the plan
  if (success)
  {
    const double jump_threshold = 0.0;
    const double eef_step = 0.1;
    moveit_msgs::msg::RobotTrajectory cart_trajectory;
    double fraction = move_group_interface.computeCartesianPath(waypoints, eef_step, jump_threshold, cart_trajectory);
    RCLCPP_INFO(logger, "Visualizing plan 4 (Cartesian path) (%.2f%% achieved)", fraction * 100.0);

    moveit::planning_interface::MoveGroupInterface::Plan cart_plan;
    cart_plan.planning_time = plan.planning_time;
    cart_plan.start_state = plan.start_state;
    cart_plan.trajectory = cart_trajectory;


    draw_trajectory_tool_path(cart_plan.trajectory);
    moveit_visual_tools.trigger();
    prompt("Press 'Next' in the RvizVisualToolsGui window to execute");
    draw_title("Executing");
    moveit_visual_tools.trigger();
    move_group_interface.execute(cart_plan);
  }
  else
  {
    draw_title("Planning Failed!");
    moveit_visual_tools.trigger();
    RCLCPP_ERROR(logger, "Planning failed!");
  }

  std::this_thread::sleep_for(std::chrono::seconds(10));

  // Shutdown ROS
  rclcpp::shutdown();
  spinner.join();
  return 0;
}
