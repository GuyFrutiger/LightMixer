# LightMixer
Dynamic Nuke & Houdini LightMixing tool
(Houdini HDA only compatible with python 3.8 and up due to use of a walrus operator)

Current version: 1.0

Tool info and Tutorial:
https://www.guyfrutiger.com/toolbench

### HOW TO INSTALL: 

Nuke Gizmo:
1. Unzip the archive
2. Drag and drop the folder in your .nuke folder
    - Make sure your folder is called LightMixer (You might need to rename it)
3. Add this code to your init.py file which can be found in your .nuke folder. If you don't have one you can simply create one.
```
    nuke.pluginAddPath('./LightMixer')
```
4. Run Nuke


Houdini HDA: 

Simple install in current .hip file:
1. Open your .hip file 
2. File -> Import -> Houdini Digital Asset -> Navigate to where the Houdini HDA is on your disk. -> Install

Studio wide & permanent installs might vary. Check this page from SideFx for further information: 
https://www.sidefx.com/docs/houdini/assets/install.html




