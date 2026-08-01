import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Add project root to python path to resolve config imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.robot_identity import robot_identity

class RobotWebHandler(SimpleHTTPRequestHandler):
    """
    Custom HTTP Request Handler that routes the root path to templates/index.html
    and serves all other static assets (css, js, images) from the project directory.
    """
    def do_GET(self) -> None:
        # Route root requests to templates/index.html
        if self.path == "/" or self.path == "/index.html":
            self.path = "/templates/index.html"
            
        return super().do_GET()

    def log_message(self, format: str, *args) -> None:
        """
        Suppresses verbose access logs in console to keep terminal clean.
        Only logs errors.
        """
        if "HTTP/1.1\" 4" in args[1] or "HTTP/1.1\" 5" in args[1]:
            print(f"[HTTP ERROR] {args[0]} - {args[1]}")

class RobotWebServer:
    """
    Multi-threaded lightweight HTTP Web Server running on a background daemon thread.
    Serves the companion UI pages to mobile clients over local Wi-Fi.
    """
    def __init__(self) -> None:
        self.host: str = "0.0.0.0"  # Bind to all interfaces to allow external phone access
        self.port: int = robot_identity.port
        self.server: ThreadingHTTPServer = None
        self.thread: threading.Thread = None

    def start(self) -> None:
        """
        Launches the HTTP web server asynchronously.
        """
        try:
            # Lock server files context to the project root directory
            project_root = Path(__file__).resolve().parent.parent
            os.chdir(project_root)
            
            self.server = ThreadingHTTPServer((self.host, self.port), RobotWebHandler)
            
            # Run in daemon thread so server exits cleanly when main process is killed
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            print(f"[WEB SERVER] HTTP Server successfully running on: http://{self.host}:{self.port}")
            
        except Exception as e:
            print(f"[WEB SERVER ERROR] Failed to start HTTP server: {e}")

    def stop(self) -> None:
        """
        Shuts down the HTTP server and releases socket resources.
        """
        if self.server:
            print("[WEB SERVER] Shutting down HTTP server...")
            try:
                self.server.shutdown()
                self.server.server_close()
                print("[WEB SERVER] HTTP Server stopped successfully.")
            except Exception as e:
                print(f"[WEB SERVER ERROR] Error stopping server: {e}")
            finally:
                self.server = None
                self.thread = None

if __name__ == "__main__":
    # Local standalone test
    web_server = RobotWebServer()
    web_server.start()
    
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        web_server.stop()
