# 🚀 Guia de Instalação e Deploy

Este guia detalha como instalar e fazer o deploy do Sistema de Rastreamento de QR Codes em diferentes ambientes.

## 📋 Pré-requisitos

### Desenvolvimento Local
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Git

### Produção
- Servidor Linux (Ubuntu 20.04+ recomendado)
- Docker e Docker Compose (recomendado)
- PostgreSQL 13+ (se não usar Docker)
- Nginx (se não usar Docker)
- Domínio configurado (ex: track.aicompleta.com)

## 🔧 Instalação Local (Desenvolvimento)

### 1. Clonar o Repositório

```bash
git clone https://github.com/pedrobatistellabit/qrcode-tracking-system.git
cd qrcode-tracking-system
```

### 2. Configurar Ambiente Virtual Python

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
nano .env
```

Configuração mínima para desenvolvimento:
```env
SECRET_KEY=dev-secret-key
DEBUG=True
DATABASE_TYPE=sqlite
SQLITE_DB_PATH=qrcode_tracking.db
API_KEY=seu-api-key-aqui
BASE_URL=http://localhost:5000
```

### 5. Iniciar Servidor

```bash
python app.py
```

O servidor estará disponível em `http://localhost:5000`

### 6. Testar Instalação

```bash
# Em outro terminal
curl http://localhost:5000/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T..."
}
```

## 🐳 Deploy com Docker (Recomendado)

### 1. Instalar Docker e Docker Compose

```bash
# Ubuntu
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
```

### 2. Configurar Variáveis de Ambiente

```bash
cd qrcode-tracking-system
cp backend/.env.example backend/.env
nano backend/.env
```

Configuração para produção:
```env
SECRET_KEY=seu-secret-key-super-seguro-aqui
DEBUG=False
DATABASE_TYPE=postgresql
DB_HOST=postgres
DB_PORT=5432
DB_NAME=qrcode_tracking
DB_USER=postgres
DB_PASSWORD=senha-segura-aqui
API_KEY=sua-api-key-segura-aqui
BASE_URL=https://track.aicompleta.com
CORS_ORIGINS=https://aicompleta.com,https://track.aicompleta.com
```

### 3. Iniciar Serviços

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f backend

# Verificar status
docker-compose ps
```

### 4. Verificar Instalação

```bash
curl http://localhost:5000/health
curl http://localhost/  # Nginx
```

## 🌐 Deploy em Servidor VPS (Sem Docker)

### 1. Preparar Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3-pip python3-venv postgresql nginx git
```

### 2. Configurar PostgreSQL

```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Criar banco de dados e usuário
CREATE DATABASE qrcode_tracking;
CREATE USER qrcode_user WITH PASSWORD 'senha-segura';
GRANT ALL PRIVILEGES ON DATABASE qrcode_tracking TO qrcode_user;
\q

# Importar schema
sudo -u postgres psql qrcode_tracking < database/schema.sql
```

### 3. Configurar Aplicação

```bash
# Criar usuário para aplicação
sudo useradd -m -s /bin/bash qrcode
sudo su - qrcode

# Clonar repositório
git clone https://github.com/pedrobatistellabit/qrcode-tracking-system.git
cd qrcode-tracking-system/backend

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn

# Configurar .env
cp .env.example .env
nano .env
```

### 4. Configurar Systemd Service

```bash
# Sair do usuário qrcode
exit

# Criar arquivo de serviço
sudo nano /etc/systemd/system/qrcode-tracking.service
```

Conteúdo do arquivo:
```ini
[Unit]
Description=QR Code Tracking System
After=network.target postgresql.service

[Service]
Type=notify
User=qrcode
Group=qrcode
WorkingDirectory=/home/qrcode/qrcode-tracking-system/backend
Environment="PATH=/home/qrcode/qrcode-tracking-system/backend/venv/bin"
ExecStart=/home/qrcode/qrcode-tracking-system/backend/venv/bin/gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/qrcode-tracking/access.log \
    --error-logfile /var/log/qrcode-tracking/error.log \
    app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Criar diretório de logs
sudo mkdir -p /var/log/qrcode-tracking
sudo chown qrcode:qrcode /var/log/qrcode-tracking

# Habilitar e iniciar serviço
sudo systemctl enable qrcode-tracking
sudo systemctl start qrcode-tracking
sudo systemctl status qrcode-tracking
```

