import sys
import subprocess
import os
import platform
import bpy

# taken from https://github.com/luckychris/install_blender_python_modules/blob/main/install_blender_python_module.py

def isWindows():
    return os.name == 'nt'

def isMacOS():
    return os.name == 'posix' and platform.system() == "Darwin"

def isLinux():
    return os.name == 'posix' and platform.system() == "Linux"

def python_exec():
    if isWindows():
        return os.path.join(sys.prefix, 'bin', 'python.exe')


def installModule(packageName):

    try:
        subprocess.call([python_exe, "import ", packageName])
    except:
        python_exe = python_exec()
       # upgrade pip
        subprocess.call([python_exe, "-m", "ensurepip"])
        subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
       # install required packages
        subprocess.call([python_exe, "-m", "pip", "install", packageName])