from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
import subprocess
import os

load_dotenv()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

class NeuralHTTP(BaseHTTPRequestHandler):
    def do_GET(self):
        print("\nRequest came for:", self.path, "\n")
        if self.path == '/run-script':
            # Execute the cronJob.sh script when the URL is /run-script
            subprocess.Popen(["bash", "cronJob.sh"])
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Cron Job Script Executed</h1></body></html>")
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
