# Improvisational Machines: Live Coding Industrial Robots
A four-day workshop bringing live coding principles, dynamic interfaces, and flexibles workflows into industrial robotics.

- Faculty: [Madeline Gannon](https://atonaton.com/)
- Faculty Assistant: [Huanyu Li](https://huanyuli.com/)

![](https://adsknews.autodesk.com/app/uploads/2016/11/MadelineinAutodesk_Boston_BUILD.png)

_Developed for the Institute for Advanced Architecture of Catalonia's Master in Robotics & Advanced Construction program._

## About
Industrial robots are conventionally programmed with software tools designed for reliability, precision, and repeatability. However, these workflows can be counterproductive in situations where real-time experimentation and problem solving needs to be the priority. For example, using industrial robots in dynamic environments—like construction sites—or for creative applications requires a level of spontaneous exploration and adaptation that can be very difficult to achieve with traditional CAD/CAM tools.

In this workshop, participants will learn how emerging live coding techniques can transform the way we engage with these powerful machines, and enable more dynamic and improvisational workflows. Through hands-on exercises, attendees will explore tools and techniques that allow for immediate feedback, iterative development, and a more fluid, creative approach to working with industrial robots. The focus will be on developing workflows that support rapid trial and error, hands-on discovery, and real-time problem-solving.

### Topics Covered
- Introduction to live coding principles
- Overview of tools & frameworks for real-time robot control
- Strategies for improvisational workflows with robots
- Safety considerations & best practices for dynamic environments
- Hands-on coding exercises & experimentation

### Learning Objectives
By the end of the workshop, attendees will:
- Understand the limitations of traditional industrial robot programming.
- Learn live coding techniques for real-time robot control.
- Explore workflows that encourage rapid prototyping and iteration.
- Implement safety best practices for working with industrial robots in dynamic environments.

## Lectures
1. [Introduction](https://docs.google.com/presentation/d/1PpFi8xqpPCxH_vHQGHs4E_36oapiLV6ezxv87PvaDPE/edit?usp=sharing)
  - What is Live Coding?
  - How live coding can help with programming Industrial Robots?
  - Unique advantages of different simulation tools
  - Intro to [Madeline Gannon](https://atonaton.com/)
  - Special Guest Lecture: [Char Stiles](https://charstiles.com/)
2. [Robot Motion](https://docs.google.com/presentation/d/1PDAVhUQRzeNh4MJ04djh2lxZirk3RrrKuliJqdh7yZo/edit?usp=sharing)
  - Nuances of Industrial Kinematics
  - Moving through Cartesian, Joint, and Torque Control
  - Introduction to ABB RobotStudio
3. [Robot Communication](https://docs.google.com/presentation/d/1DhcGB-Zu-pBoXzOxoIGn63gKD__qfvLFgHvADB2jzgw/edit?usp=sharing)
  - Pros and Cons: Offline versus Online
  - Pros and Cons: Realtime versus Real-ish time
4. Robot Interfaces
  - MIDI Controllers
  - [TouchOSC](https://hexler.net/touchosc#get)
  - Rhino/Grasshopper Python Nodes
  - Sensors

## Exercises
1. [Hello World](exercises/hello_world/): Write & run your first RAPID module
2. [Draw Square](exercises/draw_square/): Make the robot move in RAPID
3. [Basic Client/Server](exercises/client_server_basic/): Send command line messages from Python client (or Grasshopper) to the ABB Robot
4. [Multi-Task Client/Server](exercises/client_server_multitask/): Send messages to control program flow of the ABB Robot
5. [Input Devices](exercises/hid/): Python snippets for sending/receiving MIDI and OSC messages


## Final Project
This is a _one day speed project_ to integrate the live coding tools and principles we've been learning into an application of your choosing.
Consider how to harness our newly created flexible workflows to avoid programming painpoints, iterate with rapid trial-and-error, or unlock an interactive experience between people and the robots.

- Use the [Communication Manager](com_manager/) to send/receive MIDI, OSC, TCP messages between many clients and many ABB Robots.
- Use the [RobotStudio workcell](RobotStudio/) to accurately simulate your real-time communications and controls.

### IaaC MRAC 2025 (Barcelona)

#### [Reflection](https://blog.iaac.net/reflection/)
_Reflection_ is an interactive installation where two robots create immersive geometry using mirrors, lasers, and smoke machines.

![](https://blog.iaac.net/wp-content/uploads/2025/06/01.png)

Team members: Elizabeth Frias, Javier Albo, Marianne Weber and Carlos Larraín

#### [HearMeOut](https://blog.iaac.net/workshop-3-2-hearmeout/)
_HearMeOut_ is an experimental workflow project that uses LLMs to generate robot motion commands based on Natual Language Input.

![](https://blog.iaac.net/wp-content/uploads/2025/06/Screenshot-2025-06-16-at-11.25.05%E2%80%AFAM.png)

Team members: Krystyne Kontos, Lauren Deming and Santosh Prabhu Shenbagamoorthy
