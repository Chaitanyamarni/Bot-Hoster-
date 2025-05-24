from flask import Flask, request, redirect, jsonify, send_from_directory
import os, subprocess, threading

app = Flask(__name__)
BOT_DIR = 'bots'
LOG_DIR = 'logs'
running_bots = {}

os.makedirs(BOT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

@app.route('/')
def home():
    bots = [f for f in os.listdir(BOT_DIR) if f.endswith('.py')]
    bots_html = ""
    for bot in bots:
        bots_html += f"""
        <tr>
            <td>{bot}</td>
            <td>
                <button onclick="startBot('{bot}')">Start</button>
                <button onclick="stopBot('{bot}')">Stop</button>
                <button onclick="viewLogs('{bot}')">Logs</button>
                <button onclick="deleteBot('{bot}')" style="background-color:#b02a37;">Delete</button>
                <span id="status-{bot}" style="margin-left:10px;"></span>
            </td>
        </tr>
        """
    return f"""
    <html>
    <head>
        <title>Telegram Bot Panel</title>
        <style>
            body {{
                background-color: #0d1117;
                color: white;
                font-family: Arial, sans-serif;
                padding: 40px;
            }}
            h1 {{
                color: #58a6ff;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 10px;
                border-bottom: 1px solid #333;
            }}
            button {{
                background-color: #238636;
                border: none;
                padding: 6px 12px;
                color: white;
                margin-right: 5px;
                cursor: pointer;
                border-radius: 5px;
            }}
            button:hover {{
                background-color: #2ea043;
            }}
            button[style*="background-color:#b02a37;"]:hover {{
                background-color: #7a121f;
            }}
            input[type=file] {{
                margin-top: 10px;
                color: white;
            }}
            #logBox {{
                margin-top: 20px;
                background-color: #161b22;
                padding: 15px;
                border-radius: 5px;
                white-space: pre-wrap;
                max-height: 300px;
                overflow-y: auto;
                border: 1px solid #30363d;
            }}
        </style>
    </head>
    <body>
        <h1>🧠 Telegram Bot Panel</h1>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="file" name="botFile" required>
            <button type="submit">Upload Bot</button>
        </form>
        <br><br>
        <table>
            <tr>
                <th>Bot</th>
                <th>Actions</th>
            </tr>
            {bots_html}
        </table>
        <div id="logBox">Logs will appear here...</div>

        <script>
            function startBot(name) {{
                fetch('/bot/start/' + name)
                    .then(response => response.json())
                    .then(data => {{
                        document.getElementById("status-" + name).innerText = "✅ Started";
                    }});
            }}
            function stopBot(name) {{
                fetch('/bot/stop/' + name)
                    .then(response => response.json())
                    .then(data => {{
                        document.getElementById("status-" + name).innerText = "⛔ Stopped";
                    }});
            }}
            function viewLogs(name) {{
                fetch('/logs/' + name)
                    .then(response => response.text())
                    .then(text => {{
                        document.getElementById("logBox").innerText = text;
                    }});
            }}
            function deleteBot(name) {{
                if(confirm('Are you sure you want to delete "' + name + '"? This action cannot be undone.')) {{
                    fetch('/bot/delete/' + name, {{ method: 'DELETE' }})
                        .then(response => response.json())
                        .then(data => {{
                            if(data.status === 'deleted') {{
                                alert('Deleted ' + name);
                                location.reload();
                            }} else {{
                                alert('Error deleting ' + name);
                            }}
                        }});
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.route('/upload', methods=['POST'])
def upload():
    if 'botFile' not in request.files:
        return redirect('/')
    file = request.files['botFile']
    if file.filename.endswith('.py'):
        file.save(os.path.join(BOT_DIR, file.filename))
    return redirect('/')

@app.route('/bot/start/<bot>')
def start_bot(bot):
    if bot in running_bots:
        return jsonify({'status': 'already running'})
    bot_path = os.path.join(BOT_DIR, bot)
    log_path = os.path.join(LOG_DIR, f"{bot}.log")

    def run():
        with open(log_path, 'w') as log_file:
            process = subprocess.Popen(['python3', bot_path], stdout=log_file, stderr=log_file)
            running_bots[bot] = process
            process.wait()
            running_bots.pop(bot, None)

    threading.Thread(target=run, daemon=True).start()
    return jsonify({'status': 'started'})

@app.route('/bot/stop/<bot>')
def stop_bot(bot):
    process = running_bots.get(bot)
    if process:
        process.terminate()
        return jsonify({'status': 'stopped'})
    return jsonify({'status': 'not running'})

@app.route('/bot/delete/<bot>', methods=['DELETE'])
def delete_bot(bot):
    # Stop bot if running
    process = running_bots.get(bot)
    if process:
        process.terminate()
        running_bots.pop(bot, None)
    bot_path = os.path.join(BOT_DIR, bot)
    log_path = os.path.join(LOG_DIR, f"{bot}.log")
    try:
        if os.path.exists(bot_path):
            os.remove(bot_path)
        if os.path.exists(log_path):
            os.remove(log_path)
        return jsonify({'status': 'deleted'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/logs/<bot>')
def logs(bot):
    log_file = os.path.join(LOG_DIR, f"{bot}.log")
    if os.path.exists(log_file):
        with open(log_file) as f:
            return f.read()
    return "No logs found."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
