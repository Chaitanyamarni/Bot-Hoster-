import os
import json
import subprocess
import threading
from flask import Flask, request, render_template_string, redirect, url_for, session, jsonify, Response

app = Flask(__name__)
app.secret_key = "applixmain"
BASE_UPLOAD_FOLDER = "database"
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)
USERS_FILE = "users.json"
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)
        
bot_processes = {}
bot_logs = {}

ANKIT = """ 
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ZORO Hosting</title>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        :root {
            --primary-color: #007AFF;
            --background-color: #F2F2F7;
            --card-color: #FFFFFF;
            --text-color: #1C1C1E;
            --secondary-text: #8E8E93;
            --border-color: #D1D1D6;
        }
        
        @media (prefers-color-scheme: dark) {
            :root {
                --primary-color: #0A84FF;
                --background-color: #000;
                --card-color: #121212;
                --text-color: #F2F2F7;
                --secondary-text: #8E8E93;
                --border-color: #3A3A3C;
            }
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            height: 100vh;
            padding-bottom: 60px;
            overflow-x: hidden;
        }
        
        .container {
            padding: 16px;
            padding-bottom: 80px;
        }
        
        .header {
            padding: 16px;
            text-align: center;
            position: relative;
        }
        
        .header h1 {
            font-size: 22px;
            font-weight: 600;
        }
        
        .header p {
            font-size: 14px;
            color: var(--secondary-text);
            margin-top: 4px;
        }
        
        .card {
            background-color: var(--card-color);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .card-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
        }
        
        .card-title .material-icons {
            margin-right: 8px;
            font-size: 20px;
            color: var(--primary-color);
        }
        
        .bot-list {
            list-style: none;
        }
        
        .bot-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--border-color);
        }
        
        .bot-item:last-child {
            border-bottom: none;
        }
        
        .bot-name {
            font-weight: 500;
        }
        
        .bot-status {
            font-size: 13px;
            color: var(--secondary-text);
        }
        
        .bot-running {
            color: #34C759;
        }
        
        .bot-stopped {
            color: #FF3B30;
        }
        
        .bot-controls {
            display: none;
            margin-top: 16px;
        }
        
        .control-buttons {
            display: flex;
            gap: 8px;
            margin-top: 12px;
        }
        
        .btn {
            flex: 1;
            padding: 10px;
            border-radius: 8px;
            border: none;
            font-weight: 500;
            font-size: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: var(--primary-color);
            color: white;
        }
        
        .btn .material-icons {
            font-size: 18px;
            margin-right: 6px;
        }
        
        .btn-secondary {
            background-color: var(--card-color);
            color: var(--primary-color);
            border: 1px solid var(--border-color);
        }
        
        .log-container {
            height: 200px;
            overflow-y: auto;
            background-color: var(--background-color);
            border-radius: 8px;
            padding: 12px;
            font-family: 'Menlo', 'Courier New', monospace;
            font-size: 12px;
            margin-top: 12px;
            border: 1px solid var(--border-color);
        }
        
        .log-line {
            margin-bottom: 4px;
            line-height: 1.4;
            word-break: break-all;
        }
        
        .nav-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: var(--card-color);
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            border-top: 1px solid var(--border-color);
            z-index: 100;
        }
        
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-decoration: none;
            color: var(--secondary-text);
            font-size: 12px;
        }
        
        .nav-item.active {
            color: var(--primary-color);
        }
        
        .nav-item .material-icons {
            font-size: 24px;
            margin-bottom: 2px;
        }
        
        .file-input {
            display: none;
        }
        
        .upload-area {
            border: 2px dashed var(--border-color);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            margin-top: 16px;
        }
        
        .upload-area.active {
            border-color: var(--primary-color);
            background-color: rgba(0, 122, 255, 0.05);
        }
        
        .upload-icon {
            font-size: 40px;
            color: var(--primary-color);
            margin-bottom: 8px;
        }
        
        .upload-text {
            font-size: 16px;
            margin-bottom: 8px;
        }
        
        .upload-hint {
            font-size: 14px;
            color: var(--secondary-text);
        }
        
        .upload-btn {
            margin-top: 16px;
            width: 100%;
        }
        
        .settings-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--border-color);
        }
        
        .settings-item:last-child {
            border-bottom: none;
        }
        
        .settings-label {
            display: flex;
            align-items: center;
        }
        
        .settings-label .material-icons {
            margin-right: 12px;
            color: var(--primary-color);
        }
        
        .ios-alert {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: var(--card-color);
            border-radius: 14px;
            width: 270px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            z-index: 1000;
            display: none;
        }
        
        .ios-alert-title {
            font-size: 17px;
            font-weight: 600;
            text-align: center;
            padding: 15px 10px 5px;
        }
        
        .ios-alert-message {
            font-size: 13px;
            text-align: center;
            padding: 0 10px 15px;
            color: var(--secondary-text);
        }
        
        .ios-alert-buttons {
            display: flex;
            border-top: 1px solid var(--border-color);
        }
        
        .ios-alert-button {
            flex: 1;
            text-align: center;
            padding: 10px;
            font-weight: 500;
            color: var(--primary-color);
        }
        
        .ios-alert-button:not(:last-child) {
            border-right: 1px solid var(--border-color);
        }
        
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0,0,0,0.4);
            z-index: 999;
            display: none;
        }
    </style>
</head>
<body>
    <div class="overlay" id="overlay"></div>
    
    <div class="ios-alert" id="iosAlert">
        <div class="ios-alert-title" id="alertTitle">Title</div>
        <div class="ios-alert-message" id="alertMessage">Message</div>
        <div class="ios-alert-buttons">
            <div class="ios-alert-button" id="alertButton">OK</div>
        </div>
    </div>
    
    <div class="header">
        <h1>ZORO Bot Hosting</h1>
        <p>Welcome, {{ username }}</p>
    </div>
    
    <div class="container" id="homeView">
        <div class="card">
            <div class="card-title">
                <span class="material-icons">code</span>
                Your Bots
            </div>
            <ul class="bot-list" id="botList">
                {% for bot in bots %}
                <li class="bot-item" onclick="showBotControls('{{ bot }}')">
                    <span class="bot-name">{{ bot }}</span>
                    <span class="bot-status" id="status-{{ bot }}">Stopped</span>
                </li>
                {% endfor %}
            </ul>
        </div>
        
        <div class="card" id="botControls" style="display: none;">
            <div class="card-title">
                <span class="material-icons">settings</span>
                Bot Controls
            </div>
            <div id="selectedBotName" style="font-weight: 500; margin-bottom: 12px;"></div>
            <div class="control-buttons">
                <button class="btn" id="startBtn" onclick="controlBot('start')">
                    <span class="material-icons">play_arrow</span> Start
                </button>
                <button class="btn" id="stopBtn" onclick="controlBot('stop')" style="display: none;">
                    <span class="material-icons">stop</span> Stop
                </button>
                <button class="btn btn-secondary" onclick="controlBot('restart')">
                    <span class="material-icons">refresh</span> Restart
                </button>
            </div>
            <div class="control-buttons">
                <button class="btn btn-secondary" onclick="renameBot()">
                    <span class="material-icons">edit</span> Rename
                </button>
                <button class="btn btn-secondary" onclick="deleteBot()">
                    <span class="material-icons">delete</span> Delete
                </button>
            </div>
            
            <div style="margin-top: 16px;">
                <div class="card-title">
                    <span class="material-icons">terminal</span>
                    Logs
                </div>
                <div class="log-container" id="botLogs"></div>
                <button class="btn btn-secondary" style="margin-top: 12px;" onclick="copyLogs()">
                    <span class="material-icons">content_copy</span> Copy Logs
                </button>
            </div>
        </div>
    </div>
    
    <div class="container" id="uploadView" style="display: none;">
        <div class="card">
            <div class="card-title">
                <span class="material-icons">cloud_upload</span>
                Upload Bot
            </div>
            <form id="uploadForm" action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="bot_file" id="fileInput" class="file-input" accept=".py,.txt">
                <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                    <div class="upload-icon material-icons">cloud_upload</div>
                    <div class="upload-text">Choose a file or drag it here</div>
                    <div class="upload-hint">Python files only (.py)</div>
                </div>
                <div id="fileName" style="text-align: center; margin-top: 8px; color: var(--secondary-text);"></div>
                <button type="submit" class="btn upload-btn" id="uploadBtn" disabled>
                    <span class="material-icons">file_upload</span> Upload
                </button>
            </form>
        </div>
    </div>
    
    <div class="container" id="settingsView" style="display: none;">
        <div class="card">
            <div class="card-title">
                <span class="material-icons">settings</span>
                Settings
            </div>
            <div class="settings-item" onclick="showAlert('Account', 'Logged in as {{ username }}')">
                <div class="settings-label">
                    <span class="material-icons">account_circle</span>
                    Account
                </div>
                <span class="material-icons" style="color: var(--secondary-text);">chevron_right</span>
            </div>
            <div class="settings-item" onclick="showAlert('About', 'ZORO Bot Hosting v1.0')">
                <div class="settings-label">
                    <span class="material-icons">info</span>
                    About
                </div>
                <span class="material-icons" style="color: var(--secondary-text);">chevron_right</span>
            </div>
            <div class="settings-item" onclick="logout()">
                <div class="settings-label">
                    <span class="material-icons">logout</span>
                    Logout
                </div>
                <span class="material-icons" style="color: var(--secondary-text);">chevron_right</span>
            </div>
        </div>
    </div>
    
    <div class="nav-bar">
        <a href="#" class="nav-item active" onclick="showView('homeView')">
            <span class="material-icons">home</span>
            <span>Home</span>
        </a>
        <a href="#" class="nav-item" onclick="showView('uploadView')">
            <span class="material-icons">cloud_upload</span>
            <span>Upload</span>
        </a>
        <a href="#" class="nav-item" onclick="showView('settingsView')">
            <span class="material-icons">settings</span>
            <span>Settings</span>
        </a>
    </div>
    
    <script>
        let eventSource;
        let currentBot = null;
        
        // iOS-style alert
        function showAlert(title, message) {
            document.getElementById('alertTitle').textContent = title;
            document.getElementById('alertMessage').textContent = message;
            document.getElementById('overlay').style.display = 'block';
            document.getElementById('iosAlert').style.display = 'block';
        }
        
        document.getElementById('alertButton').addEventListener('click', function() {
            document.getElementById('overlay').style.display = 'none';
            document.getElementById('iosAlert').style.display = 'none';
        });
        
        // View navigation
        function showView(viewId) {
            document.getElementById('homeView').style.display = 'none';
            document.getElementById('uploadView').style.display = 'none';
            document.getElementById('settingsView').style.display = 'none';
            document.getElementById(viewId).style.display = 'block';
            
            // Update nav bar active state
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            
            if (viewId === 'homeView') {
                document.querySelectorAll('.nav-item')[0].classList.add('active');
            } else if (viewId === 'uploadView') {
                document.querySelectorAll('.nav-item')[1].classList.add('active');
            } else if (viewId === 'settingsView') {
                document.querySelectorAll('.nav-item')[2].classList.add('active');
            }
        }
        
        // File upload handling
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            const uploadArea = document.getElementById('uploadArea');
            const fileName = document.getElementById('fileName');
            const uploadBtn = document.getElementById('uploadBtn');
            
            if (file) {
                uploadArea.classList.add('active');
                fileName.textContent = file.name;
                uploadBtn.disabled = false;
            } else {
                uploadArea.classList.remove('active');
                fileName.textContent = '';
                uploadBtn.disabled = true;
            }
        });
        
        // Drag and drop for upload
        const uploadArea = document.getElementById('uploadArea');
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('active');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('active');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('active');
            
            if (e.dataTransfer.files.length) {
                document.getElementById('fileInput').files = e.dataTransfer.files;
                const fileName = document.getElementById('fileName');
                const uploadBtn = document.getElementById('uploadBtn');
                
                fileName.textContent = e.dataTransfer.files[0].name;
                uploadBtn.disabled = false;
            }
        });
        
        // Bot controls
        function showBotControls(botName) {
            currentBot = botName;
            document.getElementById('selectedBotName').textContent = botName;
            document.getElementById('botControls').style.display = 'block';
            updateBotStatus(botName);
            startLogStream(botName);
            
            // Scroll to controls
            document.getElementById('botControls').scrollIntoView({ behavior: 'smooth' });
        }
        
        function updateBotStatus(botName) {
            fetch('/bot_status/' + botName)
                .then(response => response.json())
                .then(data => {
                    const statusElement = document.getElementById('status-' + botName);
                    const startBtn = document.getElementById('startBtn');
                    const stopBtn = document.getElementById('stopBtn');
                    
                    if (data.running) {
                        statusElement.textContent = 'Running';
                        statusElement.className = 'bot-status bot-running';
                        startBtn.style.display = 'none';
                        stopBtn.style.display = 'flex';
                    } else {
                        statusElement.textContent = 'Stopped';
                        statusElement.className = 'bot-status bot-stopped';
                        startBtn.style.display = 'flex';
                        stopBtn.style.display = 'none';
                    }
                });
        }
        
        function controlBot(action) {
            if (!currentBot) return;
            
            fetch('/control_bot/' + currentBot + '/' + action)
                .then(response => response.text())
                .then(message => {
                    showAlert(action.charAt(0).toUpperCase() + action.slice(1), message);
                    updateBotStatus(currentBot);
                })
                .catch(error => {
                    showAlert('Error', 'Failed to perform action: ' + error);
                });
        }
        
        function startLogStream(botName) {
            if (eventSource) eventSource.close();
            
            const logContainer = document.getElementById('botLogs');
            logContainer.innerHTML = '';
            
            eventSource = new EventSource('/stream/' + botName);
            eventSource.onmessage = function(event) {
                const logLine = document.createElement('div');
                logLine.className = 'log-line';
                logLine.textContent = event.data;
                logContainer.appendChild(logLine);
                logContainer.scrollTop = logContainer.scrollHeight;
            };
        }
        
        function copyLogs() {
            const logs = document.getElementById('botLogs').textContent;
            navigator.clipboard.writeText(logs)
                .then(() => showAlert('Success', 'Logs copied to clipboard!'))
                .catch(() => showAlert('Error', 'Failed to copy logs'));
        }
        
        function renameBot() {
            if (!currentBot) return;
            
            const newName = prompt('Enter new name for ' + currentBot + ':', currentBot);
            if (newName && newName.trim() !== '' && newName.trim() !== currentBot) {
                window.location.href = '/rename/' + encodeURIComponent(currentBot) + '/' + encodeURIComponent(newName.trim());
            }
        }
        
        function deleteBot() {
            if (!currentBot) return;
            
            if (confirm('Are you sure you want to delete ' + currentBot + '?')) {
                window.location.href = '/permanent_delete/' + encodeURIComponent(currentBot);
            }
        }
        
        function logout() {
            window.location.href = '/logout';
        }
        
        // Initialize by checking all bot statuses
        document.addEventListener('DOMContentLoaded', function() {
            {% for bot in bots %}
                updateBotStatus('{{ bot }}');
            {% endfor %}
        });
    </script>
</body>
</html>
"""

