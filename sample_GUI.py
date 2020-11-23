from tkinter import *

class car_station_app(Tk):
    def __init__(self, *args, **kwargs):  
        
        # __init__ function for class Tk 
        Tk.__init__(self, *args, **kwargs) 
        
        # creating a container 
        container = Frame(self)   
        container.pack(side = "top", fill = "both", expand = True)  

        container.grid_rowconfigure(0, weight = 1) 
        container.grid_columnconfigure(0, weight = 1) 

        # initializing frames to an empty array 
        self.frames = {}   

        # iterating through a tuple consisting 
        # of the different page layouts 
        for F in (StartPage, Page1, Page2): 

            frame = F(container, self) 

            # initializing frame of that object from 
            # startpage, page1, page2 respectively with  
            # for loop 
            self.frames[F] = frame  

            frame.grid(row = 0, column = 0, sticky ="nsew") 

        self.show_frame(StartPage) 

    # to display the current frame passed as 
    # parameter 
    def show_frame(self, cont): 
        frame = self.frames[cont] 
        frame.tkraise() 
class StartPage(Frame): 
    def __init__(self, parent, controller):  
        Frame.__init__(self, parent) 
          
        # label of frame Layout 2 
        label = Label(self, text ="Startpage") 
          
        # putting the grid in its place by using 
        # grid 
        label.grid(row = 0, column = 4, padx = 10, pady = 10)  
   
        button1 = Button(self, text ="Page 1", 
        command = lambda : controller.show_frame(Page1)) 
      
        # putting the button in its place by 
        # using grid 
        button1.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        ## button to show frame 2 with text layout2 
        button2 = Button(self, text ="Page 2", 
        command = lambda : controller.show_frame(Page2)) 
      
        # putting the button in its place by 
        # using grid 
        button2.grid(row = 2, column = 1, padx = 10, pady = 10) 
   
           
   
   
# second window frame page1  
class Page1(Frame): 
      
    def __init__(self, parent, controller): 
          
        Frame.__init__(self, parent) 
        label = Label(self, text ="Page 1") 
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        # layout2 
        button1 = Button(self, text ="StartPage", 
                            command = lambda : controller.show_frame(StartPage)) 
      
        # putting the button in its place  
        # by using grid 
        button1.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        # layout2 
        button2 = Button(self, text ="Page 2", 
                            command = lambda : controller.show_frame(Page2)) 
      
        # putting the button in its place by  
        # using grid 
        button2.grid(row = 2, column = 1, padx = 10, pady = 10) 
   
   
   
   
# third window frame page2 
class Page2(Frame):  
    def __init__(self, parent, controller): 
        Frame.__init__(self, parent) 
        label = Label(self, text ="Page 2") 
        label.grid(row = 0, column = 4, padx = 10, pady = 10) 
   
        # button to show frame 2 with text 
        # layout2 
        button1 = Button(self, text ="Page 1", 
                            command = lambda : controller.show_frame(Page1)) 
      
        # putting the button in its place by  
        # using grid 
        button1.grid(row = 1, column = 1, padx = 10, pady = 10) 
   
        # button to show frame 3 with text 
        # layout3 
        button2 = Button(self, text ="Startpage", 
                            command = lambda : controller.show_frame(StartPage)) 
      
        # putting the button in its place by 
        # using grid 
        button2.grid(row = 2, column = 1, padx = 10, pady = 10) 
   
   
# Driver Code


root=car_station_app()
root.attributes("-fullscreen", True)
root_height = root.winfo_height()

root.columnconfigure(0, weight=45)
root.columnconfigure(1, weight=55)
root.rowconfigure(0, weight=10)
root.rowconfigure(1, weight=1)

menu = Listbox(root, highlightthickness = '3', selectmode = BROWSE)

btn = Button(root, text = "Print width")

menu.insert(1, 'General')
menu.insert(2, 'Driver')
menu.insert(3, 'Vehicle information')
menu.insert(4, 'Transaction History')
menu.insert(5, 'Debug')

menu.grid(sticky="nsew", column = 0, row = 0)

root.mainloop() 