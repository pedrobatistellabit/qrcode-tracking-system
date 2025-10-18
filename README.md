# 🔍 Sistema de Rastreamento de QR Codes

Sistema completo para geração, rastreamento e análise de QR Codes com registro detalhado de escaneamentos.

## 📋 Visão Geral

Este sistema permite criar QR Codes rastreáveis que registram informações detalhadas sobre cada escaneamento, incluindo:

- **Identificação**: QR Code ID e origem do escaneamento
- **Dados do Scanner**: IP, User-Agent, tipo de dispositivo
- **Timestamps**: Data e hora precisas de cada escaneamento
- **Redirecionamento**: Encaminhamento automático para URL de destino

## 🏗️ Arquitetura

O sistema é composto por três componentes principais:

### 1. Backend API (Flask)
- Endpoints de rastreamento e redirecionamento
- API administrativa para gestão de QR Codes
- Registro automático de escaneamentos
- Proteção com API Key

### 2. Banco de Dados
- **Desenvolvimento**: SQLite (local)
- **Produção**: PostgreSQL/Supabase
- Tabelas: `qrcodes` e `scans`
- Índices otimizados para consultas rápidas

### 3. Gerador de QR Codes
- Script Python para geração individual ou em lote
- Suporte a múltiplas origens/fontes
- Personalização de tamanho e borda
- Alta correção de erros

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose (opcional)
- PostgreSQL (para produção)

### Instalação Local

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd qrcode-tracking-system

# 2. Instalar dependências
cd backend
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# 4. Iniciar o servidor
python app.py
```

O servidor estará disponível em `http://localhost:5000`

### Instalação com Docker

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f backend

# Parar serviços
docker-compose down
```

## 📡 Endpoints da API

### Público

#### `GET /track`
Endpoint de rastreamento e redirecionamento.

**Parâmetros:**
- `qr_id` (obrigatório): ID do QR Code
- `source` (opcional): Origem do escaneamento

**Exemplo:**
```
https://track.aicompleta.com/track?qr_id=PROMO001&source=instagram
```

**Resposta:**
- Redirecionamento 302 para URL de destino
- Registro automático do escaneamento

### Administrativos (requer API Key)

Todos os endpoints administrativos requerem autenticação via header:
```
X-API-Key: sua-api-key
```

#### `GET /admin/qrcodes`
Lista todos os QR Codes cadastrados.

**Resposta:**
```json
{
  "success": true,
  "count": 2,
  "qrcodes": [
    {
      "id": "uuid",
      "qr_id": "PROMO001",
      "name": "Promoção Instagram",
      "target_url": "https://aicompleta.com/promo",
      "created_at": "2025-10-18T10:00:00",
      "is_active": true
    }
  ]
}
```

#### `POST /admin/qrcodes`
Cria um novo QR Code.

**Body:**
```json
{
  "qr_id": "PROMO001",
  "name": "Promoção Instagram",
  "target_url": "https://aicompleta.com/promo"
}
```

**Resposta:**
```json
{
  "success": true,
  "qrcode": {
    "id": "uuid",
    "qr_id": "PROMO001",
    "name": "Promoção Instagram",
    "target_url": "https://aicompleta.com/promo",
    "created_at": "2025-10-18T10:00:00"
  }
}
```

#### `GET /admin/scans`
Lista escaneamentos registrados.

**Parâmetros:**
- `qr_id` (opcional): Filtrar por QR Code específico
- `limit` (opcional): Limite de resultados (padrão: 100)

**Resposta:**
```json
{
  "success": true,
  "count": 15,
  "scans": [
    {
      "id": "uuid",
      "qr_id": "PROMO001",
      "source": "instagram",
      "scanned_at": "2025-10-18T14:30:00",
      "scanner_ip": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "device_type": "Mobile"
    }
  ]
}
```

#### `GET /admin/stats`
Retorna estatísticas de escaneamento.

**Parâmetros:**
- `qr_id` (opcional): Estatísticas de QR Code específico

**Resposta:**
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

#### `DELETE /admin/qrcodes/<qr_id>`
Desativa um QR Code (soft delete).

**Resposta:**
```json
{
  "success": true,
  "message": "QR Code deleted successfully"
}
```

## 🎨 Geração de QR Codes

### Script Python

O sistema inclui um script completo para geração de QR Codes:

```bash
cd scripts

# Gerar um único QR Code
python generate_qrcode.py \
  --qr-id PROMO001 \
  --base-url https://track.aicompleta.com \
  --source instagram

# Gerar múltiplos QR Codes
python generate_qrcode.py \
  --batch PROMO001,PROMO002,PROMO003 \
  --base-url https://track.aicompleta.com

# Com opções personalizadas
python generate_qrcode.py \
  --qr-id PROMO001 \
  --base-url https://track.aicompleta.com \
  --output ./qrcodes/promo.png \
  --size 15 \
  --border 2
