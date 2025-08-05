import os
import sys

if hasattr(sys, "frozen") and sys.frozen == "windows_exe":
    os.chdir(os.path.dirname(sys.executable))

from tkinter import Tk

root = Tk()

from app.plugins.main import main
cl = main.App(root)
root.mainloop()

