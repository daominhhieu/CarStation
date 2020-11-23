from tkinter import *

class car_station_app(Tk):
    def __init__(self, *args, **kwargs):  
        
        # __init__ function for class Tk 
        Tk.__init__(self, *args, **kwargs) 
        
        self.columnconfigure(0, weight=45)
        self.columnconfigure(1, weight=55)
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=1)
        self.attributes("-fullscreen", True)

        self.M_section = MenuSection(self, self)
        self.M_section.grid(column = 0, row = 0, sticky = 'nsew')

        # creating a container 
        container = Frame(self)
        
        container.grid(column = 1, row =0, sticky = 'nsew')

        # initializing frames to an empty array 
        self.frames = {}   
        

        # iterating through a tuple consisting 
        # of the different page layouts 
        for F in (GeneralPage, DriverPage, VehicleInormationPage, TransactionHistoryPage, DebugPage): 

            frame = F(container, self) 

            # initializing frame of that object from 
            # startpage, page1, page2 respectively with  
            # for loop 
            self.frames[F] = frame  

            frame.grid(row = 0, column = 1, sticky ="nsew") 

        self.show_frame(GeneralPage)

    # to display the current frame passed as 
    # parameter 
    def show_frame(self, cont): 
        frame = self.frames[cont] 
        frame.tkraise() 

class GeneralPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Genral Page")
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 

class DriverPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Driver Page")
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 

class VehicleInormationPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Vehicle Inormation Page")
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 

class TransactionHistoryPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Transaction History Page")
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 

class DebugPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text ="Debug Page")
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 

class MenuSection(Listbox):  
    def __init__(self, parent, controller): 
        Listbox.__init__(self, parent,highlightthickness = '3', selectmode = BROWSE)
        self.controller = controller

        self.insert(0, 'General')
        self.insert(1, 'Driver')
        self.insert(2, 'Vehicle information')
        self.insert(3, 'Transaction History')
        self.insert(4, 'Debug')
        
        self.bind('<<ListboxSelect>>', self.show_frame)
    
    def show_frame(self, event):
        for item in self.curselection():
            if(item == 0):
                self.controller.show_frame(GeneralPage)
            elif(item == 1):
                self.controller.show_frame(DriverPage)
            elif(item == 2):
                self.controller.show_frame(VehicleInormationPage)
            elif(item == 3):
                self.controller.show_frame(TransactionHistoryPage)
            elif(item == 4):
                self.controller.show_frame(DebugPage)   

   
# Driver Code


root=car_station_app()


root.mainloop() 