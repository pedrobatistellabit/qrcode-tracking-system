"""
Backend Flask para Sistema de Rastreamento de QR Codes
"""
from flask import Flask, request, redirect, jsonify, render_template_string
from flask_cors import CORS
from functools import wraps
import os
from datetime import datetime
from config import Config
from models import Database, QRCode, Scan
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização do Flask
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)

# Inicialização do banco de dados
db = Database(Config.SQLITE_DB_PATH)
qrcode_model = QRCode(db)
scan_model = Scan(db)


def require_api_key(f):
    """Decorator para proteger endpoints administrativos"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if api_key != Config.API_KEY:
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


def extract_device_type(user_agent: str) -> str:
    """Extrai o tipo de dispositivo do User-Agent"""
    if not user_agent:
        return 'Unknown'
    
    user_agent_lower = user_agent.lower()
    
    if 'mobile' in user_agent_lower or 'android' in user_agent_lower or 'iphone' in user_agent_lower:
        return 'Mobile'
    elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
        return 'Tablet'
    else:
        return 'Desktop'


@app.route('/')
def index():
    """Página inicial com informações do sistema"""
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sistema de Rastreamento de QR Codes</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .endpoint {
                background: #f8f8f8;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #007bff;
                border-radius: 4px;
            }
            code {
                background: #e9ecef;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
            .status {
                color: #28a745;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Sistema de Rastreamento de QR Codes</h1>
            <p class="status">✓ Sistema Online</p>
            
            <h2>Endpoints Disponíveis</h2>
            
            <div class="endpoint">
                <strong>GET /track</strong>
                <p>Endpoint de rastreamento e redirecionamento</p>
                <p>Parâmetros: <code>qr_id</code> (obrigatório), <code>source</code> (opcional)</p>
                <p>Exemplo: <code>/track?qr_id=DEMO001&source=instagram</code></p>
            </div>
            
            <div class="endpoint">
                <strong>GET /admin/scans</strong>
                <p>Visualizar todos os escaneamentos (requer API key)</p>
                <p>Header: <code>X-API-Key: sua-api-key</code></p>
            </div>
            
            <div class="endpoint">
                <strong>GET /admin/qrcodes</strong>
                <p>Listar todos os QR Codes (requer API key)</p>
            </div>
            
            <div class="endpoint">
                <strong>POST /admin/qrcodes</strong>
                <p>Criar novo QR Code (requer API key)</p>
                <p>Body: <code>{"qr_id": "ABC123", "name": "Meu QR", "target_url": "https://..."}</code></p>
            </div>
            
            <div class="endpoint">
                <strong>GET /admin/stats</strong>
                <p>Estatísticas gerais do sistema (requer API key)</p>
            </div>
            
            <h2>Documentação</h2>
            <p>Para mais informações, consulte a documentação completa do projeto.</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/track', methods=['GET'])
def track():
    """
    Endpoint principal de rastreamento
    Registra o escaneamento e redireciona para o URL de destino
    """
    qr_id = request.args.get('qr_id')
    source = request.args.get('source', 'direct')
    
    if not qr_id:
        return jsonify({'error': 'Missing qr_id parameter'}), 400
    
    # Buscar QR Code no banco
    qr_code = qrcode_model.get_by_qr_id(qr_id)
    
    if not qr_code:
        return jsonify({'error': 'QR Code not found'}), 404
    
    # Extrair informações da requisição
    scanner_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    referer = request.headers.get('Referer', '')
    device_type = extract_device_type(user_agent)
    
    # Registrar escaneamento
    try:
        scan_model.create(
            qr_id=qr_id,
            source=source,
            scanner_ip=scanner_ip,
            user_agent=user_agent,
            referer=referer,
            device_type=device_type
        )
        logger.info(f"Scan registered: qr_id={qr_id}, source={source}, ip={scanner_ip}")
    except Exception as e:
        logger.error(f"Error registering scan: {e}")
    
    # Redirecionar para URL de destino
    return redirect(qr_code['target_url'], code=302)


@app.route('/admin/scans', methods=['GET'])
@require_api_key
def get_scans():
    """Retorna lista de escaneamentos"""
    qr_id = request.args.get('qr_id')
    limit = int(request.args.get('limit', 100))
    
    if qr_id:
        scans = scan_model.get_by_qr_id(qr_id, limit)
    else:
        scans = scan_model.get_all(limit)
    
    return jsonify({
        'success': True,
        'count': len(scans),
        'scans': scans
    })


@app.route('/admin/qrcodes', methods=['GET'])
@require_api_key
def get_qrcodes():
    """Retorna lista de QR Codes"""
    qrcodes = qrcode_model.get_all()
    
    return jsonify({
        'success': True,
        'count': len(qrcodes),
        'qrcodes': qrcodes
    })


@app.route('/admin/qrcodes', methods=['POST'])
@require_api_key
def create_qrcode():
    """Cria um novo QR Code"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['qr_id', 'name', 'target_url']):
        return jsonify({'error': 'Missing required fields: qr_id, name, target_url'}), 400
    
    qr_code = qrcode_model.create(
        qr_id=data['qr_id'],
        name=data['name'],
        target_url=data['target_url']
    )
    
    if not qr_code:
        return jsonify({'error': 'QR Code already exists'}), 409
    
    return jsonify({
        'success': True,
        'qrcode': qr_code
    }), 201


@app.route('/admin/stats', methods=['GET'])
@require_api_key
def get_stats():
    """Retorna estatísticas gerais"""
    qr_id = request.args.get('qr_id')
    
    stats = scan_model.get_statistics(qr_id)
    
    return jsonify({
        'success': True,
        'statistics': stats
    })


@app.route('/admin/qrcodes/<qr_id>', methods=['DELETE'])
@require_api_key
def delete_qrcode(qr_id):
    """Desativa um QR Code"""
    success = qrcode_model.delete(qr_id)
    
    if not success:
        return jsonify({'error': 'QR Code not found'}), 404
    
    return jsonify({
        'success': True,
        'message': 'QR Code deleted successfully'
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)

