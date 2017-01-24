# pyroborace
![Python: v3.5](https://img.shields.io/badge/python-v3.5-blue.svg?style=plastic)
[![Build Status: Linux](https://img.shields.io/travis/robotika/pyroborace/master.svg?style=plastic&label=linux tests)](https://travis-ci.org/robotika/pyroborace)
[![Build Status: Windows](https://img.shields.io/appveyor/ci/robotika/pyroborace/master.svg?style=plastic&label=windows tests)](https://ci.appveyor.com/project/robotika/pyroborace)

Python driver for Formula-E Roborace

The official API is not available yet, so we will start from UDP protocol
described here:

 * https://github.com/vadbut/Roborace-Dreams/tree/dev/Info_Roborace

## Installation (Windows)

1) download and install official base package for Speed Dreams 2
[speed-dreams-base-2.2.1-r6404-win32-setup.exe](https://sourceforge.net/projects/speed-dreams/files/2.2.1/speed-dreams-base-2.2.1-r6404-win32-setup.exe/download) (148MB)

2) download patch with DLL for UDP robot and Robocar configuration
[speed-dreams-2.2.1-roborace.zip](https://drive.google.com/file/d/0B1UoOlZhZcoiR0Q1eU9abGFPTUk/view?usp=sharing) (10MB)

Note, that this is just a short cut how to avoid download od 2.2GB repository
and 7.5GB complete build of Speed Dreams 2.

## Version 0

The simplest "UDP robot" is "ver0.py". Press the gas to 50% and ignore inputs.
Never-the-less the car bumps from the mantinels and moves a bit.

## Demo with track description

Proper "hello world" version needs description of the track. A simple demo
is implemented in "demo.py" file. There is one parameter --- a path to XML
track.

![Robocar in rear mirrow](http://robotika.cz/competitions/formula-e-roborace/sd2-roborace-ver2-in-mirror.jpg)
