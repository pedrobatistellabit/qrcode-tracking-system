# 📡 Documentação da API

Documentação completa dos endpoints da API do Sistema de Rastreamento de QR Codes.

## 🔑 Autenticação

Endpoints administrativos requerem autenticação via API Key no header:

```http
X-API-Key: sua-api-key-aqui
```

Ou como parâmetro de query:

```http
GET /admin/qrcodes?api_key=sua-api-key-aqui
```

## 🌐 Base URL

**Desenvolvimento**: `http://localhost:5000`  
**Produção**: `https://track.aicompleta.com`

## 📍 Endpoints Públicos

### Health Check

Verifica se o sistema está online.

**Endpoint**: `GET /health`  
**Autenticação**: Não requerida

**Resposta de Sucesso** (200):
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T21:30:00.000000"
}
```

**Exemplo**:
```bash
curl https://track.aicompleta.com/health
```

---

### Rastreamento de QR Code

Registra um escaneamento e redireciona para URL de destino.

**Endpoint**: `GET /track`  
**Autenticação**: Não requerida

**Parâmetros de Query**:
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| qr_id | string | Sim | ID único do QR Code |
| source | string | Não | Origem do escaneamento (ex: instagram, facebook) |

**Resposta de Sucesso** (302):
- Redirecionamento HTTP para URL de destino
- Header `Location` contém a URL

**Resposta de Erro** (400):
```json
{
  "error": "Missing qr_id parameter"
}
```

**Resposta de Erro** (404):
```json
{
  "error": "QR Code not found"
}
```

**Exemplos**:
```bash
# Escaneamento básico
curl -I "https://track.aicompleta.com/track?qr_id=PROMO001"

# Com origem específica
curl -I "https://track.aicompleta.com/track?qr_id=PROMO001&source=instagram"
```

**Dados Capturados Automaticamente**:
- IP do scanner
- User-Agent (navegador/dispositivo)
- Referer (URL de origem)
- Tipo de dispositivo (Mobile/Tablet/Desktop)
- Data/hora do escaneamento

---

## 🔐 Endpoints Administrativos

Todos os endpoints abaixo requerem autenticação via API Key.

### Listar QR Codes

Retorna lista de todos os QR Codes cadastrados.

**Endpoint**: `GET /admin/qrcodes`  
**Autenticação**: Requerida

**Resposta de Sucesso** (200):
```json
{
  "success": true,
  "count": 2,
  "qrcodes": [
    {
      "id": "uuid-here",
      "qr_id": "PROMO001",
      "name": "Promoção Instagram",
      "target_url": "https://aicompleta.com/promo",
      "created_at": "2025-10-18T10:00:00",
      "updated_at": "2025-10-18T10:00:00",
      "is_active": 1
    }
  ]
}
```

**Exemplo**:
```bash
curl -H "X-API-Key: sua-api-key" \
  https://track.aicompleta.com/admin/qrcodes
```

---

### Criar QR Code

Cria um novo QR Code no sistema.

**Endpoint**: `POST /admin/qrcodes`  
**Autenticação**: Requerida  
**Content-Type**: `application/json`

**Body**:
```json
{
  "qr_id": "PROMO001",
  "name": "Promoção Instagram",
  "target_url": "https://aicompleta.com/promo"
}
```

**Campos**:
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| qr_id | string | Sim | ID único do QR Code (alfanumérico) |
| name | string | Sim | Nome descritivo |
| target_url | string | Sim | URL de destino (deve incluir http:// ou https://) |

**Resposta de Sucesso** (201):
```json
{
  "success": true,
  "qrcode": {
    "id": "uuid-here",
    "qr_id": "PROMO001",
    "name": "Promoção Instagram",
    "target_url": "https://aicompleta.com/promo",
    "created_at": "2025-10-18T10:00:00",
    "is_active": true
  }
}
```

**Resposta de Erro** (400):
```json
{
  "error": "Missing required fields: qr_id, name, target_url"
}
```

**Resposta de Erro** (409):
```json
{
  "error": "QR Code already exists"
}
```

**Exemplo**:
```bash
curl -X POST \
  -H "X-API-Key: sua-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "qr_id": "PROMO001",
    "name": "Promoção Instagram",
    "target_url": "https://aicompleta.com/promo"
  }' \
  https://track.aicompleta.com/admin/qrcodes
