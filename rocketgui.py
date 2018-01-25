import tkinter as tk
import matplotlib
import matplotlib.animation as animation
import urllib
import json
import pandas as pd
import numpy as np
import os

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style
from tkinter import ttk

style.use('ggplot')
matplotlib.use("TkAgg")

# The font used in all of the text
LARGE_FONT = ("Verdana", 12)


# Figures for each individual page
accelerationFig = Figure(figsize = (5, 4), dpi = 100)
tempPressFig = Figure(figsize = (5, 4), dpi = 100)

# plots that go in the figures on the pages
accelerationPlot = accelerationFig.add_subplot(111)
tempPlot = tempPressFig.add_subplot(211)
pressPlot = tempPressFig.add_subplot(212)

class RocketGUI(tk.Tk):
  def __init__(self, *args, **kwargs):
    # call init of the parent class
    tk.Tk.__init__(self, *args, **kwargs)

    tk.Tk.wm_title(self, "Rocket Realtime Data Visualization")

    container = tk.Frame(self)
    # way of populating and situating widgets in a frame: pack (other is grid)
    container.pack(side = "top", fill = "both",expand = True)
    # just some config settings
    container.grid_rowconfigure(0, weight = 1)
    container.grid_columnconfigure(0, weight = 1)

    self.frames = {}
    # creates all the frames to be used in the application
    # frames are the individual tabs
    for F in (StartPage, PageOne, AccelerationPage, TempPressPage):
      frame = F(container, self)
      self.frames[F] = frame
      frame.grid(row = 0,column = 0,sticky = "nsew")
    # we are placing our widgets in a grid (0,0) here and sticky says what direction to stretch in
    # in this case sticky is all 4 directions (north, south, east, west)

    # show_frame is a method to show the frame
    self.show_frame(StartPage)


  def show_frame(self, controller):
    frame = self.frames[controller]
    # brings frame to top for user to see
    frame.tkraise()

# class that is a frame in out tk gui application
class StartPage(tk.Frame):

  def __init__(self, parent, controller):
    # call the init of the parent class
    tk.Frame.__init__(self, parent)
    # make a simple label
    label = ttk.Label(self, text = "This is the Start Page", font = LARGE_FONT)
    # add padding on the left and y axis
    label.pack(pady = 10, padx = 10)

    accelButton = ttk.Button(self, text = "View Acceleration", command = lambda: controller.show_frame(AccelerationPage))
    accelButton.pack()

    tempPressButton = ttk.Button(self, text = "View Temperature and Pressure", command = lambda: controller.show_frame(TempPressPage))
    tempPressButton.pack()

    quitButton = ttk.Button(self, text = "Quit", command = quit)
    quitButton.pack()

class PageOne(tk.Frame):

  def __init__(self, parent, controller):
    tk.Frame.__init__(self, parent)
    label = ttk.Label(self, text = "Page One!!!", font=LARGE_FONT)
    label.pack(pady = 10,padx = 10)

    button1 = ttk.Button(self, text = "Back to Home", command = lambda: controller.show_frame(StartPage))
    button1.pack()

    button2 = ttk.Button(self, text = "Page Two",command = lambda: controller.show_frame(PageTwo))
    button2.pack()

class AccelerationPage(tk.Frame):

  def __init__(self, parent, controller):
    # typical navigation stuff
    tk.Frame.__init__(self, parent)
    label = tk.Label(self, text = "Magnitude of Acceleration / Time Unit", font = LARGE_FONT)
    label.pack(pady = 10,padx = 10)
    # canvas setup
    canvas = FigureCanvasTkAgg(accelerationFig, self)
    canvas.show()
    canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
    # toolbar
    toolbar = NavigationToolbar2TkAgg(canvas,self)
    toolbar.update()
    canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)

    button1 = ttk.Button(self, text = "Back to Home", command = lambda: controller.show_frame(StartPage))
    button1.pack()

class TempPressPage(tk.Frame):
  
  def __init__(self, parent, controller):
    tk.Frame.__init__(self, parent)
    label = tk.Label(self, text = "Temperature and Pressure / Time Unit", font = LARGE_FONT)
    label.pack(pady = 10, padx = 10)
    # canvas setup 
    canvas = FigureCanvasTkAgg(tempPressFig, self)
    canvas.show()
    canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
    # toolbar
    toolbar = NavigationToolbar2TkAgg(canvas,self)
    toolbar.update()
    canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
    
    button = ttk.Button(self, text = "Back to Home", command = lambda: controller.show_frame(StartPage))
    button.pack()


def qf(quickPrint):
  print(quickPrint)

def animateAcceleration(i):
  # this function animates the data being pulled from the file
  pullData = open('sampleText.txt','r').read()
  dataArray = pullData.split('\n')
  xar=[]
  yar=[]
  for eachLine in dataArray:
      if len(eachLine)>1:
          x,y = eachLine.split(',')
          xar.append(int(x))
          yar.append(int(y))
  accelerationPlot.clear()
  accelerationPlot.plot(xar,yar)

app = RocketGUI()
accelerationAnimation = animation.FuncAnimation(accelerationFig, animateAcceleration, interval = 1000)
app.mainloop()

