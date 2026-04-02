from flask import Flask, render_template_string, request, jsonify, Response
from flask_socketio import SocketIO, emit
from functools import wraps
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lezzet-duragi-secret-key-2026'

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25
)

orders = []

# ====================== TEK ŞİFRE ======================
ADMIN_PASSWORD = "Hamza Göktürk"

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.password != ADMIN_PASSWORD:
            return Response('Şifre gereklidir.', 401, {'WWW-Authenticate': 'Basic realm="Lezzet Admin"'})
        return f(*args, **kwargs)
    return decorated

# ====================== MENÜ HTML (Checkbox'lı) ======================
MENU_HTML = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lezzet Durağı • Menü</title>
    <script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin:0; padding:20px; background: linear-gradient(135deg, #f5e8c7, #f4d9b0); text-align:center; }
        h1 { color: #b74c2e; }
        .subtitle { color:#666; font-size:1.15em; margin-bottom:30px; }
        .menu-section { background:white; margin:25px auto; padding:25px; border-radius:16px; box-shadow:0 8px 25px rgba(0,0,0,0.1); max-width:720px; text-align:left; }
        .menu-item { padding:12px; margin:8px 0; background:#fffaf0; border-radius:10px; display:flex; align-items:center; }
        .menu-item input { margin-right:12px; transform:scale(1.3); }
        .price { margin-left:auto; color:#b74c2e; font-weight:bold; }
        input[type=number] { padding:12px; font-size:1.2em; width:180px; text-align:center; border:2px solid #b74c2e; border-radius:10px; }
        button { background:#b74c2e; color:white; border:none; padding:16px 32px; font-size:1.15em; border-radius:12px; cursor:pointer; margin:25px 10px; }
        button:hover { background:#9c3f26; transform:scale(1.05); }
        #qrcode { margin:30px auto; padding:20px; background:white; border-radius:16px; display:inline-block; }
    </style>
</head>
<body>
    <h1>🍽️ Lezzet Durağı</h1>
    <p class="subtitle">Hoş geldiniz! İstediğiniz ürünleri seçin ve sipariş verin.</p>

    <div class="menu-section">
        <h2>☕ Kahve ve İçecekler</h2>
        <label class="menu-item"><input type="checkbox" value="Türk Kahvesi (Orta)"> Türk Kahvesi (Orta) <span class="price">35 TL</span></label>
        <label class="menu-item"><input type="checkbox" value="Espresso"> Espresso <span class="price">30 TL</span></label>
        <label class="menu-item"><input type="checkbox" value="Cappuccino"> Cappuccino <span class="price">40 TL</span></label>
        <label class="menu-item"><input type="checkbox" value="Latte"> Latte <span class="price">45 TL</span></label>
        <label class="menu-item"><input type="checkbox" value="Cold Brew"> Cold Brew <span class="price">50 TL</span></label>
        <label class="menu-item"><input type="checkbox" value="Çay"> Çay <span class="price">15 TL</span></label>
        <label class="menu-item"><input type="checkbox" value="Adaçayı"> Adaçayı / Ihlamur <span class="price">25 TL</span></label>
        <label class="menu-item"><input type="checkbox" value="Limonata"> Limonata <span class="price">30 TL</span></label>
        <label class="menu-item"><input type="checkbox" value="Milkshake"> Milkshake <span class="price">45 TL</span></label>
        <label class="menu-item"><input type="checkbox" value="Portakal Suyu"> Portakal Suyu <span class="price">35 TL</span></label>
        <label class="menu-item"><input type="checkbox" value="Buzlu Çay"> Buzlu Çay <span class="price">25 TL</span></label>
        <label class="menu-item"><input type="checkbox" value="Sıcak Çikolata"> Sıcak Çikolata <span class="price">40 TL</span></label>
    </div>

    <div class="menu-section">
        <label for="table"><strong>Masa Numaranız:</strong></label><br><br>
        <input type="number" id="table" placeholder="Örn: 7" min="1">
    </div>

    <button onclick="sendOrder()">📤 Sipariş Ver</button>
    <div id="qrcode"></div>

    <script src="https://cdn.socket.io/4.8.3/socket.io.min.js"></script>
    <script>
        new QRCode(document.getElementById("qrcode"), {
            text: window.location.origin + "/menu",
            width: 220,
            height: 220,
            colorDark: "#b74c2e"
        });

        function sendOrder() {
            const table = document.getElementById('table').value.trim();
            if (!table) return alert('❗ Lütfen masa numaranızı girin!');

            const selected = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
                                  .map(cb => cb.value);

            if (selected.length === 0) return alert('❗ Lütfen en az bir ürün seçin!');

            fetch('/order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ table: parseInt(table), items: selected })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert(`✅ Siparişiniz alındı!\nMasa: \( {table}\n \){selected.length} ürün`);
                    document.getElementById('table').value = '';
                    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
                }
            })
            .catch(() => alert('Bağlantı hatası. Tekrar deneyin.'));
        }
    </script>
</body>
</html>
'''

# ====================== ADMIN HTML ======================
ADMIN_HTML = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lezzet Durağı • Admin</title>
    <script src="https://cdn.socket.io/4.8.3/socket.io.min.js"></script>
    <style>
        body { font-family:'Segoe UI',Arial,sans-serif; margin:20px; background:#f8f1e3; }
        h1 { color:#b74c2e; text-align:center; }
        .order { background:white; padding:20px; margin:15px auto; border-radius:14px; box-shadow:0 6px 20px rgba(0,0,0,0.1); max-width:700px; border-left:7px solid #ff9800; }
        .order.preparing { border-left-color:#2196F3; }
        .order.ready { border-left-color:#4CAF50; }
        .order.completed { border-left-color:#9E9E9E; opacity:0.9; }
        .table-num { font-size:1.45em; font-weight:bold; color:#b74c2e; }
        button { margin:5px 4px; padding:10px 16px; border:none; border-radius:8px; cursor:pointer; }
        .btn-preparing { background:#2196F3; color:white; }
        .btn-ready { background:#4CAF50; color:white; }
        .btn-completed { background:#607D8B; color:white; }
    </style>
</head>
<body>
    <h1>🛠️ Admin Panel - Canlı Siparişler</h1>
    <div id="orders"></div>

    <script>
        const socket = io();

        function renderOrders(ordersList) {
            const container = document.getElementById('orders');
            container.innerHTML = '';
            if (ordersList.length === 0) {
                container.innerHTML = '<p style="text-align:center;color:#666;">Henüz sipariş yok.</p>';
                return;
            }
            ordersList.sort((a,b) => b.id - a.id);
            ordersList.forEach(order => {
                const div = document.createElement('div');
                div.className = `order ${order.status}`;
                let statusHTML = '';
                if (order.status === 'new') statusHTML = '<span style="background:#ff9800;color:white;padding:6px 14px;border-radius:20px;">🆕 Yeni</span>';
                else if (order.status === 'preparing') statusHTML = '<span style="background:#2196F3;color:white;padding:6px 14px;border-radius:20px;">👨‍🍳 Hazırlanıyor</span>';
                else if (order.status === 'ready') statusHTML = '<span style="background:#4CAF50;color:white;padding:6px 14px;border-radius:20px;">✅ Hazır</span>';
                else if (order.status === 'completed') statusHTML = '<span style="background:#9E9E9E;color:white;padding:6px 14px;border-radius:20px;">📦 Tamamlandı</span>';

                div.innerHTML = `
                    <div class="table-num">${order.table}</div>
                    <small>${order.time}</small><br><br>
                    <strong>Ürünler:</strong><br>
                    ${order.items.map(i => `• ${i}`).join('<br>')}<br><br>
                    ${statusHTML}
                    <div style="margin-top:15px;">
                        \( {order.status !== 'preparing' ? `<button class="btn-preparing" onclick="updateStatus( \){order.id}, 'preparing')">Hazırlanıyor</button>` : ''}
                        \( {order.status !== 'ready' ? `<button class="btn-ready" onclick="updateStatus( \){order.id}, 'ready')">Hazır</button>` : ''}
                        \( {order.status !== 'completed' ? `<button class="btn-completed" onclick="updateStatus( \){order.id}, 'completed')">Tamamlandı</button>` : ''}
                    </div>
                `;
                container.appendChild(div);
            });
        }

        function updateStatus(id, status) {
            fetch(`/order/${id}/status`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ status })
            });
        }

        socket.on('newOrder', () => fetch('/orders').then(r=>r.json()).then(renderOrders));
        socket.on('ordersUpdated', renderOrders);
        fetch('/orders').then(r => r.json()).then(renderOrders);
    </script>
</body>
</html>
'''

# ====================== ROUTES ======================

@app.route('/')
def home():
    return "🍽️ <b>Lezzet Durağı</b><br><br><a href='/menu'>→ Menü</a> | <a href='/lezet-admin'>→ Admin Panel</a>"

@app.route('/menu')
def menu():
    return render_template_string(MENU_HTML)

@app.route('/lezet-admin')
@requires_auth
def admin():
    return render_template_string(ADMIN_HTML)

@app.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    table = data.get('table')
    items = data.get('items')

    if not table or not items or not isinstance(items, list) or len(items) == 0:
        return jsonify({'error': 'Geçersiz sipariş'}), 400

    order = {
        'id': int(datetime.datetime.now().timestamp() * 1000),
        'table': f"Masa {table}",
        'items': items,
        'time': datetime.datetime.now().strftime("%H:%M:%S"),
        'status': 'new'
    }

    orders.append(order)
    print(f"✅ Yeni Sipariş: {order['table']} - {len(items)} ürün")

    # Emit'leri güçlendirdik
    socketio.emit('newOrder', order, broadcast=True)
    socketio.emit('ordersUpdated', orders, broadcast=True)

    return jsonify({'success': True, 'message': 'Siparişiniz alındı!', 'orderId': order['id']})

@app.route('/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/order/<int:order_id>/status', methods=['PUT'])
def update_status(order_id):
    data = request.get_json()
    status = data.get('status')
    valid_statuses = ['new', 'preparing', 'ready', 'completed']
    if status not in valid_statuses:
        return jsonify({'error': 'Geçersiz durum'}), 400

    order = next((o for o in orders if o['id'] == order_id), None)
    if not order:
        return jsonify({'error': 'Sipariş bulunamadı'}), 404

    old = order['status']
    order['status'] = status
    print(f"🔄 Durum değişti: {order['table']} | {old} → {status}")

    socketio.emit('orderStatusUpdated', {'id': order['id'], 'status': status, 'table': order['table']}, broadcast=True)
    socketio.emit('ordersUpdated', orders, broadcast=True)

    return jsonify({'success': True, 'order': order})

@socketio.on('connect')
def handle_connect():
    print('📡 Client bağlandı')

@socketio.on('disconnect')
def handle_disconnect():
    print('📴 Client ayrıldı')

# ====================== BAŞLAT ======================
if __name__ == '__main__':
    print("🚀 Lezzet Durağı Flask sunucusu çalışıyor...")
    print("   Menü       : http://localhost:5000/menu")
    print("   Admin Panel: http://localhost:5000/lezet-admin")
    print(f"   Şifre      : {ADMIN_PASSWORD}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)