```

---

### Deletar QR Code

Desativa um QR Code (soft delete).

**Endpoint**: `DELETE /admin/qrcodes/<qr_id>`  
**Autenticação**: Requerida

**Parâmetros de URL**:
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| qr_id | string | ID do QR Code a ser deletado |

**Resposta de Sucesso** (200):
```json
{
  "success": true,
  "message": "QR Code deleted successfully"
}
```

**Resposta de Erro** (404):
```json
{
  "error": "QR Code not found"
}
```

**Exemplo**:
```bash
curl -X DELETE \
  -H "X-API-Key: sua-api-key" \
  https://track.aicompleta.com/admin/qrcodes/PROMO001
```

---

### Listar Escaneamentos

Retorna lista de escaneamentos registrados.

**Endpoint**: `GET /admin/scans`  
**Autenticação**: Requerida

**Parâmetros de Query**:
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| qr_id | string | Não | Filtrar por QR Code específico |
| limit | integer | Não | Limite de resultados (padrão: 100) |

**Resposta de Sucesso** (200):
```json
{
  "success": true,
  "count": 15,
  "scans": [
    {
      "id": "uuid-here",
      "qr_id": "PROMO001",
      "source": "instagram",
      "scanned_at": "2025-10-18T14:30:00",
      "scanner_ip": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "referer": "https://instagram.com",
      "device_type": "Mobile",
      "country": null,
      "city": null
    }
  ]
}
```

**Exemplos**:
```bash
# Todos os escaneamentos
curl -H "X-API-Key: sua-api-key" \
  https://track.aicompleta.com/admin/scans

# Filtrar por QR Code
curl -H "X-API-Key: sua-api-key" \
  "https://track.aicompleta.com/admin/scans?qr_id=PROMO001"

# Limitar resultados
curl -H "X-API-Key: sua-api-key" \
  "https://track.aicompleta.com/admin/scans?limit=50"
```

---

### Estatísticas

Retorna estatísticas de escaneamento.

**Endpoint**: `GET /admin/stats`  
**Autenticação**: Requerida

**Parâmetros de Query**:
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| qr_id | string | Não | Estatísticas de QR Code específico |

**Resposta de Sucesso** (200):
```json
{
  "success": true,
  "statistics": {
    "total_scans": 150,
    "unique_scanners": 87,
    "last_scan": "2025-10-18T14:30:00",
    "first_scan": "2025-10-01T09:00:00"
  }
}
```

**Exemplos**:
```bash
# Estatísticas gerais
curl -H "X-API-Key: sua-api-key" \
  https://track.aicompleta.com/admin/stats

# Estatísticas de QR Code específico
curl -H "X-API-Key: sua-api-key" \
  "https://track.aicompleta.com/admin/stats?qr_id=PROMO001"
```

---

## 🐍 Exemplos em Python

### Criar QR Code

```python
import requests

API_BASE = "https://track.aicompleta.com"
API_KEY = "sua-api-key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

data = {
    "qr_id": "PROMO001",
    "name": "Promoção Instagram",
    "target_url": "https://aicompleta.com/promo"
}

response = requests.post(
    f"{API_BASE}/admin/qrcodes",
    json=data,
    headers=headers
)

if response.status_code == 201:
    qrcode = response.json()["qrcode"]
    print(f"QR Code criado: {qrcode['qr_id']}")
else:
    print(f"Erro: {response.json()}")
```

### Listar Escaneamentos

```python
import requests

API_BASE = "https://track.aicompleta.com"
API_KEY = "sua-api-key"

headers = {"X-API-Key": API_KEY}

