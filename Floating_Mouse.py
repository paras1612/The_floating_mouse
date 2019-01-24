import matplotlib.pyplot as plt
import win32gui
import serial
import pyquaternion.quaternion as pyqt
import time
import numpy as np
from pynput.mouse import Button, Controller
from win32api import GetSystemMetrics

buffer_state_left=[]
buffer_state_right=[]
a_state=[]
b_state=[]
c_state=[]





class DynamicUpdate():
	#Suppose we know the x range
	min_x = 0
	max_x = 1535
	plt.ion()
	def on_launch(self):
		#Set up plot
		self.figure, self.ax = plt.subplots()
		self.lines, = self.ax.plot([],[], '-', color="red")
		self.line2, = self.ax.plot([],[], '-', color= "blue")
		self.line3, = self.ax.plot([],[], '-', color= "green")
		#Autoscale on unknown axis and known lims on the other
		self.ax.set_autoscaley_on(True)
		#self.ax.set_autoscalex_on(True)
		self.ax.set_xlim(self.min_x, self.max_x)
		#Other stuff
		self.ax.grid()
		...

	def on_running(self, xdata, ydata,y2data,y3data):
		#Update data (with the new _and_ the old points)
		if len(xdata) > 10:
			xdata.pop(0)
			y1data.pop(0)
			y2data.pop(0)
			y3data.pop(0)
		self.lines.set_xdata(xdata)
		self.lines.set_ydata(ydata)
		self.line2.set_xdata(xdata)
		self.line2.set_ydata(y2data)
		self.line3.set_xdata(xdata)
		self.line3.set_ydata(y3data)
		if(xdata[-1] > self.max_x):
			self.ax.set_xlim(self.min_x+0.1, self.max_x+0.1)
			self.min_x = self.min_x +0.1
			self.max_x = self.max_x +0.1
		#Need both of these in order to rescale
		self.ax.relim()
		self.ax.autoscale_view()
		#We need to draw *and* flush
		self.figure.canvas.draw()
		self.figure.canvas.flush_events()

	#Example
	def __call__(self,xdata, ydata):
		import numpy as np
		import time
		
		#y2data=[]
		#y3data=[]
		#x = 0
		self.on_running(xdata, ydata)#,y2data,y3data)
		

#MOUSE////////////////////////////////////////////////////////////////////////////////
xwidth=GetSystemMetrics(0)
ywidth=GetSystemMetrics(1)
mouse= Controller()
flag=0
mouse_sensitivity=1
x_res=xwidth/2
y_res=ywidth/2
def click(state):
	print(state, buffer_state_left, buffer_state_right)
	time.sleep(0)
	if(state[0]=="N" and state[1]=="N" and "Y" in buffer_state_left and "Y" in buffer_state_right):
		print("Entered")
		mouse.click(Button.right)
		flag=1	
		#time.sleep(1)

	if(state[0]=="N" and state[1]=="N" and "Y" in buffer_state_left and (not "Y" in buffer_state_right)):
		mouse.click(Button.left)
		flag=1
def move(a,b,c):
	curx = 0.5*(1.3*a+b -0.3)
	cury = 0.5*(a+1.3*c -0.3)
	curx *=x_res
	cury *=y_res
	if(curx>xwidth):
		curx=xwidth
	if(cury>ywidth):
		cury=ywidth
	if(curx<0):
		curx=0
	if(cury<0):
		cury=0
	print("MOVING")
	mouse.move(curx/100 -5,-(cury/80 -5))




#d = DynamicUpdate()
#d.on_launch()
ser = serial.Serial('com7', 115200)
ser.write(b"s")
count = 0
calibrated = False
validData = False
xdata =[]
y1data= []
y2data= []
y3data= []
cycle = 0
calib_mouse=0
while True:
	string=str(ser.readline())
	if(string.find("Send")!=-1):
		ser.write(b's')
	string=str(string[2:-5]).split("\\t")
	#print(string, count)

	if(len(string)==7):
		if(validData):
			if not calibrated:
				tempq = pyqt.Quaternion(list(map(float,string[1:5])))
				reqq = [0,1,1,1]
				newq = tempq.inverse*reqq*tempq
				finalList = []
				finalList.append(float(str(newq).split(" ")[0]))
				finalList.append(float(str(newq).split(" ")[1][:-1]))
				finalList.append(float(str(newq).split(" ")[2][:-1]))
				finalList.append(float(str(newq).split(" ")[3][:-1]))
				calibrated = True
			else:


				calib_mouse=1
				flag1=False
				try:
					q1=pyqt.Quaternion(list(map(float,string[1:5])))
				except:
					print("INV INPUT")
					flag1 = True
				if(flag1):
					continue
				q2=q1.inverse
				q3=pyqt.Quaternion(finalList)
				q4=q1*q3*q2

				first_val=float(str(q4).split(" ")[1][:-1])
				sec_val=float(str(q4).split(" ")[2][:-1])
				third_val=float(str(q4).split(" ")[3][:-1])
				if(flag==1):
					buffer_state_left=[]
					buffer_state_right=[]
				buffer_state_left.append(string[5])
				buffer_state_right.append(string[6])
				if(len(buffer_state_left)>10 or len(buffer_state_right)>10):
					#buffer_state_left.append(string[5])
					buffer_state_left.pop(0)
					#buffer_state_right.append(string[6])
					buffer_state_right.pop(0)
				click(string[5:7])
				move(first_val, sec_val, third_val)
				print(first_val, sec_val, third_val, string[5:7], count)
				xpos,ypos = win32gui.GetCursorPos()
				xdata.append(xpos)
				y1data.append(first_val)
				y2data.append(sec_val)
				y3data.append(third_val)
				if cycle == 4:
					#d.on_running(xdata,y1data,y2data,y3data)
					cycle = 0
				else:
					cycle +=1
		else:
			count += 1
			print(count)

			if count>500:
				validData = True
		





