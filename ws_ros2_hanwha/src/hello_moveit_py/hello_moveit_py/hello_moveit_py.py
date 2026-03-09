import time

import rclpy
from rclpy.logging import get_logger
from moveit.planning import (
    MoveItPy,
)

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

def main():
    rclpy.init()
    logger = get_logger("hello_moveit_py.pose_goal")

    robot = MoveItPy(node_name="hello_moveit_py")
    robot_arm = robot.get_planning_component("manipulator")
    logger.info("MoveItPy instance created")

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
    robot_arm.set_goal_state(pose_stamped_msg=pose_goal, pose_link="tool0")

    # plan to goal
    plan_and_execute(robot, robot_arm, logger, sleep_time=3.0)

if __name__ == '__main__':
    main()
