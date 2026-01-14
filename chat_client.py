
import socket, argparse
import threading
from chat_ui import ChatUI


class ChatClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.sock = None
        self.ui = ChatUI(title=f"Chat Client ({host}:{port})")
        self.ui.set_send_callback(self.send_message)



    def connect(self):
        """Connect to server and start receiving thread"""
        # Create TCP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to (self.host, self.port)
        self.sock.connect((self.host, self.port))

        # Send username (self.ui.username) to server
        self.sock.send(self.ui.username.encode('utf-8'))

        # Start background receiving thread (self.receive_messages)
        recv_thread = threading.Thread(target=self.receive_messages, daemon=True)
        recv_thread.start()



    def send_message(self, event=None):
        """Send message to the server"""
        # Get text from UI (self.ui.get_message())
        msg = self.ui.get_message()

        if not msg:
            return

        # Format: f"{self.ui.username}: {msg}"
        entire_msg = f"{self.ui.username}: {msg}"

        # Send via socket
        try:
            self.sock.send(entire_msg.encode('utf-8'))
        except Exception:
            self.ui.display_message("Fail to send msg.")
            return

        # Also display locally using self.ui.display_message()
        self.ui.display_message(entire_msg)



    def receive_messages(self):
        """Continuously receive messages from the server"""
        # Continuously recv(1024), decode, and show using self.ui.display_message()
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    self.ui.display_message("Server disconnected.")
                    break
                msg = data.decode('utf-8')
                self.ui.display_message(msg)
            except Exception:
                break



    def run(self):
        self.connect()
        self.ui.run()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    ChatClient(host=args.host, port=args.port).run()
