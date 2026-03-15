from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node
from launch.actions import TimerAction, ExecuteProcess, OpaqueFunction
from launch.substitutions import Command
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

import os

from launch.conditions import IfCondition
from launch.conditions import UnlessCondition
from launch.conditions import LaunchConfigurationNotEquals


packagepath = get_package_share_directory('dummy_control')
file_path = packagepath + '/config/dummy_ros2_control.xacro'


def _launch_control_file(context):
    """Decide how to launch the control file at runtime."""
    cf = context.launch_configurations.get('control_file', '')
    if not cf:
        return []
    if cf == 'test_dummy_keyboard.py':
        # Keyboard control needs a real TTY, open in a new terminal window
        return [ExecuteProcess(
            cmd=['gnome-terminal', '--', 'bash', '-c',
                 'ros2 run dummy_control test_dummy_keyboard.py; exec bash'],
        )]
    else:
        return [Node(
            package='dummy_control',
            executable=cf,
        )]


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
            default_value='',
            description='choice the control file',
            choices=[
                '',
                'test_dummy_action.py',
                'test_dummy_publisher.py',
                'test_dummy_hand.py',
                'test_dummy_keyboard.py'
            ]
        )
    )

    use_gazebo = LaunchConfiguration('use_gazebo', default='false')

    robot_desc = Command(['xacro ', file_path, ' use_gazebo:=', use_gazebo])


    actions.append(
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                [os.path.join(
                    get_package_share_directory('dummy_control'),
                    'launch'),
                 '/dummy_gazebo_launch.py']
            ),
            launch_arguments=[('robot_desc', robot_desc)],
            condition=IfCondition(use_gazebo)
        )
    )


    controller_manager_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[packagepath + '/config/dummy_controllers.yaml'],
        remappings=[
            ('~/robot_description', '/robot_description'),
        ],
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
            'joint_state_broadcaster',
            '--param-file', packagepath + '/config/dummy_controllers.yaml'
        ],
        output='screen',
        name='controllers'
    )


    actions.extend([
        controllers_node,
        robot_desc_node,
        rviz_node,
        controller_manager_node,
        TimerAction(
            period=5.0,
            actions=[OpaqueFunction(function=_launch_control_file)],
        )
    ])


    return LaunchDescription(actions)