ZORO = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ZORO Hosting - Login</title>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        :root {
            --primary-color: #007AFF;
            --background-color: #F2F2F7;
            --card-color: #FFFFFF;
            --text-color: #1C1C1E;
            --error-color: #FF3B30;
        }
        
        @media (prefers-color-scheme: dark) {
            :root {
                --primary-color: #0A84FF;
                --background-color: #000;
                --card-color: #121212;
                --text-color: #F2F2F7;
                --error-color: #FF453A;
            }
        }        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .login-container {
            width: 100%;
            max-width: 400px;
            background-color: var(--card-color);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo .material-icons {
            font-size: 50px;
            color: var(--primary-color);
        }
        
        .logo h1 {
            font-size: 24px;
            margin-top: 10px;
            font-weight: 600;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 8px;
            font-size: 14px;
            color: var(--text-color);
            opacity: 0.8;
        }
        
        .input-field {
            width: 100%;
            padding: 12px 15px;
            border: 1px solid #333;
            border-radius: 10px;
            font-size: 16px;
            background-color: var(--card-color);
            color: var(--text-color);
        }
        
        .input-field:focus {
            outline: none;
            border-color: var(--primary-color);
        }
        
        .login-btn {
            width: 100%;
            padding: 14px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 500;
            margin-top: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-btn .material-icons {
            margin-right: 8px;
        }
        
        .error-message {
            color: var(--error-color);
            font-size: 14px;
            margin-top: 15px;
            text-align: center;
            display: none;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <span class="material-icons">cloud</span>
            <h1>ZORO Hosting</h1>
        </div>
        
        <form id="loginForm" action="/login" method="post">
            <div class="input-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" class="input-field" placeholder="Enter your username" required>
            </div>
            
            <div class="input-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" class="input-field" placeholder="Enter your password" required>
            </div>
            
            <div class="error-message" id="errorMessage"></div>
            
            <button type="submit" class="login-btn">
                <span class="material-icons">login</span>
                Sign In
            </button>
        </form>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();
            const errorElement = document.getElementById('errorMessage');
            
            errorElement.style.display = 'none';
            
            fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.text();
                }
            })
            .then(text => {
                if (text) {
                    errorElement.textContent = text.replace(/<[^>]*>/g, '');
                    errorElement.style.display = 'block';
                }
            })
            .catch(error => {
                errorElement.textContent = 'An error occurred. Please try again.';
                errorElement.style.display = 'block';
            });
        });
    </script>
