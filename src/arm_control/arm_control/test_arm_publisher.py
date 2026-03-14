#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class TrajectoryPublisher(Node):

    def __init__(self):
        super().__init__('joint_trajectory_publisher')

        # 创建publisher，向arm_controller发送轨迹
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )

        # 机械臂关节名称
        self.joint_names = [
            "joint1",
            "joint2",
            "joint3",
            "joint4",
            "joint5",
            "joint6"
        ]

        # 定时发布轨迹
        timer_period = 6.0   # 发布周期（秒）
        self.timer = self.create_timer(timer_period, self.publish_trajectory)


    def publish_trajectory(self):

        msg = JointTrajectory()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.joint_names = self.joint_names

        # 生成轨迹点
        points = []

        # 轨迹点1
        point1 = JointTrajectoryPoint()
        point1.positions = [0.0, 0.0, 1.0, 0.0, 1.0, 0.0]
        # point1.velocities = [0.5, 0.5, 0.5]   # 可选速度指令
        point1.time_from_start = Duration(sec=3, nanosec=0)
        points.append(point1)

        # 轨迹点2
        point2 = JointTrajectoryPoint()
        point2.positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        point2.time_from_start = Duration(sec=6, nanosec=0)
        points.append(point2)

        msg.points = points

        # 发布轨迹
        self.publisher.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = TrajectoryPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()