from tkinter import *

class VehicleInormationPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Vehicle Inormation Page")
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 