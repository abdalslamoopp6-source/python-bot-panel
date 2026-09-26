import os
import uuid
import subprocess
from flask import Flask, render_template_string, request, redirect, url_for, jsonify

app = Flask(__name__)

BOTS_DIR = 'bots'
os.makedirs(BOTS_DIR, exist_ok=True)

# لتخزين العمليات النشطة في الذاكرة
running_bots = {}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة استضافة بوتات بايثون</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --success: #10b981;
            --danger: #ef4444;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --border-color: #e2e8f0;
        }

        body {
            font-family: 'Tajawal', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 30px 20px;
            direction: rtl;
        }

        .container {
            max-width: 850px;
            margin: auto;
        }

        .header-title {
            text-align: center;
            color: var(--primary);
            margin-bottom: 30px;
            font-size: 28px;
            font-weight: 700;
        }

        .card {
            background: var(--card-bg);
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: 1px solid var(--border-color);
        }

        h2 {
            margin-top: 0;
            font-size: 20px;
            color: #334155;
            border-bottom: 2px solid var(--bg-color);
            padding-bottom: 12px;
            margin-bottom: 20px;
        }

        .upload-form {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }

        input[type="file"] {
            border: 2px dashed var(--border-color);
            padding: 12px;
            border-radius: 10px;
            width: 100%;
            max-width: 400px;
            background: #fdfdfd;
            cursor: pointer;
            font-family: 'Tajawal', sans-serif;
        }

        button {
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            color: white;
            font-weight: 500;
            font-family: 'Tajawal', sans-serif;
            transition: all 0.2s ease;
        }

        .btn-upload {
            background: var(--primary);
        }
        .btn-upload:hover {
            background: var(--primary-hover);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            overflow: hidden;
            border-radius: 10px;
        }

        th, td {
            padding: 14px 16px;
            text-align: center;
            border-bottom: 1px solid var(--border-color);
        }

        th {
            background-color: #f1f5f9;
            color: #475569;
            font-weight: 600;
        }

        tr:hover {
            background-color: #f8fafc;
        }

        .badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
            display: inline-block;
        }

        .status-running {
            background-color: #d1fae5;
            color: #065f46;
        }

        .status-stopped {
            background-color: #fee2e2;
            color: #991b1b;
        }

        .btn-start {
            background: var(--success);
            padding: 6px 14px;
            font-size: 14px;
        }
        .btn-start:hover { opacity: 0.9; }

        .btn-stop {
            background: var(--danger);
            padding: 6px 14px;
            font-size: 14px;
        }
        .btn-stop:hover { opacity: 0.9; }

        .actions {
            display: flex;
            gap: 8px;
            justify-content: center;
        }

        .empty-row {
            color: #64748b;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header-title">⚡ لوحة تحكم استضافة بوتات بايثون</h1>
        
        <!-- قسم رفع البوت -->
        <div class="card">
            <h2>رفع بوت جديد (.py)</h2>
            <form action="/upload" method="POST" enctype="multipart/form-data" class="upload-form">
                <input type="file" name="file" accept=".py" required>
                <button type="submit" class="btn-upload">رفع وتشغيل البوت</button>
            </form>
        </div>

        <!-- جدول عرض البوتات -->
        <div class="card">
            <h2>البوتات المرفوعة</h2>
            <table>
                <thead>
                    <tr>
                        <th>معرف البوت (ID)</th>
                        <th>الحالة</th>
                        <th>التحكم</th>
                    </tr>
                </thead>
                <tbody>
                    {% for bot in bots %}
                    <tr>
                        <td><code>{{ bot.id }}</code></td>
                        <td>
                            <span class="badge {{ 'status-running' if bot.status == 'يعمل' else 'status-stopped' }}">
                                {{ bot.status }}
                            </span>
                        </td>
                        <td>
                            <div class="actions">
                                <button class="btn-start" onclick="startBot('{{ bot.id }}')">تشغيل</button>
                                <button class="btn-stop" onclick="stopBot('{{ bot.id }}')">إيقاف</button>
                            </div>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="3" class="empty-row">لا توجد بوتات مرفوعة حتى الآن. ابدأ برفع أول بوت!</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function startBot(botId) {
            fetch('/start/' + botId, { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                });
        }

        function stopBot(botId) {
            fetch('/stop/' + botId, { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    bots = []
    if os.path.exists(BOTS_DIR):
        for bot_id in os.listdir(BOTS_DIR):
            bot_path = os.path.join(BOTS_DIR, bot_id)
            if os.path.isdir(bot_path):
                status = "يعمل" if bot_id in running_bots and running_bots[bot_id].poll() is None else "متوقف"
                bots.append({'id': bot_id, 'status': status})
    return render_template_string(HTML_TEMPLATE, bots=bots)

@app.route('/upload', methods=['POST'])
def upload_bot():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.py'):
        return redirect(url_for('index'))

    bot_id = str(uuid.uuid4())[:8]
    bot_folder = os.path.join(BOTS_DIR, bot_id)
    os.makedirs(bot_folder, exist_ok=True)
    
    file_path = os.path.join(bot_folder, 'main.py')
    file.save(file_path)
    
    return redirect(url_for('index'))

@app.route('/start/<bot_id>', methods=['POST'])
def start_bot(bot_id):
    bot_folder = os.path.join(BOTS_DIR, bot_id)
    main_file = os.path.join(bot_folder, 'main.py')

    if os.path.exists(main_file):
        if bot_id in running_bots and running_bots[bot_id].poll() is None:
            return jsonify({'success': False, 'message': 'البوت يعمل بالفعل!'})

        process = subprocess.Popen(
            ['python', 'main.py'], 
            cwd=bot_folder,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        running_bots[bot_id] = process
        
        return jsonify({'success': True, 'message': 'تم تشغيل البوت بنجاح!'})
    
    return jsonify({'success': False, 'message': 'ملف البوت غير موجود!'})

@app.route('/stop/<bot_id>', methods=['POST'])
def stop_bot(bot_id):
    if bot_id in running_bots:
        process = running_bots[bot_id]
        if process.poll() is None:
            process.terminate()
            process.wait()
        del running_bots[bot_id]
        return jsonify({'success': True, 'message': 'تم إيقاف البوت.'})
    return jsonify({'success': False, 'message': 'البوت متوقف مسبقاً.'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
