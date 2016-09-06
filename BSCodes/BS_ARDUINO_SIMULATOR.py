import serial,re,time

port = "COM22"
baud = 9600

import sys

if len(sys.argv)>1:
    port = sys.argv[1]

Arduino = serial.Serial(port,baud,timeout=100)



def rcvImage(ImageFile="rcv.jpg"):
	try:
		Arduino.write("BS+PULLIMG\r\n")
		
		while True:
			rcvCmd = Arduino.readline()
			rcvCmd = rcvCmd.strip() #remove CR LF

			rcvCmdFormat = "BS\+PUSHIMG=(\d+)"

			rcvCmdValidity = re.search(rcvCmdFormat,rcvCmd)

			if rcvCmdValidity==None:
				print "Invalid command from Satellite."
				print "Expected format BS+PUSHIMG=(\d+) , but got:",rcvCmd
				break;

				#return False
			else:
				break

		length2read = rcvCmdValidity.group(1)

		if not length2read.isdigit():
			print "Excepted length2read to be a number."
			print "length2read received:",length2read
			return False

		length2read = int(length2read) # convert to interger

		print "Waiting for image from SATELLITE. Ready to write to",ImageFile
		print "Size (in bytes) of Image:",length2read


		buffersize = 2048 # note this must be less than 4096

		Arduino.timeout = (buffersize / (baud/10)) * 2

		f = open(ImageFile,'wb')

		no_of_bytes_written = 0

		for i in xrange(int(length2read/buffersize)):
			imgData = Arduino.read(buffersize)
			f.write(imgData)
			no_of_bytes_written += buffersize
			print "Received bytes = ",no_of_bytes_written


		# for the remainder of bytes
		imgData = Arduino.read(length2read%buffersize)
		f.write(imgData)

		no_of_bytes_written += length2read%buffersize
		print "Received bytes = ",no_of_bytes_written
		

		#f.close()

		print "Image received successfully."
		return True


	except Exception as e:
		print "Unexpected error:",e
		return False
	finally:
                f.close()
		print "Please wait... Returning to data capture mode..."
		time.sleep(10)
		#Arduino.flushInput()
                #Arduino.flushOutput()
                Arduino.read(1000)



def sendPacket(packet="HELLO WORLD"): # CAUTION : packet cannot contain a line feed LF ('\n')
	
	try:
		cmd = "BS+STOREPT=" + str(len(packet)) + "\r\n"

		print "Sending command :",cmd

		Arduino.write(cmd)

		Arduino.write(packet + "\r\n")

		print "Packet sent successfully."

	except Exception as e:
		print "Unexpected error :",e




if __name__ == "__main__":
	
	#sendPacket()
	import socket
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	server = ('localhost',9999)

	s.sendto("hello",server)
	data,server = s.recvfrom(10)
	if data=="ack":
		print "Server connected....."
	else:
		print "Server not found....."
		exit()

	while True:
		try:
			SATdata =  Arduino.readline()
			print SATdata
			s.sendto(SATdata,server)
			
		except KeyboardInterrupt:
			rcvImage()













