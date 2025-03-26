from flask import Flask, jsonify, request
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)
DATA_FILE = "counter.json" # 指定用來儲存資料的 JSON 檔

def read_counter():
    if not os.path.exists(DATA_FILE): # 如果檔案不存在，建立預設資料
        return {"total": 0, "ips": {}, "logs": []}
    with open(DATA_FILE, "r") as f: # 否則讀取 counter.json 並轉成 Python 字典
        return json.load(f)

def write_counter(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2) # 將更新後的資料寫回 counter.json

# API
@app.route("/api/visit", methods=["GET"])
def count_visit():
    data = read_counter()

    # 取得訪問者 IP，累加總計與 IP 計數
    ip = request.remote_addr # 拿到訪問者的 IP
    data["total"] += 1 
    data["ips"][ip] = data["ips"].get(ip, 0) + 1 # 如果這個 IP 第一次訪問，初始化為 0，並加總這個 IP 的訪問次數

    # 取得台灣時間，記錄 log
    taiwan_time = datetime.now(ZoneInfo("Asia/Taipei")) # 台灣時區
    log = {
        "timestamp": taiwan_time.isoformat(),
        "ip": ip,
        "referrer": request.referrer or "direct" # 從哪個網址過來的（沒有就寫 "direct"）
    }
    data["logs"].append(log) # 把這次訪問紀錄存到 logs 裡。

    write_counter(data)

    # 回傳 JSON 給前端
    return jsonify({ 
        "total": data["total"],
        "your_ip": ip,
        "your_visits": data["ips"][ip]
    })

# 首頁
@app.route("/")
def home():
    return "Welcome to VisitLog API! Try /api/visit"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
