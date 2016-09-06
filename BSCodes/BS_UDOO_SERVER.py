import serial,time,re

import platform

if platform.system()=="Windows":
	UdooPortName = "COM10"
elif platform.system()=="Linux":
	UdooPortName = "/dev/ttymxc3"
else:
	print "Unsupported platform"


baud = 9600

PacketStore = "PS.txt"
ImageFile = "abc.jpg"

Udoo = serial.Serial()
Udoo.port = UdooPortName
Udoo.baudrate = baud
Udoo.timeout=5
Udoo.open()
print "Udoo operating on",Udoo.name

# commands must be of the format BS+xxxxxxx with 7 'x'es as characters (can't be numbers)

COMMANDS = ["BS+PULLIMG",
			"BS+STOREPT"]




def PULLIMG():
	try:
		import GP
		imgName = GP.Capture()
		imgName = imgName.strip()
		f = open(imgName,'rb')
		imgData = f.read()
		
		cmd = "BS+PUSHIMG=" + str(f.tell()) + "\r\n" #f.tell() gives the current position of file pointer and as have 
													 # read all the bytes using .read() it give the size of the file.

		print "Sending CMD:",cmd

		f.close()

		time.sleep(0.5) #wait for a little time to let the basestation ready to receive the command BS+PUSH

		Udoo.write(cmd)

		print "Image Load Complete....Pushing Image in 1s."
		time.sleep(1) # wait for a little time to let the basestation be ready to receive the Image

		Udoo.write(imgData)
		
		print "IMAGE sent."
	
	except Exception as e:
		print "Unexpected error:",e


def STOREPT(param):
	try:
		print "Waiting for PACKET....."
		f = open(PacketStore,'a')
		estimated_timeout = (param / (baud/10)) * 2 # in 1s we receive 960 bytes at 9600 baud , so we set a timeout double the time required as a safety
		Udoo.timeout = estimated_timeout
		packet = Udoo.readline()
		f.write(packet)
		f.close()
		print "PACKET  received successfully."
	
	except Exception as e:
		print "Unexpected error:",e



def serve():
	while True:
		try:
			time.sleep(0.5)
			Udoo.timeout = None
			Udoo.flushInput()

			print "Waiting for REMOTE Command...."

			line = Udoo.readline()
			line = line.strip() #remove \r\n

			print "Rcvd REMOTE command >",line

			#line = "BS+STOREPT=99"
			#line = "BS+PASSIMG"

			cmd_format = "BS\+(\w+)=?(\d*)"

			cmdSearch = re.search(cmd_format,line)

			if cmdSearch == None:
				print "Command Format Error. Rcvd Cmd >",line
				continue


			fun = cmdSearch.group(1)		# extract ABCDEFG from BS+ABCDEF=100
			param = cmdSearch.group(2)		# extract 100 from BS+ABCDEFG=100

			print "function:",fun,"parameter:",param

			if "BS+"+fun in COMMANDS:
				print fun+"("+param+")"
				eval(fun+"("+param+")")

		except Exception as e:
			print "Unexpected error:",e
			print "Closing Udoo Serial port..."
			Udoo.close()



if __name__ == "__main__":
	serve()


