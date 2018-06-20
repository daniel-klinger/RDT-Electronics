
'''
serial - for sending data to and from external devices like the accelerometer
sys - for information about hardware on this system
math - for math related functions
logging - for clear and pretty output 
'''


"""To DO: Implement all handlers properly"""
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


buffer = {
  "berryImuData": "",
  "gpsData": "",
  "temppressoroni": "",
}

eventFxnList=[]
def doAllEvents(thatEvent):
  for i in eventFxnList:
    i(thatEvent)
    
class Root(tk.Tk):
  BUFFER_INTERVAL = 10 #In ms
  MAX_BUFFER_LENGTH = 100 #entries

  def __init__(self, ser, *arg, **kwargs):
    super().__init__(*arg, **kwargs)
    self.handlers = []
    self.ser = ser
    
    self.nb = ttk.Notebook(self)
    
  def readBuffer(self):
    # read one byte at a time until we read newline character
    # then log the message that was received.
    stringBuffer = ""
    while True:
      lastChar = ser.read(1).decode("utf-8")
      if lastChar != '\n':
        stringBuffer += lastChar
      else:
        break

    logger.info("Message: %s", stringBuffer)
    # split up the data from the string into their respective parts
    dataParts = stringBuffer.split("|")
    #Put each piece of data into their respective buffers
    for i in range(len(dataParts)):
      handler = self.handlers[i]
      handler.update(time.time(), dataParts[i])
      
    #Update the currently displayed window
    handler = self.handlers[self.nb.index(self.nb.select())]
    Handler.setCurrentHandler(handler)
    
    #Then prepare to read the buffer again after interval
    self.after(self.BUFFER_INTERVAL, self.readBuffer)
    
  def registerHandler(self, handler):
    if not isinstance(handler, Handler):
      raise TypeError("new handler must be of type Handler")
    
    self.handlers.append(handler)
    self.nb.add(handler, text=handler.name.title())
    
  def startProcessing(self):
    #Begin the processing loop
    self.after(10, self.readBuffer)
    #Begin main loop
    self.mainloop()
    

#Base class for all data handlers. Each handler is associated with a window.
class Handler(tk.Frame):
  self.programStart = time.time() #Shared by all handlers
  self.currentHandler = None #To tell if a frame should actually be updated

  def __init__(self, root, name):
    super().__init__(root)
    self.name = name
    self.lastUpdated = 0
    self.timeCutoff = 20 #Seconds
    self.dataBuffer = [] #Buffer of things that will be graphed. List of 2-tuple (timestamp, data)
    
  def clampDataBuffer(self):
    cutoffTime = time.time() - self.programStart - self.timeCutoff
    for i in range(len(self.dataBuffer)-1, -1, -1):
      if self.dataBuffer[0] < cutoffTime:
        index = i
        break
    else:
      index = 0
      
    self.dataBuffer = self.dataBuffer[index:]

  def updateFromNew(self, bufferArray):
    self.lastUpdated = time.time()
    self.update(bufferArray)
    self.clampDataBuffer()
    
  def update(self, timestamp, dataString):
    raise NotImplementedError("update should be subclassed")
    
  def animate(self):
    if Handler.currentHandler == self:
      self._animate()
  
  def _animate(self):
    raise NotImplementedError("animate should be subclassed")
    

class TempPressureHandler(Handler):
  def __init__(self, root, name):
    super().__init__(root, name)
    label = tk.Label(self, text = "Temperature and Pressure / Time Unit", font = LARGE_FONT)
    label.pack(pady = 10, padx = 10)
    # Matplotlib setup
    self.figure = Figure(figsize = (5, 4), dpi = 100)
    self.tempPlot = self.figure.add_subplot(211)
    self.pressPlot = self.figure.add_subplot(212)
    # canvas setup
    canvas = FigureCanvasTkAgg(self.figure, self)
    canvas.show()
    canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
    # toolbar
    toolbar = NavigationToolbar2TkAgg(canvas,self)
    toolbar.update()
    canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
    
    
  def update(self, timestamp, dataString):
    #Process each piece of data
    self.dataBuffer.append((timestamp, map(float, dataString.split(","))))
    
  def _animate(self):
    # this function animates the data being pulled from the file
    self.tempPlot.clear()
    self.pressPlot.clear()
    #Turn a list of tuples into two lists
    applyTime = lambda inputList, dataIndex: zip(*map(lambda val: (val[0]-self.programStart, val[1][dataIndex]), inputList))
    self.tempPlot.plot(*applyTime(self.dataBuffer, 0))
    self.pressPlot.plot(*applyTime(self.dataBuffer, 1))
    
