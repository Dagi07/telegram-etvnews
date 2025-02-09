from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
# from flask import Flask, request, jsonify
# from main import main
import subprocess
import os

load_dotenv()

# Access the variables

# app = Flask(__name__)

# @app.route("/")
# def getRequest():
#     print("requet came")
#     return 200

# if __name__ == "__main__":
#     app.run(debug=True)

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
class NeuralHTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        print("\n request came \n")
        subprocess.Popen(["python3", "main.py"])
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><body><h1>Sending News</h1></body></html>", "utf-8"))

server = HTTPServer((HOST, int(PORT)), NeuralHTTP)
print("\n Server running on ", PORT)
server.serve_forever()
server.server_close()
print("Server now stopped")