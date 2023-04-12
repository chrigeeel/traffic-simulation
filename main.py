from tkinter import *
from controller import *

SIZE = 50

def main():
    root = Tk()
    controller = Controller(root, size=SIZE)
    controller.mainloop()

if __name__ == "__main__":
    main()