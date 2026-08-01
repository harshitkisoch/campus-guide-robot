import asyncio
import json
import threading
import time
from typing import Set, Dict, Any, Callable
from config.settings import settings
from config.robot_identity import robot_identity

class WebSocketServer:
    """
    Central WebSocket server routing real-time communication between
    the robot hardware (ESP32) and multiple browser companion web apps (Phones).
    Runs asynchronously on a background daemon thread.
    """
    def __init__(self) -> None:
        self.host: str = settings.ws_host
        self.port: int = settings.ws_port

        # Connection sets
        self.robot_client = None           # Active ESP32 WebSocket connection
        self.phone_clients: Set = set()    # Active Phone browser connections

        # Auto-incrementing message ID counter
        self.message_id: int = 0

        # Background thread properties
        self._loop: asyncio.AbstractEventLoop = None
        self._thread: threading.Thread = None
        self._server = None
        self._ready_event = threading.Event()

        # Query Callback: registered by the core pipeline to handle input queries
        self.on_query_callback: Callable[[str], None] = None

        print(f"[WS SERVER] Initialized central router for port {self.port}")

    @property
    def is_connected(self) -> bool:
        """
        Backward compatibility helper mapping to ESP32 connection state.
        """
        return self.robot_client is not None

    def start(self) -> None:
        """
        Launches the WebSocket server asynchronously on a background thread.
        """
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

        # Wait briefly for the server socket to listen
        if self._ready_event.wait(timeout=5.0):
            print(f"[WS SERVER] Central WebSocket router active on ws://{self.host}:{self.port}")
        else:
            print("[WS SERVER WARNING] WebSocket server startup timeout.")

    def _run_event_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._serve())
        except (asyncio.CancelledError, RuntimeError):
            # Suppress asyncio cancellation/shutdown warnings during exit
            pass

    async def _serve(self) -> None:
        import websockets
        async with websockets.serve(
            self._handle_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=5
        ) as server:
            self._server = server
            self._ready_event.set()
            await asyncio.Future()  # Run forever

    async def _handle_client(self, websocket) -> None:
        import websockets
        
        path = getattr(websocket, 'path', '/')
        is_phone = "phone" in path.lower()
        is_robot = "robot" in path.lower()
        
        client_type = "unknown"
        
        # Categorize by connection path if possible
        if is_phone:
            client_type = "phone"
            self.phone_clients.add(websocket)
            print(f"[WS SERVER] Browser companion connected from {websocket.remote_address}")
            await self._send_status_to_phone(websocket)
        elif is_robot:
            client_type = "robot"
            await self._register_robot(websocket)

        try:
            async for raw_message in websocket:
                try:
                    data = json.loads(raw_message)
                    msg_type = data.get("type", "unknown")
                    
                    # Handle handshake / default fallback categorization
                    if client_type == "unknown":
                        if data.get("client") == "phone" or msg_type == "ping":
                            client_type = "phone"
                            self.phone_clients.add(websocket)
                            print(f"[WS SERVER] Browser registered from {websocket.remote_address}")
                            await self._send_status_to_phone(websocket)
                        else:
                            # Assume robot for root path '/' or ESP32 status packets
                            client_type = "robot"
                            await self._register_robot(websocket)

                    # Route messages based on client type
                    if client_type == "phone":
                        await self._handle_phone_message(websocket, msg_type, data)
                    elif client_type == "robot":
                        await self._handle_robot_message(websocket, msg_type, data)
                        
                except json.JSONDecodeError:
                    print(f"[WS SERVER WARNING] Received non-JSON message: {raw_message}")

        except websockets.exceptions.ConnectionClosed as e:
            print(f"[WS SERVER] Connection closed ({client_type}): {websocket.remote_address}")
        except Exception as e:
            print(f"[WS SERVER ERROR] Connection exception: {e}")
        finally:
            if client_type == "phone":
                self.phone_clients.discard(websocket)
            elif client_type == "robot":
                self.robot_client = None
                print("[WS SERVER] ESP32 disconnected.")
                self.broadcast_to_phones("robot_status", {"connected": False})

    async def _register_robot(self, websocket) -> None:
        """
        Registers the single ESP32 client connection, dropping any stale sockets.
        """
        if self.robot_client is not None and self.robot_client != websocket:
            print("[WS SERVER] Overwriting stale ESP32 socket reference.")
            try:
                await self.robot_client.close()
            except Exception:
                pass
        
        self.robot_client = websocket
        print(f"[WS SERVER] ESP32 successfully registered from {websocket.remote_address}")
        self.broadcast_to_phones("robot_status", {"connected": True})

    async def _handle_phone_message(self, websocket, msg_type: str, data: dict) -> None:
        """
        Processes incoming dashboard events from the browser app.
        """
        if msg_type == "query":
            text = data.get("text", "")
            print(f"[WS SERVER] Phone query request: '{text}'")
            if self.on_query_callback:
                # Execute pipeline query in a separate thread to prevent blocking WebSocket server
                threading.Thread(
                    target=self.on_query_callback,
                    args=(text,),
                    daemon=True
                ).start()
        
        elif msg_type == "ping":
            # Quick loopback for latency visualization
            try:
                await websocket.send(json.dumps({
                    "type": "pong",
                    "timestamp": data.get("timestamp", time.time())
                }))
            except Exception:
                pass

        elif msg_type == "control":
            # Forward motion/head controller commands to the ESP32 robot client
            if self.robot_client:
                try:
                    await self.robot_client.send(json.dumps(data))
                    print(f"[WS SERVER] Forwarded control command to ESP32: {data}")
                except Exception as e:
                    print(f"[WS SERVER ERROR] Failed to forward control to ESP32: {e}")

    async def _handle_robot_message(self, websocket, msg_type: str, data: dict) -> None:
        """
        Processes status reports and heartbeats originating from the ESP32.
        """
        if msg_type == "status":
            print(f"[WS SERVER] ESP32 telemetry packet: {data}")
            # Broadcast the ESP32 telemetry status directly to all browsers
            self.broadcast_to_phones("robot_telemetry", data)
        elif msg_type == "ack":
            print(f"[WS SERVER] ESP32 spoke message #{data.get('id', '?')}")
        elif msg_type == "heartbeat":
            pass

    async def _send_status_to_phone(self, websocket) -> None:
        """
        Sends current robot configuration and state to a new browser client on startup.
        """
        status_payload = {
            "type": "initial_status",
            "robot_name": robot_identity.robot_name,
            "network_mode": robot_identity.network_mode,
            "robot_connected": self.robot_client is not None,
            "gemini_connected": True,
            "websocket_connected": True,
            "speaker_selected": settings.output_device,
            "fallback_ip": robot_identity.local_ip
        }
        try:
            await websocket.send(json.dumps(status_payload))
        except Exception as e:
            print(f"[WS SERVER ERROR] Failed to send status handshake: {e}")

    def broadcast_to_phones(self, msg_type: str, payload: dict) -> None:
        """
        Sends an event update thread-safely to all connected companion apps.
        """
        if not self.phone_clients or self._loop is None or self._loop.is_closed():
            return

        message = {
            "type": msg_type,
            "timestamp": time.time(),
            **payload
        }
        json_string = json.dumps(message)

        # Safely schedule the async broadcast coroutine in the loop thread
        asyncio.run_coroutine_threadsafe(
            self._async_broadcast(json_string),
            self._loop
        )

    async def _async_broadcast(self, json_string: str) -> None:
        if not self.phone_clients:
            return
        # Broadcast concurrently across all browser sockets
        await asyncio.gather(
            *(client.send(json_string) for client in list(self.phone_clients)),
            return_exceptions=True
        )

    def send_message(self, msg_type: str, payload: dict) -> bool:
        """
        Synthesizes a JSON packet and sends it thread-safely to the ESP32.
        """
        if not self.is_connected or self.robot_client is None:
            return False

        if self._loop is None or self._loop.is_closed():
            return False

        self.message_id += 1
        message = {
            "type": msg_type,
            "id": self.message_id,
            **payload
        }
        json_string = json.dumps(message)

        try:
            future = asyncio.run_coroutine_threadsafe(
                self.robot_client.send(json_string),
                self._loop
            )
            future.result(timeout=4.0)
            return True
        except Exception as e:
            print(f"[WS SERVER ERROR] Send to ESP32 failed: {e}")
            self.robot_client = None
            return False

    def send_speech(self, text: str) -> bool:
        """
        Synthesizes a speech command and routes it wirelessly to the ESP32.
        """
        return self.send_message("speech", {"text": text})

    def stop(self) -> None:
        """
        Cleanly closes all sockets and terminates the async execution loop.
        """
        print("[WS SERVER] Shutting down Central router...")
        if self._loop and self._loop.is_running():
            async def shutdown_tasks():
                # Close all browser tabs
                for p_client in list(self.phone_clients):
                    try:
                        await p_client.close()
                    except Exception:
                        pass
                # Close robot connection
                if self.robot_client:
                    try:
                        await self.robot_client.close()
                    except Exception:
                        pass
                # Close server
                if self._server:
                    self._server.close()
                    await self._server.wait_closed()
                self._loop.stop()

            asyncio.run_coroutine_threadsafe(shutdown_tasks(), self._loop)

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)

        self.robot_client = None
        self.phone_clients.clear()
        print("[WS SERVER] Central router shutdown complete.")
