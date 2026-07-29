"""
WebSocket Server Localhost Test.

Purpose:
    Verifies that the Python WebSocket server starts correctly,
    accepts a client connection, and delivers JSON messages.

    This test simulates the ESP32 by connecting a Python websocket
    client to the server on localhost. No hardware required.

How to run:
    python tests/test_websocket.py
"""

import sys
import asyncio
import json
import threading
import time
from pathlib import Path

# Add project root to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from communication.websocket_server import WebSocketServer


def run_test() -> None:
    """
    Test sequence:
    1. Start the WebSocket server on localhost.
    2. Connect a fake ESP32 client.
    3. Send a speech message from server to client.
    4. Verify the client received a valid JSON speech message.
    5. Send an acknowledgment back from client to server.
    6. Disconnect cleanly.
    """
    print("=" * 50)
    print("  WebSocket Server - Localhost Test")
    print("=" * 50)

    # ── Step 1: Start the server ──
    print("\n[TEST] Starting WebSocket server...")
    server = WebSocketServer()
    server.start()
    time.sleep(1.0)  # Give the server a moment to bind the port

    # ── Step 2: Connect a simulated ESP32 client ──
    received_messages = []
    client_connected = threading.Event()
    client_done = threading.Event()

    async def fake_esp32_client():
        """Simulates the ESP32 WebSocket client."""
        import websockets

        uri = f"ws://127.0.0.1:{server.port}"
        print(f"[TEST CLIENT] Connecting to {uri}...")

        try:
            async with websockets.connect(uri) as ws:
                print("[TEST CLIENT] Connected to server!")
                client_connected.set()

                # Wait for messages from the server
                try:
                    async for raw_msg in ws:
                        data = json.loads(raw_msg)
                        received_messages.append(data)
                        print(f"[TEST CLIENT] Received: {data}")

                        # Send an ACK back (like the real ESP32 will)
                        ack = json.dumps({
                            "type": "ack",
                            "id": data.get("id", 0)
                        })
                        await ws.send(ack)

                        # After receiving the message, signal we are done
                        client_done.set()
                except websockets.exceptions.ConnectionClosed:
                    pass
        except Exception as e:
            print(f"[TEST CLIENT] Connection failed: {e}")
            client_done.set()

    # Run the fake client in a background thread
    def run_client():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(fake_esp32_client())

    client_thread = threading.Thread(target=run_client, daemon=True)
    client_thread.start()

    # Wait for client to connect
    if not client_connected.wait(timeout=5.0):
        print("[FAIL] Test client could not connect to server.")
        server.stop()
        sys.exit(1)

    # Give server a moment to register the connection
    time.sleep(0.5)

    # ── Step 3: Verify server sees the client ──
    print(f"\n[TEST] Server reports is_connected = {server.is_connected}")
    if not server.is_connected:
        print("[FAIL] Server did not detect client connection.")
        server.stop()
        sys.exit(1)

    # ── Step 4: Send a speech message ──
    test_text = "Welcome to JECRC University"
    print(f"[TEST] Sending speech: '{test_text}'")
    success = server.send_speech(test_text)

    if not success:
        print("[FAIL] send_speech() returned False.")
        server.stop()
        sys.exit(1)

    # ── Step 5: Wait for client to receive and ACK ──
    if not client_done.wait(timeout=5.0):
        print("[FAIL] Client did not receive the message within 5 seconds.")
        server.stop()
        sys.exit(1)

    # ── Step 6: Validate the received message ──
    print("\n[TEST] Validating received message...")
    assert len(received_messages) == 1, f"Expected 1 message, got {len(received_messages)}"

    msg = received_messages[0]
    assert msg["type"] == "speech", f"Expected type 'speech', got '{msg['type']}'"
    assert msg["text"] == test_text, f"Expected text '{test_text}', got '{msg['text']}'"
    assert "id" in msg, "Message missing 'id' field"
    assert isinstance(msg["id"], int), f"Expected int id, got {type(msg['id'])}"

    print(f"  ✓ type  = '{msg['type']}'")
    print(f"  ✓ id    = {msg['id']}")
    print(f"  ✓ text  = '{msg['text']}'")

    # ── Step 7: Clean shutdown ──
    server.stop()

    print("\n" + "=" * 50)
    print("          ALL TESTS PASSED ✓")
    print("=" * 50)
    print("\nThe WebSocket server is working correctly on localhost.")
    print("Ready for Step 3: Connect the real ESP32.\n")


if __name__ == "__main__":
    run_test()
