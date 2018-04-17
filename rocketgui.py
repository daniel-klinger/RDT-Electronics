
'''
serial - for sending data to and from external devices like the accelerometer
sys - for information about hardware on this system
math - for math related functions
logging - for clear and pretty output 
'''
try:
  import serial
except ImportError:
  pass
import sys
import logging
import tkinter as tk
import matplotlib
import matplotlib.animation as animation
import math
import time

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style
from tkinter import ttk

style.use('ggplot')
matplotlib.use("TkAgg")

#ser = serial.Serial('dev/ttyUSB0')
# The font used in all of the text
LARGE_FONT = ("Verdana", 12)

# create formatters for the logger
format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
rawformat = logging.Formatter('%(message)s')
# initialize our logger
logger = logging.getLogger("groundServer")
logger.setLevel(logging.DEBUG)
# create a file to log data to
fileHandler = logging.FileHandler("data.log", mode = "a", delay = True)
fileHandler.setFormatter(format)
fileHandler.setLevel(logging.INFO)
logger.addHandler(fileHandler)
# create file to log raw data to
fileHandler = logging.FileHandler("raw.log", mode = "a", delay = True)
fileHandler.setFormatter(rawformat)
fileHandler.setLevel(logging.DEBUG)
logger.addHandler(fileHandler)
# create a handler that prints out thing to stdout
outHandler = logging.StreamHandler(sys.stdout)
outHandler.setFormatter(format)
outHandler.setLevel(logging.INFO)
logger.addHandler(outHandler)
# set the level to info so we don't get so much spam

# Figures for each individual page
accelerationFig = Figure(figsize = (5, 4), dpi = 100)
tempPressFig = Figure(figsize = (5, 4), dpi = 100)

# plots that go in the figures on the pages
accelerationPlot = accelerationFig.add_subplot(111)
tempPlot = tempPressFig.add_subplot(211)
pressPlot = tempPressFig.add_subplot(212)

buffer = {
  "berryImuData": "",
  "gpsData": "",
  "gpioData": ""
}

class RocketGUI():
  def __init__(self, root):
    self.root=root
    nb = ttk.Notebook(root)

    # tuple of tuples containing our frames and the title of their tabs
    self.frames = (
      (StartPage(), 'Start'), 
      (AccelerationPage(), 'Acceleration'),
      (TempPressPage(), 'Temperature & Pressure'),
      (GPIOPage(), 'GPIO')
    )

    for F in self.frames:
      # iterate through and add all the frames with their titles to the app
      nb.add(F[0], text = F[1])    
    nb.pack()

# class that is a frame in out tk gui application
class StartPage(tk.Frame):
  def __init__(self, *args, **kw):
    # call the init of the  parent class
    tk.Frame.__init__(self, *args, **kw)
    # make a simple label
    label = ttk.Label(self, text = "This is the Start Page", font = LARGE_FONT)
    # add padding on the left and y axis
    label.pack(pady = 10, padx = 10)

class AccelerationPage(tk.Frame):
  def __init__(self, *args, **kw):
    # data read from buffer
    self.accel = []
    self.time = []
    # call the init of the parent class
    super().__init__(*args, **kw)
    label = tk.Label(self, text = "Magnitude of Acceleration / Time Unit", font = LARGE_FONT)
    label.pack(pady = 10,padx = 10)
    self.master.bind("<<Update>>", self.update)
    # canvas setup
    canvas = FigureCanvasTkAgg(accelerationFig, self)
    canvas.show()
    canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
    # toolbar
    toolbar = NavigationToolbar2TkAgg(canvas,self)
    toolbar.update()
    canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)   
    
    self.startTime = time.time()

  def update(self, event):
    print("Updating")
    data = buffer["berryImuData"].split(",")
    accelMagnitude = math.sqrt(int(data[0])**2 + int(data[1])**2 + int(data[2])**2)
    self.accel.append(accelMagnitude)
    self.time.append(time.time())
    timeLimit = 10
    indexAtTime = None
    for i in range(len(self.time)-1, 0, -1):
      if time.time() - self.time[i] > timeLimit:
        indexAtTime = i
        break
    self.accel = self.accel[indexAtTime:]
    self.time  = self.time[indexAtTime:]
  
  def animateAcceleration(self, i):
    # this function animates the data being pulled from the file
    accelerationPlot.clear()
    accelerationPlot.plot(list(map(lambda t: t-self.startTime, self.time)), self.accel)

