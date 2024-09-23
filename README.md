# YAW

**Y**et **a**nother **w**orkflow. Workflow to automate repetitive process, build with Python and Bash.

Version: v1.0

## Description
YAW parses recipie files (in YAML) which contais several steps. Each step contains several parameters that tune the execution of the step.
The most important parameter is the _type_, which uses a pre-defined workflow for different tasks.

![YAW](https://github.com/user-attachments/assets/97c26c4e-9ba8-40cf-9f20-03c87646e4de)

The most powerfull capability of this tool is the ability of generate recipe variations; if the recipe contains a multivalue parameter (list)
YAW automatically generates all the combinations (cartesian mode) or joins by order the different values(zip mode)

## Installation
Add the `bin` folder to the path of your system and call `yaw` to execute the application.

## Usage
1. Generate recipe template: Use `--generate <recipie type>` to generate and empty template.

2. Run recipies: Use `yaw <recipe file(s)>` to run the recipies


## Example
TBD

## Extending the functionalities

YAW is designed following a modular design, despite is hardly recommended to 
tune your functionalities using your bash scripts you can also extend YAW
core to add **new types of recipie runners**.



