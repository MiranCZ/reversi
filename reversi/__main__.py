def win_resize_hotfix():
    """
    fixes weird windows resize issue
    from: https://stackoverflow.com/a/32063729
    """

    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

def deps_loaded() -> bool:
    try:
        import setuptools, pygame, cython
    except ImportError:
        return False
    return True


def cython_built():
    try:
        import reversi.bot.optimized.montecarlo
    except:
        return False
    return True



def load_deps():
    deps = deps_loaded()
    cython = cython_built()

    if deps and cython:
        return
    print("Attempting to automatically install dependencies...")

    import subprocess
    import sys

    if deps and not cython:
        subprocess.run([sys.executable, "setup.py", "build_ext", "--inplace"])
        return

    subprocess.run([sys.executable, "pip", "install", "."])

    try:
        import pygame
    except ImportError:
        import tkinter.messagebox
        tkinter.messagebox.showerror("Failed to load pygame!", "Attempt to automatically install pygame has failed")
        exit(-1)

    if not cython_built():
        print("Failed to build cython file!")

def module_accessible():
    return __package__ is not None and __package__ != ""

if __name__ == '__main__':
    import os
    import sys
    import pathlib

    script_dir = os.path.abspath(pathlib.Path(__file__).parent.parent)
    os.chdir(script_dir)
    print("Set cmd directory to",script_dir)

    if not module_accessible():
        import subprocess

        print("HOTFIX: Trying to run app as module...")
        subprocess.run([sys.executable, "-m", "reversi"])
        exit(0)


    load_deps()
    win_resize_hotfix()

    # FIXME not the ideal way to run things xd...
    import reversi.ui.screen
