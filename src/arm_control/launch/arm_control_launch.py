from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node
from launch.actions import TimerAction
from launch.substitutions import Command
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

import os

from launch.conditions import IfCondition
from launch.conditions import UnlessCondition


packagepath = get_package_share_directory('arm_control')
file_path = packagepath + '/config/arm_ros2_control.xacro'


def generate_launch_description():

    actions = []

    actions.append(
        DeclareLaunchArgument(
            'use_gazebo',
            default_value='false',
            description='Whether to use Gazebo simulation',
            choices=['true', 'false', 'True', 'False']
        )
    )

    actions.append(
        DeclareLaunchArgument(
            'control_file',
            default_value='test_arm_action.py',
            description='choice the control file',
            choices=[
                'test_arm_action.py',
                'test_arm_publisher.py',
                'test_arm_hand.py'
            ]
        )
    )

    use_gazebo = LaunchConfiguration('use_gazebo', default='false')
    control_file = LaunchConfiguration('control_file', default='test_arm_action.py')

    robot_desc = Command(['xacro ', file_path, ' use_gazebo:=', use_gazebo])


    actions.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(
                    get_package_share_directory('arm_control'),
                    'launch'),
                 '/arm_gazebo_launch.py']
            ),
            launch_arguments=[('robot_desc', robot_desc)],
            condition=IfCondition(use_gazebo)
        )
    )


    controller_manager_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[packagepath + '/config/arm_controllers.yaml'],
        name='controller_manager',
        output='both',
        condition=UnlessCondition(use_gazebo)
    )


    robot_desc_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            {'use_sim_time': True},
            {'robot_description': robot_desc}
        ]
    )


    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        arguments=['-d', packagepath + '/config/rviz.rviz']
    )


    controllers_node = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'arm_controller',
            'hand_controller',
            'joint_state_broadcaster'
        ],
        output='screen',
        name='controllers'
    )


    arm_control_node = Node(
        package='arm_control',
        executable=control_file
    )


    actions.extend([
        controllers_node,
        robot_desc_node,
        rviz_node,
        controller_manager_node,
        TimerAction(
            period=5.0,
            actions=[arm_control_node],
        )
    ])


    return LaunchDescription(actions)