-- Schema para Sistema de Rastreamento de QR Codes
-- Database: qrcode_tracking

-- Extensão para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de QR Codes
CREATE TABLE IF NOT EXISTS qrcodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    qr_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    target_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabela de Escaneamentos
CREATE TABLE IF NOT EXISTS scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    qr_id VARCHAR(100) NOT NULL,
    source VARCHAR(255),
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scanner_ip VARCHAR(45),
    user_agent TEXT,
    referer TEXT,
    country VARCHAR(100),
    city VARCHAR(100),
    device_type VARCHAR(50),
    FOREIGN KEY (qr_id) REFERENCES qrcodes(qr_id) ON DELETE CASCADE
);

-- Índices para melhor performance
CREATE INDEX idx_scans_qr_id ON scans(qr_id);
CREATE INDEX idx_scans_scanned_at ON scans(scanned_at);
CREATE INDEX idx_qrcodes_qr_id ON qrcodes(qr_id);
CREATE INDEX idx_scans_source ON scans(source);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_qrcodes_updated_at BEFORE UPDATE ON qrcodes
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View para estatísticas de escaneamento
CREATE OR REPLACE VIEW scan_statistics AS
SELECT 
    q.qr_id,
    q.name,
    q.target_url,
    COUNT(s.id) as total_scans,
    COUNT(DISTINCT s.scanner_ip) as unique_scanners,
    MAX(s.scanned_at) as last_scan,
    MIN(s.scanned_at) as first_scan
FROM qrcodes q
LEFT JOIN scans s ON q.qr_id = s.qr_id
GROUP BY q.qr_id, q.name, q.target_url;

-- Dados de exemplo (opcional)
INSERT INTO qrcodes (qr_id, name, target_url) VALUES
    ('DEMO001', 'QR Code Demo 1', 'https://aicompleta.com'),
    ('DEMO002', 'QR Code Demo 2', 'https://aicompleta.com/sobre')
ON CONFLICT (qr_id) DO NOTHING;

