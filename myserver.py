from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is Running!"

def run():
    port = int(os.environ.get("PORT", 10000))  # Render ใช้ PORT นี้เป็นค่าเริ่มต้น
    app.run(host='0.0.0.0', port=port)

def server_on():
    t = Thread(target=run, daemon=True)  # ใช้ daemon เพื่อให้ปิดโปรแกรมได้ง่ายขึ้น
    t.start()
