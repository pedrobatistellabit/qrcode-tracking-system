"""
Modelos de dados para o sistema de rastreamento de QR Codes
"""
import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import json


class Database:
    """Gerenciador de conexão com banco de dados SQLite"""
    
    def __init__(self, db_path: str = 'qrcode_tracking.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de QR Codes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qrcodes (
                id TEXT PRIMARY KEY,
                qr_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                target_url TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Tabela de Escaneamentos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY,
                qr_id TEXT NOT NULL,
                source TEXT,
                scanned_at TEXT DEFAULT CURRENT_TIMESTAMP,
                scanner_ip TEXT,
                user_agent TEXT,
                referer TEXT,
                country TEXT,
                city TEXT,
                device_type TEXT,
                FOREIGN KEY (qr_id) REFERENCES qrcodes(qr_id) ON DELETE CASCADE
            )
        ''')
        
        # Índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scans_qr_id ON scans(qr_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scans_scanned_at ON scans(scanned_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_qrcodes_qr_id ON qrcodes(qr_id)')
        
        conn.commit()
        conn.close()


class QRCode:
    """Modelo para QR Codes"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, qr_id: str, name: str, target_url: str) -> Dict:
        """Cria um novo QR Code"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO qrcodes (id, qr_id, name, target_url, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (id, qr_id, name, target_url, created_at, created_at))
            
            conn.commit()
            
            return {
                'id': id,
                'qr_id': qr_id,
                'name': name,
                'target_url': target_url,
                'created_at': created_at,
                'is_active': True
            }
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def get_by_qr_id(self, qr_id: str) -> Optional[Dict]:
        """Busca um QR Code pelo qr_id"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM qrcodes WHERE qr_id = ? AND is_active = 1', (qr_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all(self) -> List[Dict]:
        """Retorna todos os QR Codes"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM qrcodes ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update(self, qr_id: str, **kwargs) -> bool:
        """Atualiza um QR Code"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        kwargs['updated_at'] = datetime.utcnow().isoformat()
        
        set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
        values = list(kwargs.values()) + [qr_id]
        
        cursor.execute(f'UPDATE qrcodes SET {set_clause} WHERE qr_id = ?', values)
        conn.commit()
        
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    def delete(self, qr_id: str) -> bool:
        """Desativa um QR Code (soft delete)"""
        return self.update(qr_id, is_active=0)


class Scan:
    """Modelo para Escaneamentos"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, qr_id: str, source: str = None, scanner_ip: str = None,
               user_agent: str = None, referer: str = None, country: str = None,
               city: str = None, device_type: str = None) -> Dict:
        """Registra um novo escaneamento"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        id = str(uuid.uuid4())
        scanned_at = datetime.utcnow().isoformat()
        
        cursor.execute('''
            INSERT INTO scans (id, qr_id, source, scanned_at, scanner_ip, user_agent, 
                             referer, country, city, device_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id, qr_id, source, scanned_at, scanner_ip, user_agent, referer, 
              country, city, device_type))
        
        conn.commit()
        conn.close()
        
        return {
            'id': id,
            'qr_id': qr_id,
            'source': source,
            'scanned_at': scanned_at,
            'scanner_ip': scanner_ip,
            'user_agent': user_agent
        }
    
    def get_by_qr_id(self, qr_id: str, limit: int = 100) -> List[Dict]:
        """Retorna escaneamentos de um QR Code específico"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM scans 
            WHERE qr_id = ? 
            ORDER BY scanned_at DESC 
            LIMIT ?
        ''', (qr_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_all(self, limit: int = 100) -> List[Dict]:
        """Retorna todos os escaneamentos"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM scans ORDER BY scanned_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self, qr_id: str = None) -> Dict:
        """Retorna estatísticas de escaneamento"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if qr_id:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_scans,
                    COUNT(DISTINCT scanner_ip) as unique_scanners,
                    MAX(scanned_at) as last_scan,
                    MIN(scanned_at) as first_scan
                FROM scans
                WHERE qr_id = ?
            ''', (qr_id,))
        else:
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_scans,
                    COUNT(DISTINCT scanner_ip) as unique_scanners,
                    MAX(scanned_at) as last_scan,
                    MIN(scanned_at) as first_scan
                FROM scans
            ''')
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {}