class TempPressPage(tk.Frame):
  def __init__(self, *args, **kw):
    # data read from buffer
    self.temp = []
    self.press = []
    self.time = []
    # call the init of the parent class
    tk.Frame.__init__(self, *args, **kw)
    label = tk.Label(self, text = "Temperature and Pressure / Time Unit", font = LARGE_FONT)
    label.pack(pady = 10, padx = 10)

    #self.bind("<<event>>", self.update)
    # canvas setup 
    canvas = FigureCanvasTkAgg(tempPressFig, self)
    canvas.show()
    canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
    # toolbar
    toolbar = NavigationToolbar2TkAgg(canvas,self)
    toolbar.update()
    canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
  
  def update():
    data = buffer["berryImuData"].split(",")
    tempData = int(data[9])
    pressData = int(data[10])
    self.temp.append(tempData)
    self.press.append(pressData)
    self.time.append(time.time())

class GPIOPage(tk.Frame):
  def __init__(self, *args, **kw):
    # data read from buffer
    self.gpio = []
    # tk setup
    tk.Frame.__init__(self, *args, **kw)
    canvas = tk.Canvas(self)
    self.canvas = canvas
    # starting position of the circles
    x0, y0, x1, y1 = 50, 50, 50, 50
    # the change in position for each circle
    dx, dy = 30, 30
    # test boolean to change color
    b = True
    self.b = b
    # array of circle item references
    circles = []
    for i in range(1, 41):
      # draw the circle and save the reference
      circles.append(canvas.create_oval(x0, y0, x1, y1, outline = "#0f0", fill = "#0f0", width = 20))
      # draw the text corresponding to the gpio pin
      canvas.create_text(x0, y0, text = str(i), anchor = tk.NW)
      # incrememt y position
      y0 += dy
      y1 += dy
      # if it is the 20th gpio move the x position over by double dx
      if (i % 20 == 0):
        x0 += 2*dx
        x1 += 2*dx
        y0, y1 = 50, 50
      # if it is the any 10 gpio position move it over by dx
      elif (i % 10 == 0):
        x0 += dx
        x1 += dx
        y0, y1 = 50, 50
    canvas.pack(fill = tk.BOTH, expand = 1)
  # function to test changing the circle color based on a boolean
  def click(self, canvas, i):
    self.b = not self.b
    if self.b:
      canvas.after(10, lambda: canvas.itemconfig(i, outline = "#0f0", fill = "#0f0"))
    else:
      canvas.after(10, lambda: canvas.itemconfig(i, outline = "#f00", fill = "#f00"))
    
  def update():
    pass

# class for the map page
class MapPage(tk.Frame):
  def __init__(self, *args, **kw):
    tk.Frame.__init__(self, *args, **kw)
  
def readBuffer():
  # read one byte at a time until we read newline character
  # then log the message that was received.
  stringBuffer = ""
  charFromStream = ""
  berryImuData = ""
  gpsData = ""
  gpioData = ""
  while charFromStream != '\n':
    charFromStream = ser.read(1).decode("utf-8")
    if charFromStream == -1:
      break
    if charFromStream != '\n':
      stringBuffer += charFromStream

  logger.debug("Message: %s", stringBuffer)
  # split up the data from the string into their respective parts
  berryImuData, gpsData, gpioData = stringBuffer.split("|")
  buffer["berryImuData"] = berryImuData
  buffer["gpsData"] = gpsData
  buffer["gpioData"] = gpioData
  readBuffer.root.after(10, readBuffer)

def pretendToReadBuffer(i = 0):
  listOfPoints = [(1,52, 77), (2,33, 12), (3, 5, 89), (4, 50, 1), (5, 25, 2), (6, 66, 4)]
  if i >= 30:#or len(listOfPoints):
    i = 0
  buffer["berryImuData"] = ",".join(map(str, (i**2, i**2, i**2)))
  pretendToReadBuffer.root.after(100, pretendToReadBuffer, i+1)
  pretendToReadBuffer.root.event_generate("<<Update>>", when="tail")
    

if __name__ == '__main__':
  root = tk.Tk()
  root.option_add('*font', ('verdana', 9, 'normal'))
  root.title("Rocket Data Visualization")
  display = RocketGUI(root)
  # set up the animation function for acceleration
  accelerationAnimation = animation.FuncAnimation(accelerationFig, display.frames[1][0].animateAcceleration, interval = 500)
  logger.info("Initializing serial connection and antenna...")
  try:
    ser = serial.Serial("dev/ttyUSB0") #TODO: Add baudrate
    readBuffer.root = root
    root.after(10, readBuffer)
  except NameError:
    logger.info("Not connected to Pi: Not starting serial")
    pretendToReadBuffer.root = root
    pretendToReadBuffer()
  root.mainloop()