class AccelerationHandler(Handler):
  def __init__(self, root, name):
    super().__init__(self, root, name)
    
    # matplotlib setup
    self.figure = Figure(figsize = (5, 4), dpi = 100)
    self.accelPlot = self.figure.add_subplot(111)
    
    label = tk.Label(self, text = "Magnitude of Acceleration / Time Unit", font = LARGE_FONT)
    label.pack(pady = 10,padx = 10)
    eventFxnList.append(self.update)
    # canvas setup
    canvas = FigureCanvasTkAgg(self.figure, self)
    canvas.show()
    canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
    # toolbar
    toolbar = NavigationToolbar2TkAgg(canvas,self)
    toolbar.update()
    canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
    
  def update(self, timestamp, dataString):
    self.dataBuffer.append((timestamp, float(dataString)))
    
  def _animate(self):
    self.accelPlot.clear()
    #Turn a list of tuples into two lists
    applyTime = lambda inputList: zip(*map(lambda val: (val[0]-self.programStart, val[1]), inputList))
    self.accelPlot.plot(*applyTime(self.dataBuffer))
    
class RocketGUI():
  def __init__(self, root):
    self.root=root
    nb = ttk.Notebook(root)
    root.bind("<<Update>>",doAllEvents)
    # tuple of tuples containing our frames and the title of their tabs
    self.frames = (
      (StartPage(), 'Start'), 
      (AccelerationPage(), 'Acceleration'),
      (TempPressPage(), 'Temperature & Pressure'),
      #(GPIOPage(), 'GPIO')
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
    eventFxnList.append(self.update)
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
    eventFxnList.append(self.update)
    # canvas setup 
    canvas = FigureCanvasTkAgg(tempPressFig, self)
    canvas.show()
    canvas.get_tk_widget().pack(side = tk.BOTTOM, fill = tk.BOTH, expand = True)
    # toolbar
    toolbar = NavigationToolbar2TkAgg(canvas,self)
    toolbar.update()
    canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
    
    self.startTime=time.time()
  
  def update(self, event):
    print('HEEEEEE')
    data = buffer["temppressoroni"].split(",")
    tempData = float(data[0])
    pressData = float(data[1])
    self.temp.append(tempData)
    self.press.append(pressData)
    self.time.append(time.time())
    timeLimit2=10
    indexAtTime=None
    for i in range(len(self.time)-1,0,-1):
      if time.time()-self.time[i]>timeLimit2:
        indexAtTime=i
        break
    self.temp=self.temp[indexAtTime:]
    self.press=self.press[indexAtTime:]
    self.time=self.time[indexAtTime:]
  def animateTempandPress(self,i):
    # this function animates the data being pulled from the file
    print('2222222')
    tempPlot.clear()
    pressPlot.clear()
    tempPlot.plot(list(map(lambda t: t-self.startTime, self.time)), self.temp)
    pressPlot.plot(list(map(lambda t: t-self.startTime, self.time)), self.press)
    
        
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

#Tester for when we don't have actual data
class PretendBuffer():
  RECEIVE_INTERVAL = 0.5 #in seconds
  def __init__(self):
    self.buffer = io.BytesIO()
    
  def runThread(self):
    listOfPoints = [(1,52, 77), (2,33, 12), (3, 5, 89), (4, 50, 1), (5, 25, 2), (6, 66, 4)]
    temppressfakenews=[(1,34),(2,32),(3,12),(4,37),(5,45),(6,60),(7,79),(8,89)]
      
    while True:
      time.sleep(self.RECEIVE_INTERVAL)
      berryData = ",".join(map(str, (i**2, i**2, i**2)))
      gpsData = str(temppressfakenews[i%8])[1:-1]
      self.buffer.write(bytes("|".join(berryData, gpsData)))
      
  def read(self, bytes=None):
    while len(self.buffer) == 0:
      time.sleep(0.05)
    self.buffer.seek(0)
    return self.buffer.read(bytes)
      
  
def pretendToReadBuffer(i = 0):
  listOfPoints = [(1,52, 77), (2,33, 12), (3, 5, 89), (4, 50, 1), (5, 25, 2), (6, 66, 4)]
  temppressfakenews=[(1,34),(2,32),(3,12),(4,37),(5,45),(6,60),(7,79),(8,89)]
  if i >= 30:#or len(listOfPoints):
    i = 0
  buffer["berryImuData"] = ",".join(map(str, (i**2, i**2, i**2)))
  buffer["temppressoroni"]=str(temppressfakenews[i%8])[1:-1]
  pretendToReadBuffer.root.after(100, pretendToReadBuffer, i+1)
  pretendToReadBuffer.root.event_generate("<<Update>>", when="tail")
    

if __name__ == '__main__':
  root = Root()
  root.option_add('*font', ('verdana', 9, 'normal'))
  root.title("Rocket Data Visualization")
  root.registerHandler(TempPressureHandler(root, "temp and pressure"))
  root.registerHandler(AccelerationHandler(root, "acceleration"))
  

  root = tk.Tk()
  root.option_add('*font', ('verdana', 9, 'normal'))
  root.title("Rocket Data Visualization")
  display = RocketGUI(root)
  # set up the animation function for acceleration
  accelerationAnimation = animation.FuncAnimation(accelerationFig, display.frames[1][0].animateAcceleration, interval = 500)
  tempAnimation=animation.FuncAnimation(tempPressFig,display.frames[2][0].animateTempandPress, interval=500)
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
