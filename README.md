📦 MediaCloud
A simple local network file sharing system built with Flask (server) and Tkinter (client).
It allows users to upload, download, view, import, and manage files across devices on the same network.
✨ Features
📤 Upload files to server
📥 Download / Import files to device storage
👁 View files in browser
🗑 Delete files (owner-only protection system)
🔄 Refresh file list
💾 Auto-save server IP
🔐 Device-based ownership system (UUID-based)
⚙️ Requirements
🖥 Server Requirements
Python 3.x
Flask
Werkzeug
Install dependencies:
pip install flask werkzeug
📱 Client Requirements
Python 3.x
Tkinter (usually built-in with Python)
Requests
Install dependencies:
pip install requests
🚀 How to Run
1. Start the Server
python server.py
The server will run on:
http://0.0.0.0:5000
or your local IP:
http://192.168.x.x:5000
2. Start the Client
python client.py
Then:
Enter the server IP
Example:
http://192.168.1.5:5000
Click Connect
📂 File Storage Locations
Server storage:
/uploads
Client imported files:
/storage/emulated/0/MediaCloud/Files
🔐 Ownership System
Each device gets a unique UUID (Device ID).
Files are linked to the uploader's Device ID
Only the owner can delete their files
Prevents unauthorized deletion
🌐 Network Requirements
All devices must be on the same WiFi network
Server must be running before client connection
Default port: 5000
🧠 Project Purpose
This project demonstrates:
Client-server architecture
REST API usage with Flask
File upload/download handling
Basic ownership security system
GUI development with Tkinter
📌 Notes
This is a local network project (not cloud hosted)
No authentication system (uses Device ID only)
Designed for educational purposes
👨‍💻 Author
A simple educational project for learning backend + client communication using Python.
