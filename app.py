import subprocess
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import time
import random

load_dotenv()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

class NeuralHTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        print("\nRequest came for:", self.path, "\n")
        if self.path == '/run-script':
            # Generate random sleep time between 120 and 300 seconds
            sleep_time = random.randint(120, 300)
            
            # Log the sleep time
            with open('logfile.log', 'a') as f:
                f.write(f"Sleeping for {sleep_time} seconds...\n")
            
            # Actually sleep
            time.sleep(sleep_time)
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Slept for {sleep_time} seconds</h1></body></html>".encode())
        else:
            # Default: execute main.py
            subprocess.Popen(["python3", "main.py"])
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Sending News</h1></body></html>")

if __name__ == "__main__":
    server = HTTPServer((HOST, int(PORT)), NeuralHTTP)
    print("\nServer running on", PORT)
    server.serve_forever()
    server.server_close()
    print("Server now stopped")