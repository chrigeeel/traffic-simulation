"""
Description: A simulation environment for car traffic with cellular automata
The program encapsules four files: main.py, controller.py, model.py, view.py
Author: Christian Tognazza
Datum: 13.04.2023
"""

from tkinter import *

from controller import *

# must be between 25 and 50
SIZE = 50


def main():
    if SIZE < 25 or SIZE > 75:
        raise Exception("SIZE must be between 25 and 75")
    root = Tk()
    controller = Controller(root, size=SIZE)
    controller.mainloop()


if __name__ == "__main__":
    main()
