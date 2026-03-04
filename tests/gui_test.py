
def test_gui():
    import os
    os.environ["PYOPENGL_PLATFORM"] = "glx"

    from phaast.gui.gui import GUI

    GUI()
