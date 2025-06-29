# YAW

**Y**et **a**nother **w**orkflow. Workflow to automate repetitive processes, build with Python and Bash.

Version: v0.96.0 - Alpha

- [YAW](#yaw)
  - [Introduction](#introduction)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Examples](#examples)
  - [Extending the functionalities](#extending-the-functionalities)
    - [UML overview - Runners](#uml-overview---runners)
    - [Creating your runner](#creating-your-runner)


## Introduction
YAW parses recipe files (in YAML format) and executes each step described in the recipe. Each step contains several parameters that tune the execution of the step.

![YAW](https://github.com/user-attachments/assets/97c26c4e-9ba8-40cf-9f20-03c87646e4de)

The most powerful capability of this tool is the ability to generate recipe variations; if the recipe contains a multivalue parameter (list)
YAW automatically generates all the combinations (cartesian mode) or joins by order of the different values(zip mode). This allows systematical executions
with only writing a YAML file. There are several "runners" available and you can extend the runnerns for a custom use case.

## Installation
Clone the repository with `--recursive` or initialize the submodules.
````bash
git clone git@github.com:correalramos24/YAW.git --recursive
# OR
git clone git@github.com:correalramos24/YAW.git
cd YAW
git submodule init
git submodule update
````
Add the `bin` folder to the path of your system and call `yaw` to execute the application.

## Usage
1. Generate recipe template: Use `--generate <recipie type>` to generate an empty template.

2. Run recipies: Use `yaw <recipe file(s)>` to run the recipies. YAW will first parse the recipes and then run them sequentially.

3. Check the results: Check the output from the command line to see the execution results.

## Runner hierarchy
YAW was defined using a object-oriented hierarchy to be easy to extend.

### AbstractRunner - Minimal parameters

The abstract runner defines the minimal parameters to execute something. It manages:

* type: Set the runner type
* mode: Set the mode for multirecipie parameters. `zip` by default
* log_file: Dump the execution to a log file
* env_file: Set the environment file.
* track_env: Dump the environment to a file. `env.log` by default
* rundir: Set the rundir to execute the runner. If not set, it will be set to the current path where YAW was invoked.
* create_dir: Create the rundir. 
* overwrite: Overwrite the rundir
* same_rundir: Execute all the multirecipies in the same rundir. `false` by default.
* dry: Not execute anything, just set the rundir. `false` by default
* mirror: Generate mirror runners.
* verbose: Be verbose with this step. `false` by default.

It also defines the two execution steps, a first one where the parameters are managed and a second one where the execution happens.

### SlurmAbstractRunner - SLURM parameters

Define an interface to interact with SLURM jobs. 

### BashRunner

Extends the abstract runner to execute commands using bash and inflate the rundir 
with input files.

### BashSlurmRunner
TBD

## Examples
TBD

## Extending the functionalities

Despite being recommended to tune your functionalities using your bash scripts you can also extend YAW
core to support **new types of recipie**. This section will briefly summarize the modular design,
to make it easy to extend the functionalities of this application.

### UML overview - Runners

TBD

### Creating your runner

TBD


### Using pytests

There is support of use unittest. To use them you need to:

````bash
# Go to yaw folder
source tests/test_env.sh
python3 tests/test_your_test_name.py
````
