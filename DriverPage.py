from tkinter import *
from tkinter import font

class DriverPage(Frame):
    def __init__(self, parent, controller):
        customfont = font.Font(size = 20)
        Frame.__init__(self, parent)
        label = Label(self, text ="Driver Page", font = customfont)
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 