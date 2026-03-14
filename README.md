# Arm Control Package

这是一个基于 ROS 2 Humble 的机械臂控制和仿真包。支持在 RViz2 中的纯显示控制，也可以借助 Gazebo 进行完整的物理联合仿真。

> **参考学习来源:**
> 相关实现与灵感来源于 B站教程：[ROS2 机械臂联合仿真与控制](https://www.bilibili.com/video/BV1SGYRzBEEm)

## 环境依赖
* Ubuntu 22.04
* ROS 2 Humble
* Gazebo (Ignition Fortress)
* ros2_control & gz_ros2_control

## 编译与环境配置

在运行前，请确保在工作空间根目录下完成编译和环境变量加载：

```bash
cd ~/arm_control_ws
colcon build
source install/setup.bash
```

> **注意：** 每次新开一个终端窗口跑 ROS2 节点前，都需要执行 `source install/setup.bash`。

---

## 运行模式及使用步骤

本代码包通过 `arm_control_launch.py` 控制各种启动模式。你可以组合控制台参数以适应不同的需求场景：

### 模式一：纯 RViz 显示（不加载控制脚本）
这是最基础的模式。它会加载机器人的 URDF 描述文件，启动 `ros2_control` 以及状态发布器，并在 RViz 中显示机器人模型。默认不带有物理仿真，也不自动运行控制脚本。

```bash
ros2 launch arm_control arm_control_launch.py
```

### 模式二：RViz 显示 + 自动加载控制动作脚本
如果你想观察默认的自动控制脚本如何驱动机械臂运动，可以通过赋予 `control_file` 参数来告知系统在启动5秒后自动运行对应的 Python 动作节点。

```bash
# 自动运行 test_arm_action.py 控制器
ros2 launch arm_control arm_control_launch.py control_file:=test_arm_action.py

# 自动运行 test_arm_publisher.py 控制器
ros2 launch arm_control arm_control_launch.py control_file:=test_arm_publisher.py
```

### 模式三：完全物理仿真 (Gazebo + RViz)
如果你想要引入重力和物理碰撞，需要启动 Gazebo 仿真环境。此模式下，原先的虚拟硬件接口（Mock Hardware）会被 `gz_ros2_control` 插件替换为真实物理系统的插件。

```bash
# 启动 Gazebo 仿真阵列（默认不加载控制脚本）
ros2 launch arm_control arm_control_launch.py use_gazebo:=true
```

当 Gazebo 窗口弹出后，点击 Gazebo 左下角的 **运行(Play)** 按钮（`▶`），让物理时间流逝，RViz2 中的机械臂姿态便会自动对齐，相关状态控制器也会完成初始化。

### 模式四：完全物理仿真 + 自动加载控制动作脚本
结合前两者的参数，可以同时进行 Gazebo 物理仿真并指派对应的动作脚本来操控机械臂。

```bash
ros2 launch arm_control arm_control_launch.py use_gazebo:=true control_file:=test_arm_action.py
```
*(注意：同样需要在启动 Gazebo 后点选“Play”让仿真时间流逝，动作服务端才能接收到客户端发送来的轨迹)*

---

## 问题排查

*   **节点因没有权限卡住 (Operation not permitted)：** 
    通常是由于 `ros2_control` 尝试设置实时线程(RT scheduler)没有权限出现的黄色警告。只要不致命，完全可以忽略；若为了更平滑的控制性能，请按照 ROS 2 官方文档调整系统极限权限即可。
*   **动作脚本没反应：**
    Gazebo 默认启动是处于**暂停**状态的。你需要检查 Gazebo 的时间是否在前进。点击界面底部的播放按钮使时间正常走动，控制命令才会被底层控制器接收响应。
