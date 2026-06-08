# YAW

**Y**et **a**nother **w**orkflow. Workflow to automate repetitive processes, build with Python and Bash.

Version: v0.96.0 - Alpha

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Creating your runner - Runner hierarchy](#creating-your-runner---runner-hierarchy)
  - [AbstractRunner - Minimal parameters](#abstractrunner---minimal-parameters)
  - [SlurmAbstractRunner - SLURM parameters](#slurmabstractrunner---slurm-parameters)
  - [BashRunner](#bashrunner)
  - [BashSlurmRunner](#bashslurmrunner)
- [Examples](#examples)
- [Using pytests](#using-pytests)

## Introduction
YAW parses recipe files (in YAML format) and executes each step described in the recipe. Each step contains several parameters that tune the execution of the step.

![YAW]()

The most powerful capability of this tool is the ability to generate recipe variations; if the recipe contains a multivalue parameter (list)
YAW automatically generates all the combinations (cartesian mode) or joins by order of the different values(zip mode). This allows systematical executions
with only writing a YAML file. There are several "runners" available and you can extend the runnerns for a custom use case.

## Installation
Clone the repository ...

Alternatively, you can install the YAW package using ...

## Usage
1. Generate recipe template: Use `--generate <recipie type>` to generate an empty template.
2. Fill the YAML file with your values for the required parameters.
3. Run recipies: Use `yaw <recipe file(s)>` to run the recipies. YAW will first parse the recipes and then run them sequentially.
4. Check the results: Check the output from the command line to see the execution results.

## Creating your runner - Runner hierarchy
YAW was defined using a object-oriented hierarchy to be easy to extend:

| TODO: Add UML here!

### AbstractRunner - Minimal parameters

The abstract runner defines the minimal parameters to execute something. It manages:

* type: Set the runner type
* mode: Set the mode for multirecipie parameters. `zip` by default
* track_env: Dump the environment to a file. `env.log` by default
* create_dir: Create the rundir to execute the recipie. 
* overwrite: Overwrite the rundir if exists.
* dry: Not execute anything, just set the rundir. `false` by default
* mirror: Generate mirror runners.
* log_name: Dump the execution to a log file
* env_file: Set the environment file.
* rundir: Set the rundir to execute the runner. If not set, it will be set to the current path where YAW was invoked.

It also defines the two execution steps, a first one where the parameters are managed and a second one where the execution happens.


## Examples
TBD

### Using pytests
TBD