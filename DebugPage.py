from tkinter import *

class DebugPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Debug Page")
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 