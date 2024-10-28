from http.server import HTTPServer, BaseHTTPRequestHandler
# from flask import Flask, request, jsonify
# from main import main
import subprocess

# app = Flask(__name__)

# @app.route("/")
# def getRequest():
#     print("requet came")
#     return 200

# if __name__ == "__main__":
#     app.run(debug=True)

HOST = "localhost"
PORT = 9999

class NeuralHTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        print("\n request came \n")
        subprocess.Popen(["python3", "main.py"])
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><body><h1>Sending News</h1></body></html>", "utf-8"))

server = HTTPServer((HOST, PORT), NeuralHTTP)
print("\n Server running on ", PORT)
server.serve_forever()
server.server_close()
print("Server now stopped")