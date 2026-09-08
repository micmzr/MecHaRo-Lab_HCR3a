from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    declared_arguments = []

    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    declared_arguments.append(
        DeclareLaunchArgument(
            "runtime_config_package",
            default_value="hcr3a",
            description='Package with the controller\'s configuration in "config" folder. \
        Usually the argument is not set, it enables use of a custom setup.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "controllers_file",
            default_value="hcr_controllers.yaml",
            description="YAML file with the controllers configuration.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "description_package",
            default_value="hcr3a",
            description="Description package with robot URDF/XACRO files. Usually the argument \
        is not set, it enables use of a custom description.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "moveit_config_package",
            default_value="hcr3a",
            description="MoveIt configuration package for the robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "description_file",
            default_value="hcr3a.xacro",
            description="URDF/XACRO description file with the robot",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "prefix",
            default_value='""',
            description="Prefix of the joint names, useful for \
        multi-robot setup. If changed then also joint names in the controllers' configuration \
        have to be updated.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="false",
            description="Start robot with fake hardware mirroring command to its states.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "hcr_ip",
            default_value="None",
            description="IP of RODI computer/HCR controller. \
            Used only if 'use_fake_hardware' parameter is false.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "hcr_port",
            default_value="6667",
            description="Port at which HCR can be found. \
            Used only if 'use_fake_hardware' parameter is false.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "fake_sensor_commands",
            default_value="false",
            description="Enable fake command interfaces for sensors used for simple simulations. \
            Used only if 'use_fake_hardware' parameter is true.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "initial_joint_controller",
            default_value="joint_trajectory_controller",
            description="Robot controller to start.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "launch_rviz", default_value="false", description="Launch RViz?"
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_ft",
            default_value="false",
            description="Use force-torque sensor.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "ft_ip",
            default_value="192.168.1.1",
            description="FT sensor ip adress.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "rdt_sampling_rate",
            default_value="500",
            description="FT sampling rate.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "sensor_type",
            default_value="onrobot",
            description="FT sensor type.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "internal_filter_rate",
            default_value="0",
            description="FT internal filter rate.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_hardware_biasing",
            default_value="false",
            description="FT hardware bassing.",
        )
    )

    # Initialize Arguments
    runtime_config_package = LaunchConfiguration("runtime_config_package")
    controllers_file = LaunchConfiguration("controllers_file")
    description_package = LaunchConfiguration("description_package")
    moveit_config_package = LaunchConfiguration("moveit_config_package")
    description_file = LaunchConfiguration("description_file")
    prefix = LaunchConfiguration("prefix")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    fake_sensor_commands = LaunchConfiguration("fake_sensor_commands")
    hcr_ip = LaunchConfiguration("hcr_ip")
    hcr_port = LaunchConfiguration("hcr_port")
    initial_joint_controller = LaunchConfiguration("initial_joint_controller")
    use_ft = LaunchConfiguration("use_ft")
    ft_ip = LaunchConfiguration("ft_ip")
    rdt_sampling_rate = LaunchConfiguration("rdt_sampling_rate")
    sensor_type = LaunchConfiguration("sensor_type")
    internal_filter_rate = LaunchConfiguration("internal_filter_rate")
    use_hardware_biasing = LaunchConfiguration("use_hardware_biasing")
    launch_rviz = LaunchConfiguration("launch_rviz")

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare(description_package), "urdf", description_file]
            ),
            " ",
            "prefix:=",
            prefix,
            " ",
            "use_fake_hardware:=",
            use_fake_hardware,
            " ",
            "fake_sensor_commands:=",
            fake_sensor_commands,
            " ",
            "hcr_ip:=",
            hcr_ip,
            " ",
            "hcr_port:=",
            hcr_port,
            " ",
            "use_ft:=",
            use_ft,
            " ",
            "ft_ip:=",
            ft_ip,
            " ",
            "rdt_sampling_rate:=",
            rdt_sampling_rate,
            " ",
            "sensor_type:=",
            sensor_type,
            " ",
            "internal_filter_rate:=",
            internal_filter_rate,
            " ",
            "use_hardware_biasing:=",
            use_hardware_biasing,
            " ",                        
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    robot_controllers = PathJoinSubstitution(
        [FindPackageShare(runtime_config_package), "config", controllers_file]
    )

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare(moveit_config_package), "rviz", "moveit.rviz"]
    )

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[{'use_sim_time': use_sim_time}, robot_description, robot_controllers],
        output="both",
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[{'use_sim_time': use_sim_time}, robot_description],
    )

    rviz_node = Node(
        package="rviz2",
        condition=IfCondition(launch_rviz),
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
        parameters=[{'use_sim_time': use_sim_time}, robot_controllers],
    )

    initial_joint_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[initial_joint_controller, "-c", "/controller_manager"],
        parameters=[{'use_sim_time': use_sim_time}, robot_controllers],
    )

    gripper_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gripper_controller", "-c", "/controller_manager"],
        parameters=[{'use_sim_time': use_sim_time}, robot_controllers],
    )

    force_torque_sensor_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["force_torque_sensor_broadcaster","-c","/controller_manager"],
        parameters=[{'use_sim_time': use_sim_time}, robot_controllers],
    )

    gpio_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gpio_controller","-c","/controller_manager"],
        parameters=[{'use_sim_time': use_sim_time}, robot_controllers],
    )

    nodes_to_start = [
        control_node,
        robot_state_publisher_node,
        rviz_node,
        joint_state_broadcaster_spawner,
        initial_joint_controller_spawner,
        gripper_controller_spawner,
        force_torque_sensor_broadcaster_spawner,
        gpio_controller_spawner
    ]

    return LaunchDescription(declared_arguments + nodes_to_start)
