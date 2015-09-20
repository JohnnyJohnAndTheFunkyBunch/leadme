import tornado.ioloop
import tornado.web
import json
import os
import sys
import main
from tornado.options import define, options


class GetRating(tornado.web.RequestHandler):
    def get(self):
        address = self.get_argument("address")
        output = main.jsonOutput(address)
        self.write(json.dumps(output))

class GetFake(tornado.web.RequestHandler):
    def get(self):
        with open("test.json", 'rb') as f:
          data = f.read()
          self.write(data)

class Main(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html") 
     
application = tornado.web.Application([
    (r"/", Main),
    (r"/discover",GetFake),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "/home/ubuntu/leadme/static"}),
],debug=True)

if __name__ == "__main__":
    print "Listening..."
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
