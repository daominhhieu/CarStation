from tkinter import *
from tkinter import font

class DebugPage(Frame):
    def __init__(self, parent, controller):
        customfont = font.Font(size = 20)
        Frame.__init__(self, parent)
        label = Label(self, text ="Debug Page", font = customfont)
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 