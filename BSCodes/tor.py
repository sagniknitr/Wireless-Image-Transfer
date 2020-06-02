import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
'''
This is a simple Websocket Echo server that uses the Tornado websocket handler.
Please run `pip install tornado` with python of version 2.7.9 or greater to install tornado.
This program will echo back the reverse of whatever it recieves.
Messages are output to the terminal for debuggin purposes. 
''' 
 
class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
      
    def on_message(self, message):
        print 'message received:  %s' % message
        # Reverse Message and send it back
        #print 'sending back message: %s' % message[::-1]
        #self.write_message(message[::-1])
        import socket
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        serverAddress = ("localhost",9999)
        s.bind(serverAddress)

        while True:
            data,client = s.recvfrom(5)
            if data=="hello":
                s.sendto("ack",client)
                print "Tornado connected to BSAT script...."
                while True:
                    data,client = s.recvfrom(100)
                    print "BSAT data ===>",data
                    self.write_message(data)

 
    def on_close(self):
        print 'connection closed'
 
    def check_origin(self, origin):
        return True
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print '*** Websocket Server Started at %s ***' % myIP
    tornado.ioloop.IOLoop.instance().start()