import serial

class GPS:

	def init(self):
		self.ser = serial.Serial(port= "/dev/serial0", baudrate = 9600, timeout = 0.5)

	def decode(self,coord):
		#Converts DDDMM.MMMMM -&gt; DD deg MM.MMMMM min
		x = coord.split(".")
		head = x[0]
		tail = x[1]
		deg = head[0:-2]
		min = head[-2:]
		return deg + " deg " + min + "." + tail + " min"

	def parseGPS(self,data):
	#    print "raw:", data #prints raw data
		if data[0:6] == b"$GPRMC":
			sdata = data.decode("utf-8").split(",")
			if sdata[2] == 'V':
				#print("no satellite data available")
				return
			#print("---Parsing GPRMC---", end=' ')
			time = sdata[1][0:2] + ":" + sdata[1][2:4] + ":" + sdata[1][4:6]
			lat = self.decode(sdata[3]) #latitude
			dirLat = sdata[4]      #latitude direction N/S
			lon = self.decode(sdata[5]) #longitute
			dirLon = sdata[6]      #longitude direction E/W
			speed = sdata[7]       #Speed in knots
			trCourse = sdata[8]    #True course
			date = sdata[9][0:2] + "/" + sdata[9][2:4] + "/" + sdata[9][4:6]#date
			return {"time":time,"lat":lat,"dirLat":dirLat,"lon":lon,"dirLon":dirLon,"speed":speed,"trCourse":trCourse,"date":date};
			#("time : %s, latitude : %s(%s), longitude : %s(%s), speed : %s, True Course : %s, Date : %s" %  (time,lat,dirLat,lon,dirLon,speed,trCourse,date))

	def getGps(self):
		data = self.ser.readline()
		while (data[0:6] != b"$GPRMC"):
			data = self.ser.readline()
		return self.parseGPS(data)

#x=GPS();
#x.init();
#poop=x.getGps();
#print(poop);


