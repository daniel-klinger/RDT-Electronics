
#Library to access functionality of GPS module
#TODO: Implement checksum checking for "NMEA setneces" to ensure data accuracy
import serial

#Instances will try to access a given port
class GPS():
  SENTLEN = 5 #The length of a GPS sentence
  SEPARATOR = b"," #Separator between pieces of a sentence
  TERMINATOR = b"\r" #Terminator for a GPS sentence
  
  
  def __init__(self, port = "/dev/ttyS0", *arg, **kwarg):
    self.gps = serial.Serial(port, *arg, **kwarg)

  #Gets all available GPS sentences. Will keep reading bytes until it encounters
  #repeated sentences
  #PRE:  force should be an integer specifying at least how many sentences
        #there should be
  #POST: Returns a list of available sentences
  def getAvailableSentences(self, force = -1):
      toRet = []
      while True:
          if self.gps.read() == b"$":
              sentence = self.gps.read(self.SENTLEN).decode()
              if sentence in toRet:
                if len(toRet) >= force:
                  return sorted(toRet)
              else:
                toRet.append(sentence)


  #Returns the given sentence as a list of the comma-separated values
  #PRE: sentence should be a valid GPS sentence. If bool(sentence) is false,
  #     then will return the first sentence encountered
  #POST: Return a list of comma-separated values. [0] is always sentence, [-1]
  #      is always checksum
  def getSentence(self, sentence = None):
    if sentence: #Only do this if we have a valid sentence
      if sentence[:2] != "GP":
        sentence = "GP" + sentence
      sentence = sentence.upper().encode() #For dealing with bytes
    while True:
        if self.gps.read() == b"$": #Wait for a new sentence
          #if this is the sentence we are looking for
          foundSentence = self.gps.read(self.SENTLEN)
          if foundSentence == sentence or not sentence:
            toRet = []
            buffer = []
            char = None
            while char != self.TERMINATOR:
                char = self.gps.read()
                if char in (self.SEPARATOR, self.TERMINATOR, b"*"):
                    #Add the string the sentence piece and clear buffer
                    toRet.append((b"".join(buffer)).decode())
                    buffer.clear()
                else:
                    buffer.append(char)
            toRet[0] = foundSentence.decode() #This had been a blank string
            return toRet #After we finish processing proper sentence

  #Reads the GPGGA sentence to determine if it has a fix or not                
  def hasFix(self):
    tab = self.getSentence("GPGGA")
    return tab[6] != "0" #0 is time, 1,2 is lat, 3,4 is long, 5 is fix

  #Reads GPGGA sentence to get position.
  #POST: Returns 2-tuple of lat-long if fix. Otherwise 2-tuple (0,0)
  def getLocation(self):
    loc = self.getSentence("GPGGA")
    #If it has a fix
    if loc[6] == "0":
      return (0,0)
    #This is kind of cumbersome, but it gets the data properly
    loc1 = loc[2].split(".")
    loc2 = loc[4].split(".")
    opp = lambda bool: 1 if bool else -1 #Multiplies by -1 if bool is false
    getNum = lambda loc, bool: opp(bool) * (\
             float(loc[0][:-2]) + float(".".join((loc[0][-2:], loc[1])))/60)
    return (getNum(loc1, loc[3] == "N"), getNum(loc2, loc[5] == "E"))

  ### Testing Methods ###
  
  #This will give the relative frequencies of different sentences in a given
  #time period
  def testFrequencies(self, timeout = 5.0):
    from time import time
    start = time()
    dataDict = {}
    while time()-start < timeout:
      sent = self.getSentence()[0]
      print("Got",sent)
      if not sent in dataDict:
        dataDict[sent] = 1
      else:
        dataDict[sent] += 1
        
    total = sum(dataDict.values())
    print("\nTest Results over {} seconds".format(round(timeout,2)))
    for key in sorted(dataDict):
      val = dataDict[key]
      print("{}: {:3} ({} %)".format(key, val, round(100*val/total, 2)))
  
    
  ### Browswer-Enabled Methods ###
  
  #This method will redirect to the webpage of aprs, which has all the sentences
  #If a sentence is specified, it will go to that part of the page
  @staticmethod
  def getMeaning(sentence = None):
    import webbrowser
    return webbrowser.open("http://aprs.gids.nl/nmea/"+\
                      ("#"+sentence.lower()[-3:] if sentence else ""))
    
  #Opens up google maps to show current location
  def googleLocation(self):
    import webbrowser as web
    return web.open("https://www.google.com/maps/place/{},{}".format(*self.getLocation()))