response = requests.get(
    f"{API_BASE}/admin/scans",
    params={"qr_id": "PROMO001", "limit": 50},
    headers=headers
)

if response.status_code == 200:
    scans = response.json()["scans"]
    print(f"Total de escaneamentos: {len(scans)}")
    
    for scan in scans:
        print(f"- {scan['scanned_at']} | {scan['device_type']} | {scan['source']}")
else:
    print(f"Erro: {response.json()}")
```

### Obter Estatísticas

```python
import requests

API_BASE = "https://track.aicompleta.com"
API_KEY = "sua-api-key"

headers = {"X-API-Key": API_KEY}

response = requests.get(
    f"{API_BASE}/admin/stats",
    params={"qr_id": "PROMO001"},
    headers=headers
)

if response.status_code == 200:
    stats = response.json()["statistics"]
    print(f"""
    Total de Scans: {stats['total_scans']}
    Scanners Únicos: {stats['unique_scanners']}
    Último Scan: {stats['last_scan']}
    """)
```

---

## 🌐 Exemplos em JavaScript

### Criar QR Code (Node.js)

```javascript
const axios = require('axios');

const API_BASE = 'https://track.aicompleta.com';
const API_KEY = 'sua-api-key';

async function createQRCode() {
  try {
    const response = await axios.post(
      `${API_BASE}/admin/qrcodes`,
      {
        qr_id: 'PROMO001',
        name: 'Promoção Instagram',
        target_url: 'https://aicompleta.com/promo'
      },
      {
        headers: {
          'X-API-Key': API_KEY,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('QR Code criado:', response.data.qrcode);
  } catch (error) {
    console.error('Erro:', error.response.data);
  }
}

createQRCode();
```

### Listar Escaneamentos (Browser)

```javascript
const API_BASE = 'https://track.aicompleta.com';
const API_KEY = 'sua-api-key';

fetch(`${API_BASE}/admin/scans?qr_id=PROMO001&limit=50`, {
  headers: {
    'X-API-Key': API_KEY
  }
})
  .then(response => response.json())
  .then(data => {
    console.log(`Total: ${data.count} escaneamentos`);
    data.scans.forEach(scan => {
      console.log(`${scan.scanned_at} | ${scan.device_type} | ${scan.source}`);
    });
  })
  .catch(error => console.error('Erro:', error));
```

---

## 📊 Códigos de Status HTTP

| Código | Significado | Descrição |
|--------|-------------|-----------|
| 200 | OK | Requisição bem-sucedida |
| 201 | Created | Recurso criado com sucesso |
| 302 | Found | Redirecionamento (endpoint /track) |
| 400 | Bad Request | Parâmetros inválidos ou ausentes |
| 401 | Unauthorized | API Key inválida ou ausente |
| 404 | Not Found | Recurso não encontrado |
| 409 | Conflict | Recurso já existe (QR Code duplicado) |
| 500 | Internal Server Error | Erro interno do servidor |

---

## 🔒 Segurança

### Proteção da API Key

**❌ Não faça:**
```javascript
// Expor API Key no frontend
const API_KEY = 'minha-api-key-secreta';
fetch(`/admin/qrcodes?api_key=${API_KEY}`);
```

**✅ Faça:**
```javascript
// Use proxy backend
fetch('/api/qrcodes', {
  // Seu backend adiciona a API Key
});
```

### Rate Limiting

- Limite recomendado: 100 requisições/minuto por IP
- Endpoints públicos (/track): sem limite
- Endpoints administrativos: 100 req/min

### CORS

Configure `CORS_ORIGINS` no `.env` para restringir origens:

```env
CORS_ORIGINS=https://aicompleta.com,https://app.aicompleta.com
```

---

## 📞 Suporte

Para dúvidas sobre a API:
- GitHub Issues: https://github.com/pedrobatistellabit/qrcode-tracking-system/issues
- Email: api@aicompleta.com

---

**Versão da API**: 1.0  
**Última atualização**: 18/10/2025

