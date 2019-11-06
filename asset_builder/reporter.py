import sys
import time
import logging as logger
import socket
import json

response_len = 16
message = '{"test": 32}'

class Reporter(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def report(self, filelist):
        logger.info("Reporting to {}:{}".format(self.host, self.port))
        logger.info(str(filelist))
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            sock.connect((self.host, self.port))
            
            message = {
                "command": "resource.reload",
                "data": filelist
            } 
            
            data = json.dumps(message)
            data += "\n"

            try: 
                sock.sendall(data.encode('utf-8'))
                response = sock.recv(response_len) 
                print("Response: " + response.decode())

            except Exception as e: 
                print("Send Exception: %s" % str(e)) 

            finally: 
                sock.close() 
        except Exception as e: 
            print("Couldn't connect: %s" % str(e)) 