### 5. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/qrcode-tracking
```

Conteúdo do arquivo:
```nginx
server {
    listen 80;
    server_name track.aicompleta.com;

    # Frontend estático
    location / {
        root /home/qrcode/qrcode-tracking-system/frontend;
        index index.html dashboard.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /track {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:5000;
    }

    # Logs
    access_log /var/log/nginx/qrcode-tracking-access.log;
    error_log /var/log/nginx/qrcode-tracking-error.log;
}
```

```bash
# Habilitar site
sudo ln -s /etc/nginx/sites-available/qrcode-tracking /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Configurar SSL com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d track.aicompleta.com

# Renovação automática já está configurada
sudo certbot renew --dry-run
```

## ☁️ Deploy em Plataformas Cloud

### Heroku

```bash
# Instalar Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Criar app
heroku create qrcode-tracking-app

# Adicionar PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Configurar variáveis de ambiente
heroku config:set SECRET_KEY=seu-secret-key
heroku config:set API_KEY=sua-api-key
heroku config:set DATABASE_TYPE=postgresql

# Deploy
git push heroku main

# Executar migrations
heroku run python -c "from models import Database; Database()"
```

### Railway

1. Acesse [railway.app](https://railway.app)
2. Conecte seu repositório GitHub
3. Adicione PostgreSQL database
4. Configure variáveis de ambiente
5. Deploy automático

### Render

1. Acesse [render.com](https://render.com)
2. New → Web Service
3. Conecte repositório GitHub
4. Configure:
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && gunicorn app:app`
5. Adicione PostgreSQL database
6. Configure variáveis de ambiente

## 🔒 Configurações de Segurança

### 1. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### 2. Fail2Ban

```bash
# Instalar
sudo apt install fail2ban

# Configurar
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Backup Automático

```bash
# Criar script de backup
sudo nano /usr/local/bin/backup-qrcode-db.sh
```

Conteúdo:
```bash
#!/bin/bash
BACKUP_DIR="/backup/qrcode-tracking"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump -U qrcode_user qrcode_tracking | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
```

```bash
# Tornar executável
sudo chmod +x /usr/local/bin/backup-qrcode-db.sh

# Adicionar ao cron (diariamente às 2h)
sudo crontab -e
# Adicionar linha:
0 2 * * * /usr/local/bin/backup-qrcode-db.sh
```

## 📊 Monitoramento

### Logs

```bash
# Docker
docker-compose logs -f backend

# Systemd
sudo journalctl -u qrcode-tracking -f

# Nginx
sudo tail -f /var/log/nginx/qrcode-tracking-access.log
```

### Health Check

```bash
# Criar script de monitoramento
nano monitor.sh
```

```bash
#!/bin/bash
URL="https://track.aicompleta.com/health"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ $STATUS -eq 200 ]; then
    echo "✓ Sistema online"
else
    echo "✗ Sistema offline - Status: $STATUS"
    # Enviar alerta (email, Slack, etc)
fi
```

## 🔄 Atualização

```bash
# Docker
cd qrcode-tracking-system
git pull
docker-compose down
docker-compose build
docker-compose up -d

# Systemd
cd qrcode-tracking-system
git pull
sudo systemctl restart qrcode-tracking
```

## 🆘 Troubleshooting

### Problema: Banco de dados não conecta

```bash
# Verificar PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"

# Verificar credenciais no .env
cat backend/.env | grep DB_
```

### Problema: Porta 5000 já em uso

```bash
# Encontrar processo
sudo lsof -i :5000

# Matar processo
sudo kill -9 <PID>
```

### Problema: Permissões negadas

```bash
# Corrigir permissões
sudo chown -R qrcode:qrcode /home/qrcode/qrcode-tracking-system
chmod +x scripts/generate_qrcode.py
```

## 📞 Suporte

Para problemas ou dúvidas:
- GitHub Issues: https://github.com/pedrobatistellabit/qrcode-tracking-system/issues
- Email: suporte@aicompleta.com

---

**Última atualização**: 18/10/2025

