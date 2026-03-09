from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import OpaqueFunction
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
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

    # Planning context
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare(support_package), "urdf", robot_xacro_file]
            ),
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    robot_description_semantic_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare(moveit_config_package), "config", moveit_config_file]
            ),
        ]
    )
    robot_description_semantic = {
        "robot_description_semantic": robot_description_semantic_content.perform(
            context
        )
    }

    kinematics_yaml = load_yaml(
        moveit_config_package.perform(context), "config/kinematics.yaml"
    )

    joint_limits_yaml = {
        "robot_description_planning": load_yaml(
            moveit_config_package.perform(context), "config/joint_limits.yaml"
        )
    }

    pentagram_node = Node(
        package="pentagram",
        executable="pentagram",
        output="screen",
        parameters=[
            robot_description,
            robot_description_semantic,
            kinematics_yaml,
            joint_limits_yaml,
        ],
    )

    nodes_to_start = [pentagram_node]
    return nodes_to_start


def generate_launch_description():

    declared_arguments = []

    # TODO(andyz): add other options
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_xacro_file",
            description="Xacro describing the robot.",
            default_value="hcr3a.xacro",
            choices=["irb360.xacro", "hcr3a.xacro"],
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "support_package",
            description="Name of the support package",
            default_value="hcr3a",
            choices=["irb360", "hcr3a"],
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "moveit_config_package",
            description="Name of the support package",
            default_value="hcr3a",
            choices=["irb360", "hcr3a"],
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "moveit_config_file",
            description="Name of the SRDF file",
            default_value="hcr3a.srdf.xacro",
            choices=["abb_irb360.srdf.xacro","hcr3a.srdf.xacro"],
        )
    )

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )

