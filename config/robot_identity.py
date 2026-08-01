import socket
import sys
from typing import Dict, Any

class RobotIdentityManager:
    """
    Manages the Robot's Identity Layer (Name, Hostname, Network Mode, and URL configurations).
    Handles the registration of the Multicast DNS (mDNS) responder to broadcast 
    the `<hostname>.local` domain name on the Wi-Fi network.
    """
    def __init__(self) -> None:
        # 1. Permanent Identity Configuration
        self.robot_name: str = "Campus Guide Robot"
        self.hostname: str = "campusguiderobot"
        self.port: int = 8000
        self.ws_port: int = 8765
        
        # 2. Network Mode Selection:
        # "development" (Laptop backend), "local_hotspot" (ESP32 AP), "production" (Onboard computer)
        self.network_mode: str = "development"
        
        # 3. Dynamic IP Discovery
        self.local_ip: str = self._discover_local_ip()
        
        # 4. Permanent Identity URLs (independent of changing dynamic IPs)
        self.permanent_url: str = f"http://{self.hostname}.local:{self.port}"
        self.permanent_ws_url: str = f"ws://{self.hostname}.local:{self.ws_port}"
        
        # 5. Developer Debug/Fallback URLs
        self.fallback_url: str = f"http://{self.local_ip}:{self.port}"
        self.fallback_ws_url: str = f"ws://{self.local_ip}:{self.ws_port}"

        # 6. mDNS Responder references
        self._zeroconf = None
        self._service_info = None

    def _discover_local_ip(self) -> str:
        """
        Discovers the active network interface IP address of the laptop/onboard computer.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Dummy socket connection to establish network interface mapping
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def start_mdns_responder(self) -> None:
        """
        Registers the `<hostname>.local` domain on the local Wi-Fi multicast group.
        Allows any local phone/browser client to resolve the robot without needing IP updates.
        """
        try:
            from zeroconf import Zeroconf, ServiceInfo
            
            print(f"[IDENTITY] Initializing mDNS responder for '{self.hostname}.local'...")
            
            # Service description properties
            properties: Dict[str, str] = {
                "version": "1.0.0",
                "robot_name": self.robot_name,
                "network_mode": self.network_mode
            }
            
            # Register the HTTP server service
            self._service_info = ServiceInfo(
                type_="_http._tcp.local.",
                name=f"{self.hostname}._http._tcp.local.",
                addresses=[socket.inet_aton(self.local_ip)],
                port=self.port,
                properties=properties,
                server=f"{self.hostname}.local."
            )
            
            self._zeroconf = Zeroconf()
            self._zeroconf.register_service(self._service_info)
            print(f"[IDENTITY SUCCESS] mDNS broadcast active: {self.permanent_url}")
            print(f"[IDENTITY INFO] Fallback debug URL: {self.fallback_url}")
            
        except ImportError:
            print("\n[IDENTITY WARNING] 'zeroconf' package not found in virtual environment.")
            print("Hostname resolution (.local) will be disabled. Please install it:")
            print(">>> pip install zeroconf\n")
            print(f"[IDENTITY INFO] Running in IP Fallback Mode: {self.fallback_url}")
            
        except Exception as e:
            print(f"[IDENTITY ERROR] Failed to register mDNS service: {e}")

    def stop_mdns_responder(self) -> None:
        """
        Unregisters the mDNS service and closes socket descriptors.
        """
        if self._zeroconf:
            print("[IDENTITY] Stopping mDNS responder...")
            try:
                self._zeroconf.unregister_service(self._service_info)
                self._zeroconf.close()
                print("[IDENTITY] mDNS broadcast stopped successfully.")
            except Exception as e:
                print(f"[IDENTITY ERROR] Error shutting down mDNS: {e}")
            finally:
                self._zeroconf = None
                self._service_info = None

# Instantiate a global instance of the Identity Layer
robot_identity = RobotIdentityManager()
