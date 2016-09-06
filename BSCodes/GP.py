import urllib2,re
from BeautifulSoup import BeautifulSoup as soup

password="hello123"
ip = "http://10.5.5.9"



def GPcmd(cmd):
	cmds={
	"turnOn":ip+"/bacpac/PW?t="+password+"&p=%01",
	"turnOff":ip+"/bacpac/PW?t="+password+"&p=%00",
	"setModeImg":ip+"/camera/CM?t="+password+"&p=%01",
	"getImg":ip+"/bacpac/SH?t="+password+"&p=%01"
	}
	urllib2.urlopen(cmds[cmd])


def GPLastImg(rename=""):
	url = "http://10.5.5.9:8080/DCIM/100GOPRO/"
	page = urllib2.urlopen(url).read()
	html = soup(page)
	jpegs = []
	for href in html.findAll("a",{"class":"link"}):
		x = re.search('.*href="(.+\.JPG)".*',str(href))
		if x:jpegs.append(x.group(1))
	
	lastImg = jpegs[-1]
	imgUrl = url+"/"+lastImg

	import PIL
	from PIL import Image
	import urllib2 as urllib
	import io

	image_file = io.BytesIO(urllib2.urlopen(imgUrl).read())
	img = Image.open(image_file)

	img = img.resize((400,300), PIL.Image.ANTIALIAS)
	img.save(lastImg)
	return lastImg
	

def Capture():
	import time
	GPcmd("setModeImg")
	time.sleep(1)
	GPcmd("getImg")
	time.sleep(3)
	img_name = GPLastImg()
	return img_name

if __name__ == '__main__':
	print Capture()