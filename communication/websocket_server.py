"""
WebSocket Server for Campus Guide Robot.

Purpose:
    Runs a WebSocket server on the laptop. The ESP32 connects to this
    server over Wi-Fi. When the pipeline has a Gemini response to speak,
    it calls send_speech() which transmits a JSON message to the ESP32.

Architecture:
    - The server runs in a background daemon thread with its own asyncio event loop.
    - The pipeline (synchronous) calls send_speech() which safely pushes
      the message into the async loop using run_coroutine_threadsafe().
    - Only one ESP32 client connection is accepted at a time.

Message Format:
    {
        "type": "speech",
        "id": 1,
        "text": "Welcome to JECRC University."
    }

    Future-compatible types: "motor", "gesture", "status", etc.
"""

import asyncio
import json
import threading
import time
from config.settings import settings


class WebSocketServer:
    """
    Manages a persistent WebSocket connection between the laptop and ESP32.
    Runs the async server on a background thread so the synchronous pipeline
    can call send_speech() without blocking.
    """

    def __init__(self) -> None:
        """
        Initializes server configuration from settings.
        Does NOT start the server yet — call start() explicitly.
        """
        self.host = settings.ws_host
        self.port = settings.ws_port

        # Connection state
        self.client = None          # The single connected ESP32 websocket object
        self.is_connected = False   # True when ESP32 is actively connected
        self.message_id = 0         # Auto-incrementing message counter

        # Background thread internals
        self._loop = None           # The asyncio event loop running in the thread
        self._thread = None         # The background daemon thread
        self._server = None         # The websockets server object
        self._ready_event = threading.Event()  # Signals when server is listening

        print(f"[WS SERVER] Initialized for {self.host}:{self.port}")

    def start(self) -> None:
        """
        Launches the WebSocket server on a background daemon thread.

        Why a background thread?
            The main thread runs the synchronous keyboard input loop.
            The WebSocket server needs its own asyncio event loop to
            listen for incoming ESP32 connections concurrently.
            A daemon thread dies automatically when the main program exits.
        """
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

        # Block the caller briefly until the server is actually listening.
        # This prevents the pipeline from trying to send before the server is up.
        if self._ready_event.wait(timeout=5.0):
            print(f"[WS SERVER] Listening on ws://{self.host}:{self.port}")
        else:
            print("[WS SERVER WARNING] Server did not start within 5 seconds.")

    def _run_event_loop(self) -> None:
        """
        Internal: Creates a new asyncio event loop and runs the server forever.
        This method executes entirely inside the background thread.
        """
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._serve())

    async def _serve(self) -> None:
        """
        Internal: Starts the websockets server and blocks forever.
        Uses the modern websockets.serve() async context manager.
        """
        # Import here to keep the module importable even if websockets
        # is not yet installed (gives a clear error at runtime, not import time).
        import websockets

        async with websockets.serve(
            self._handle_client,
            self.host,
            self.port,
            ping_interval=20,     # Server sends ping every 20 seconds
            ping_timeout=10,      # Client must respond within 10 seconds
            close_timeout=5       # Grace period for clean disconnection
        ) as server:
            self._server = server
            self._ready_event.set()  # Signal that the server is now listening
            await asyncio.Future()   # Run forever (until thread is killed)

    async def _handle_client(self, websocket) -> None:
        """
        Handles a single ESP32 WebSocket client connection.

        Only one client is supported at a time. If a new client connects
        while an old one exists, the old one is replaced (the ESP32 may
        have rebooted and reconnected with a fresh socket).

        Args:
            websocket: The connected client's websocket object.
        """
        import websockets

        client_address = websocket.remote_address
        print(f"[WS SERVER] ESP32 connected from {client_address}")

        # Replace any stale previous connection
        if self.client is not None:
            print("[WS SERVER] Replacing previous stale connection.")
            try:
                await self.client.close()
            except Exception:
                pass

        self.client = websocket
        self.is_connected = True

        try:
            # Listen for incoming messages from ESP32 (heartbeats, status, etc.)
            async for raw_message in websocket:
                try:
                    data = json.loads(raw_message)
                    msg_type = data.get("type", "unknown")

                    if msg_type == "heartbeat":
                        # ESP32 sends periodic heartbeats to confirm it is alive
                        pass  # Silently acknowledge (ping/pong handles keepalive)

                    elif msg_type == "status":
                        print(f"[WS SERVER] ESP32 status: {data}")

                    elif msg_type == "ack":
                        # ESP32 confirms it received and began speaking a message
                        print(f"[WS SERVER] ESP32 acknowledged message #{data.get('id', '?')}")

                    else:
                        print(f"[WS SERVER] Unknown message type: {data}")

                except json.JSONDecodeError:
                    print(f"[WS SERVER] Received non-JSON data: {raw_message}")

        except websockets.exceptions.ConnectionClosed as e:
            print(f"[WS SERVER] ESP32 disconnected: {e.reason} (code {e.code})")
        except Exception as e:
            print(f"[WS SERVER] Connection error: {e}")
        finally:
            self.is_connected = False
            self.client = None
            print("[WS SERVER] Waiting for ESP32 to reconnect...")

    def send_message(self, msg_type: str, payload: dict) -> bool:
        """
        Sends a JSON message to the connected ESP32 client.
        This is a synchronous method safe to call from the main thread.

        Args:
            msg_type: The message type string (e.g., "speech", "motor", "gesture").
            payload: A dictionary of additional fields to include in the message.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        if not self.is_connected or self.client is None:
            print("[WS SERVER] Cannot send: No ESP32 connected.")
            return False

        if self._loop is None or self._loop.is_closed():
            print("[WS SERVER] Cannot send: Event loop is not running.")
            return False

        # Build the JSON envelope
        self.message_id += 1
        message = {
            "type": msg_type,
            "id": self.message_id,
            **payload
        }

        json_string = json.dumps(message)

        try:
            # Schedule the async send on the background event loop
            # and wait for it to complete (with a timeout)
            future = asyncio.run_coroutine_threadsafe(
                self.client.send(json_string),
                self._loop
            )
            future.result(timeout=5.0)  # Block up to 5 seconds for delivery
            return True

        except Exception as e:
            print(f"[WS SERVER] Send failed: {e}")
            self.is_connected = False
            self.client = None
            return False

    def send_speech(self, text: str) -> bool:
        """
        Convenience method to send a speech command to the ESP32.
        This is what the pipeline calls after getting a Gemini response.

        Args:
            text: The sanitized text string for the ESP32 to speak.

        Returns:
            True if sent successfully, False otherwise.
        """
        return self.send_message("speech", {"text": text})

    def stop(self) -> None:
        """
        Cleanly shuts down the WebSocket server and background thread.
        """
        print("[WS SERVER] Shutting down...")
        self.is_connected = False

        if self._loop and self._loop.is_running():
            # Schedule client and server resource closure inside the loop thread
            async def shutdown_tasks():
                if self.client:
                    try:
                        await self.client.close()
                    except Exception:
                        pass
                if self._server:
                    self._server.close()
                    await self._server.wait_closed()
                self._loop.stop()

            asyncio.run_coroutine_threadsafe(shutdown_tasks(), self._loop)

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)

        self.client = None
        print("[WS SERVER] Shutdown complete.")
