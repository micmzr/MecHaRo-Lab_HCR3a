from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.actions import OpaqueFunction
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder

import os
import yaml


def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)

    try:
        with open(absolute_file_path, "r") as file:
            return yaml.safe_load(file)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        return None


def launch_setup(context, *args, **kwargs):
    # Command-line arguments
    robot_xacro_file = LaunchConfiguration("robot_xacro_file")
    support_package = LaunchConfiguration("support_package")
    moveit_config_package = LaunchConfiguration("moveit_config_package")
    moveit_config_file = LaunchConfiguration("moveit_config_file")
    launch_rviz = LaunchConfiguration("launch_rviz")
    not_only_rviz = LaunchConfiguration("not_only_rviz")
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    # MoveIt configuration
    moveit_config = (
        MoveItConfigsBuilder(
            "hcr3a", package_name=f"{moveit_config_package.perform(context)}"
        )
        .robot_description(
            file_path=os.path.join(
                get_package_share_directory(f"{support_package.perform(context)}"),
                "urdf",
                f"{robot_xacro_file.perform(context)}",
            )
        )
        .robot_description_semantic(
            file_path=os.path.join(
                get_package_share_directory(
                    f"{moveit_config_package.perform(context)}"
                ),
                "config",
                f"{moveit_config_file.perform(context)}",
            )
        )
        .planning_pipelines()
        .robot_description_kinematics(
            file_path=os.path.join(
                get_package_share_directory(
                    f"{moveit_config_package.perform(context)}"
                ),
                "config",
                "kinematics.yaml",
            )
        )
        .trajectory_execution(
            file_path=os.path.join(
                get_package_share_directory(
                    f"{moveit_config_package.perform(context)}"
                ),
                "config",
                "moveit_controllers.yaml",
            ),
            # moveit_manage_controllers=False,
        )
        .planning_scene_monitor(
            publish_planning_scene=True,
            publish_geometry_updates=True,
            publish_state_updates=True,
            publish_transforms_updates=True,
            publish_robot_description=True,
            publish_robot_description_semantic=True,
        )
        .joint_limits(
            file_path=os.path.join(
                get_package_share_directory(
                    f"{moveit_config_package.perform(context)}"
                ),
                "config",
                "joint_limits.yaml",
            )
        )
        .sensors_3d(
            file_path=os.path.join(
                get_package_share_directory(f"{moveit_config_package.perform(context)}"),
                "config",
                "sensors_3d.yaml", # Ensure this file exists, even if empty or configured to 'none'
            )
        )
        .planning_pipelines(
            default_planning_pipeline="ompl",
            pipelines=["ompl", "pilz_industrial_motion_planner"]
        )
        .to_moveit_configs()
    )

    # Trajectory Execution Functionality
    moveit_simple_controllers_yaml = load_yaml(
        "hcr3a", "config/moveit_controllers.yaml"
    )
    moveit_controllers = {
        "moveit_simple_controller_manager": moveit_simple_controllers_yaml,
        "moveit_controller_manager": "moveit_simple_controller_manager/MoveItSimpleControllerManager",
    }

    # Start the actual move_group node/action server
    move_group_node = Node(
        package="moveit_ros_move_group",
        condition=IfCondition(not_only_rviz),
        executable="move_group",
        output="screen",     
        parameters=[
            {'use_sim_time': use_sim_time},
            moveit_config.trajectory_execution,
            moveit_controllers,
            moveit_config.to_dict(),
        ],
    )

    # RViz
    rviz_base = os.path.join(
        get_package_share_directory("hcr3a"), "rviz"
    )
    rviz_config = os.path.join(rviz_base, "moveit.rviz")
    rviz_node = Node(
        package="rviz2",
        condition=IfCondition(launch_rviz),
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[
            {'use_sim_time': use_sim_time},
            moveit_config.to_dict(),
        ],
    )

    # Publish TF
    robot_state_pub_node = Node(
        package="robot_state_publisher",
        condition=IfCondition(not_only_rviz),
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[
            {'use_sim_time': use_sim_time},
            moveit_config.robot_description,
            ],
    )

    nodes_to_start = [move_group_node, rviz_node, robot_state_pub_node]
    return nodes_to_start


def generate_launch_description():

    declared_arguments = []

    # TODO(andyz): add other options
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_xacro_file",
            default_value="hcr3a.xacro",
            description="Xacro describing the robot.",
            choices=["hcr3a.xacro"],
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "support_package",
            default_value="hcr3a",
            description="Name of the support package",
            choices=["hcr3a"],
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "moveit_config_package",
            default_value="hcr3a",
            description="Name of the support package",
            choices=["hcr3a"],
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "moveit_config_file",
            default_value="hcr3a.srdf.xacro",
            description="Name of the SRDF file",
            choices=["hcr3a.srdf.xacro"],
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "launch_rviz", default_value="true", description="Launch RViz?"
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "not_only_rviz", default_value="true", description="Launch not only RViz?"
        )
    )

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