</body>
</html>

"""

@app.route("/", methods=["GET"])
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    user = session["username"]
    user_folder = os.path.join(BASE_UPLOAD_FOLDER, user)
    os.makedirs(user_folder, exist_ok=True)
    bots = os.listdir(user_folder)
    return render_template_string(ANKIT, bots=bots, username=user)

@app.route("/upload", methods=["POST"])
def upload_bot():
    if "username" not in session:
        return redirect(url_for("login"))
    user = session["username"]
    user_folder = os.path.join(BASE_UPLOAD_FOLDER, user)
    file = request.files.get("bot_file")
    if file:
        file_path = os.path.join(user_folder, file.filename)
        file.save(file_path)
        os.chmod(file_path, 0o755)
    return redirect(url_for("home"))

@app.route("/bot_status/<bot_name>", methods=["GET"])
def bot_status(bot_name):
    if "username" not in session:
        return jsonify({"running": False})
    user = session["username"]
    bot_name = os.path.basename(bot_name)
    if user not in bot_processes:
        bot_processes[user] = {}
    running = bot_name in bot_processes[user] and bot_processes[user][bot_name].poll() is None
    return jsonify({"running": running})

@app.route("/control_bot/<bot_name>/<action>", methods=["GET"])
def control_bot(bot_name, action):
    if "username" not in session:
        return redirect(url_for("login"))
    user = session["username"]
    bot_name = os.path.basename(bot_name)
    user_folder = os.path.join(BASE_UPLOAD_FOLDER, user)
    bot_path = os.path.join(user_folder, bot_name)
    if user not in bot_processes:
        bot_processes[user] = {}
    if action == "start":
        # Reset logs on start
        if user not in bot_logs:
            bot_logs[user] = {}
        bot_logs[user][bot_name] = []
        try:
            process = subprocess.Popen(
                ["python3", bot_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            bot_processes[user][bot_name] = process
            threading.Thread(target=stream_logs, args=(user, bot_name, process), daemon=True).start()
            return f"{bot_name} started successfully!"
        except Exception as e:
            return f"Failed to start {bot_name}: {str(e)}"
    elif action == "restart":
        if bot_name in bot_processes[user] and bot_processes[user][bot_name].poll() is None:
            bot_processes[user][bot_name].terminate()
        return control_bot(bot_name, "start")
    elif action == "stop":
        if bot_name in bot_processes[user] and bot_processes[user][bot_name].poll() is None:
            bot_processes[user][bot_name].terminate()
            return f"{bot_name} stopped successfully!"
        return f"{bot_name} is not running!"
    return "Invalid action!"

def stream_logs(user, bot_name, process):
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if user in bot_logs and bot_name in bot_logs[user]:
            bot_logs[user][bot_name].append(output.strip())

@app.route("/stream/<bot_name>")
def stream(bot_name):
    if "username" not in session:
        return redirect(url_for("login"))
    user = session["username"]
    bot_name = os.path.basename(bot_name)
    def event_stream():
        last_len = 0
        while True:
            if user in bot_logs and bot_name in bot_logs[user]:
                new_logs = bot_logs[user][bot_name][last_len:]
                last_len += len(new_logs)
                for line in new_logs:
                    yield f"data: {line}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/permanent_delete/<bot_name>", methods=["GET"])
def permanent_delete(bot_name):
    if "username" not in session:
        return redirect(url_for("login"))
    user = session["username"]
    bot_name = os.path.basename(bot_name)
    user_folder = os.path.join(BASE_UPLOAD_FOLDER, user)
    bot_path = os.path.join(user_folder, bot_name)
    if os.path.exists(bot_path):
        os.remove(bot_path)
    return redirect(url_for("home"))

@app.route("/rename/<old_name>/<new_name>", methods=["GET"])
def rename_bot(old_name, new_name):
    if "username" not in session:
        return redirect(url_for("login"))
    user = session["username"]
    old_name = os.path.basename(old_name)
    new_name = os.path.basename(new_name)
    user_folder = os.path.join(BASE_UPLOAD_FOLDER, user)
    old_path = os.path.join(user_folder, old_name)
    new_path = os.path.join(user_folder, new_name)
    if os.path.exists(new_path):
        return f"File with name {new_name} already exists. <a href='/'>Return</a>"
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        if user in bot_logs and old_name in bot_logs[user]:
            bot_logs[user][new_name] = bot_logs[user].pop(old_name)
        if user in bot_processes and old_name in bot_processes[user]:
            bot_processes[user][new_name] = bot_processes[user].pop(old_name)
        return redirect(url_for("home"))
    else:
        return f"File {old_name} not found. <a href='/'>Return</a>"
        
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        users = load_users()
        if username not in users:
            users[username] = password
            save_users(users)
            os.makedirs(os.path.join(BASE_UPLOAD_FOLDER, username), exist_ok=True)
            session["username"] = username
            return redirect(url_for("home"))
        else:
            if users[username] == password:
                session["username"] = username
                os.makedirs(os.path.join(BASE_UPLOAD_FOLDER, username), exist_ok=True)
                return redirect(url_for("home"))
            else:
                return "Invalid credentials"
    return render_template_string(ZORO)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2000, debug=True)