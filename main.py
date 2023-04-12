from tkinter import *
from controller import *

# must be at least 25
SIZE = 25

def main():
    if SIZE < 25:
        raise Exception("SIZE must be at least 25")
    root = Tk()
    controller = Controller(root, size=SIZE)
    controller.mainloop()

if __name__ == "__main__":
    main()