#!/usr/bin/env python3
"""
Gerador de QR Codes para o Sistema de Rastreamento
"""
import qrcode
import argparse
import sys
import os
from pathlib import Path


def generate_qrcode(qr_id: str, base_url: str, source: str = None, 
                   output_path: str = None, size: int = 10, border: int = 4):
    """
    Gera um QR Code para rastreamento
    
    Args:
        qr_id: Identificador único do QR Code
        base_url: URL base do sistema (ex: https://track.aicompleta.com)
        source: Origem/fonte do QR Code (opcional)
        output_path: Caminho para salvar a imagem (opcional)
        size: Tamanho do QR Code (1-40, padrão: 10)
        border: Largura da borda (padrão: 4)
    """
    # Construir URL de rastreamento
    tracking_url = f"{base_url}/track?qr_id={qr_id}"
    
    if source:
        tracking_url += f"&source={source}"
    
    # Configurar QR Code
    qr = qrcode.QRCode(
        version=1,  # Tamanho automático
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta correção de erros
        box_size=size,
        border=border,
    )
    
    # Adicionar dados
    qr.add_data(tracking_url)
    qr.make(fit=True)
    
    # Criar imagem
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Definir caminho de saída
    if not output_path:
        output_path = f"qrcode_{qr_id}.png"
    
    # Salvar imagem
    img.save(output_path)
    
    print(f"✓ QR Code gerado com sucesso!")
    print(f"  ID: {qr_id}")
    print(f"  URL: {tracking_url}")
    print(f"  Arquivo: {output_path}")
    
    return output_path


def generate_batch_qrcodes(qr_ids: list, base_url: str, source: str = None, 
                          output_dir: str = "qrcodes"):
    """
    Gera múltiplos QR Codes em lote
    
    Args:
        qr_ids: Lista de IDs de QR Codes
        base_url: URL base do sistema
        source: Origem comum (opcional)
        output_dir: Diretório de saída
    """
    # Criar diretório se não existir
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"Gerando {len(qr_ids)} QR Codes...")
    
    for i, qr_id in enumerate(qr_ids, 1):
        output_path = os.path.join(output_dir, f"qrcode_{qr_id}.png")
        generate_qrcode(qr_id, base_url, source, output_path)
        print(f"  [{i}/{len(qr_ids)}] {qr_id}")
    
    print(f"\n✓ {len(qr_ids)} QR Codes gerados em: {output_dir}/")


def main():
    parser = argparse.ArgumentParser(
        description='Gerador de QR Codes para Sistema de Rastreamento',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Gerar um único QR Code
  python generate_qrcode.py --qr-id PROMO001 --base-url https://track.aicompleta.com

  # Gerar com origem específica
  python generate_qrcode.py --qr-id PROMO001 --base-url https://track.aicompleta.com --source instagram

  # Gerar múltiplos QR Codes
  python generate_qrcode.py --batch PROMO001,PROMO002,PROMO003 --base-url https://track.aicompleta.com

  # Especificar diretório de saída
  python generate_qrcode.py --qr-id PROMO001 --base-url https://track.aicompleta.com --output ./meus_qrcodes/promo.png
        """
    )
    
    parser.add_argument('--qr-id', type=str, help='ID único do QR Code')
    parser.add_argument('--batch', type=str, help='Lista de IDs separados por vírgula')
    parser.add_argument('--base-url', type=str, required=True, 
                       help='URL base do sistema (ex: https://track.aicompleta.com)')
    parser.add_argument('--source', type=str, help='Origem/fonte do QR Code')
    parser.add_argument('--output', type=str, help='Caminho do arquivo de saída')
    parser.add_argument('--output-dir', type=str, default='qrcodes', 
                       help='Diretório para QR Codes em lote (padrão: qrcodes)')
    parser.add_argument('--size', type=int, default=10, 
                       help='Tamanho do QR Code (1-40, padrão: 10)')
    parser.add_argument('--border', type=int, default=4, 
                       help='Largura da borda (padrão: 4)')
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not args.qr_id and not args.batch:
        parser.error('É necessário especificar --qr-id ou --batch')
    
    if args.qr_id and args.batch:
        parser.error('Não é possível usar --qr-id e --batch simultaneamente')
    
    try:
        if args.batch:
            # Modo em lote
            qr_ids = [qr_id.strip() for qr_id in args.batch.split(',')]
            generate_batch_qrcodes(qr_ids, args.base_url, args.source, args.output_dir)
        else:
            # Modo único
            generate_qrcode(args.qr_id, args.base_url, args.source, 
                          args.output, args.size, args.border)
    
    except Exception as e:
        print(f"✗ Erro ao gerar QR Code: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

