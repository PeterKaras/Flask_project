from myblog.app import flask_app
from myblog.app import init_db

import sys

def start():
    debug = True
    host = "0.0.0.0"
    flask_app.run(host,debug=debug)

def init():
    init_db(flask_app)
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        commad = sys.argv[1]
        if commad == "start":
            start()
        elif commad == "init":
            init()
    else:
        print("usage:\n\n\trun.py [ start | init]")
"""
GET is used to request data from a specified resource.
GET is one of the most common HTTP methods.

POST is used to send data to a server to create/update a resource.
"""

