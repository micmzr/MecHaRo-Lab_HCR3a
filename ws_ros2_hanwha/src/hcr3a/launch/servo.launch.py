from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.actions import OpaqueFunction
from launch_param_builder import ParameterBuilder
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
        .to_moveit_configs()
    )

    servo_params = {
        "moveit_servo": ParameterBuilder("hcr3a")
        .yaml("config/servo_config.yaml")
        .to_dict()
    }

    print(servo_params)

    acceleration_filter_update_period = {"update_period": 0.01}
    planning_group_name = {"planning_group_name": "manipulator"}

    servo = Node(
        package="moveit_servo",
        executable="servo_node",
        name="servo_node",
        parameters=[
            servo_params,
            acceleration_filter_update_period,
            planning_group_name,
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            {'use_sim_time': use_sim_time},
        ],
        output="screen",
    )

    nodes_to_start = [servo]
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

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