```

### Opções do Gerador

- `--qr-id`: ID único do QR Code
- `--batch`: Lista de IDs separados por vírgula
- `--base-url`: URL base do sistema (obrigatório)
- `--source`: Origem/fonte do QR Code
- `--output`: Caminho do arquivo de saída
- `--output-dir`: Diretório para QR Codes em lote
- `--size`: Tamanho do QR Code (1-40, padrão: 10)
- `--border`: Largura da borda (padrão: 4)

## 🗄️ Estrutura do Banco de Dados

### Tabela `qrcodes`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| qr_id | VARCHAR | ID do QR Code (único) |
| name | VARCHAR | Nome descritivo |
| target_url | TEXT | URL de destino |
| created_at | TIMESTAMP | Data de criação |
| updated_at | TIMESTAMP | Data de atualização |
| is_active | BOOLEAN | Status ativo/inativo |

### Tabela `scans`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único |
| qr_id | VARCHAR | ID do QR Code |
| source | VARCHAR | Origem do escaneamento |
| scanned_at | TIMESTAMP | Data/hora do escaneamento |
| scanner_ip | VARCHAR | IP do scanner |
| user_agent | TEXT | User-Agent do dispositivo |
| referer | TEXT | URL de referência |
| country | VARCHAR | País (futuro) |
| city | VARCHAR | Cidade (futuro) |
| device_type | VARCHAR | Tipo de dispositivo |

## 🔒 Segurança

### API Key
Todos os endpoints administrativos requerem autenticação via API Key:

```bash
curl -H "X-API-Key: sua-api-key" \
  https://track.aicompleta.com/admin/qrcodes
```

### Variáveis de Ambiente
Configure as seguintes variáveis no arquivo `.env`:

```env
SECRET_KEY=seu-secret-key-seguro
API_KEY=sua-api-key-segura
ADMIN_USERNAME=admin
ADMIN_PASSWORD=senha-segura
```

### Boas Práticas
- ✅ Use HTTPS em produção
- ✅ Altere as credenciais padrão
- ✅ Mantenha as chaves de API seguras
- ✅ Configure CORS adequadamente
- ✅ Use PostgreSQL em produção

## 🌐 Deploy em Produção

### Opção 1: Docker + Nginx

```bash
# 1. Configurar variáveis de ambiente
cp backend/.env.example backend/.env
# Editar .env com credenciais de produção

# 2. Iniciar serviços
docker-compose up -d

# 3. Verificar status
docker-compose ps
```

### Opção 2: Servidor VPS

```bash
# 1. Instalar dependências
sudo apt update
sudo apt install python3-pip postgresql nginx

# 2. Configurar PostgreSQL
sudo -u postgres createdb qrcode_tracking
sudo -u postgres psql qrcode_tracking < database/schema.sql

# 3. Instalar aplicação
cd backend
pip install -r requirements.txt

# 4. Configurar systemd
sudo cp qrcode-tracking.service /etc/systemd/system/
sudo systemctl enable qrcode-tracking
sudo systemctl start qrcode-tracking

# 5. Configurar Nginx
sudo cp nginx.conf /etc/nginx/sites-available/qrcode-tracking
sudo ln -s /etc/nginx/sites-available/qrcode-tracking /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

### Opção 3: Plataforma Cloud (Heroku, Railway, Render)

O sistema é compatível com plataformas cloud que suportam Docker ou Python.

## 📊 Casos de Uso

### Marketing Digital
- Rastrear campanhas em diferentes canais (Instagram, Facebook, Email)
- Medir efetividade de anúncios físicos
- Analisar conversões por origem

### Eventos
- Registrar check-ins de participantes
- Rastrear materiais distribuídos
- Coletar dados de engajamento

### Produtos
- Autenticação de produtos
- Rastreamento de distribuição
- Suporte ao cliente

### Educação
- Rastreamento de materiais didáticos
- Registro de acesso a conteúdos
- Análise de engajamento estudantil

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
qrcode-tracking-system/
├── backend/
│   ├── app.py              # Aplicação Flask principal
│   ├── models.py           # Modelos de dados
│   ├── config.py           # Configurações
│   ├── requirements.txt    # Dependências Python
│   ├── Dockerfile          # Container Docker
│   └── .env.example        # Exemplo de configuração
├── database/
│   └── schema.sql          # Schema do banco de dados
├── frontend/
│   └── index.html          # Interface web
├── scripts/
│   └── generate_qrcode.py  # Gerador de QR Codes
├── docker-compose.yml      # Orquestração Docker
├── nginx.conf              # Configuração Nginx
└── README.md               # Documentação
```

### Testes

```bash
# Testar endpoint de rastreamento
curl "http://localhost:5000/track?qr_id=DEMO001&source=test"

# Testar API administrativa
curl -H "X-API-Key: admin-api-key" \
  http://localhost:5000/admin/qrcodes

# Criar novo QR Code
curl -X POST \
  -H "X-API-Key: admin-api-key" \
  -H "Content-Type: application/json" \
  -d '{"qr_id":"TEST001","name":"Teste","target_url":"https://example.com"}' \
  http://localhost:5000/admin/qrcodes
```

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

## 📧 Suporte

Para suporte, entre em contato através de [seu-email@example.com]

---

**Desenvolvido com ❤️ para AICompleta**

