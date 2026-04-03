import time

import rclpy
from rclpy.logging import get_logger
from moveit.planning import (
    MoveItPy,
)
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive

def plan_and_execute(
    robot,
    planning_component,
    logger,
    single_plan_parameters=None,
    multi_plan_parameters=None,
    sleep_time=0.0,
):
    logger.info("Planning trajectory")
    if multi_plan_parameters is not None:
        plan_result = planning_component.plan(
            multi_plan_parameters=multi_plan_parameters
        )
    elif single_plan_parameters is not None:
        plan_result = planning_component.plan(
            single_plan_parameters=single_plan_parameters
        )
    else:
        plan_result = planning_component.plan()

    # execute the plan
    if plan_result:
        logger.info("Executing plan")
        robot_trajectory = plan_result.trajectory
        robot.execute(robot_trajectory, controllers=[])
    else:
        logger.error("Planning failed")

    time.sleep(sleep_time)

def add_collision_objects(planning_scene_monitor):
    """Helper function that adds collision objects to the planning scene."""
    object_positions = [
        (0.15, 0.1, 0.5),
        (0.25, 0.0, 1.0),
        (-0.25, -0.3, 0.8),
        (0.25, 0.3, 0.75),
    ]
    object_dimensions = [
        (0.1, 0.4, 0.1),
        (0.1, 0.4, 0.1),
        (0.2, 0.2, 0.2),
        (0.15, 0.15, 0.15),
    ]

    with planning_scene_monitor.read_write() as scene:
        collision_object = CollisionObject()
        collision_object.header.frame_id = "base_link"
        collision_object.id = "boxes"

        for position, dimensions in zip(object_positions, object_dimensions):
            box_pose = Pose()
            box_pose.position.x = position[0]
            box_pose.position.y = position[1]
            box_pose.position.z = position[2]

            box = SolidPrimitive()
            box.type = SolidPrimitive.BOX
            box.dimensions = dimensions

            collision_object.primitives.append(box)
            collision_object.primitive_poses.append(box_pose)
            collision_object.operation = CollisionObject.ADD

        scene.apply_collision_object(collision_object)
        scene.current_state.update()  # Important to ensure the scene is updated

def main():
    rclpy.init()
    logger = get_logger("hello_moveit_py.pose_goal")

    robot = MoveItPy(node_name="hello_moveit_py")
    robot_arm = robot.get_planning_component("manipulator")
    logger.info("MoveItPy instance created")

    planning_scene_monitor = robot.get_planning_scene_monitor()
    add_collision_objects(planning_scene_monitor)

    # set plan start state to current state
    robot_arm.set_start_state_to_current_state()

    # set pose goal with PoseStamped message
    from geometry_msgs.msg import PoseStamped

    pose_goal = PoseStamped()
    pose_goal.header.frame_id = "base_link"

    pose_goal.pose.orientation.x = 0.26787
    pose_goal.pose.orientation.y = -0.654076
    pose_goal.pose.orientation.z = 0.65484
    pose_goal.pose.orientation.w = -0.267606
    pose_goal.pose.position.x = 0.430377
    pose_goal.pose.position.y = -0.150136
    pose_goal.pose.position.z = 0.0177264
#    pose_goal.pose.orientation.x = 0.799098
#    pose_goal.pose.orientation.y = 0.112868 
#    pose_goal.pose.orientation.z = -0.576817
#    pose_goal.pose.orientation.w = -0.126436
#    pose_goal.pose.position.x = -0.278177
#    pose_goal.pose.position.y = -0.262118
#    pose_goal.pose.position.z = 0.499117 
    robot_arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link="tool0")

    # plan to goal
    plan_and_execute(robot, robot_arm, logger, sleep_time=3.0)

if __name__ == '__main__':
    main()
