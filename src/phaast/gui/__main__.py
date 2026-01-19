import os
os.environ["PYOPENGL_PLATFORM"] = "glx"

from phaast.gui.gui import GUI

root = GUI()
root.run()
