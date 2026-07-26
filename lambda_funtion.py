import json
import boto3
import os
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    }

    # Manejar petición 'Preflight' CORS del navegador
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    bucket_name = os.environ.get('BUCKET_NAME')
    file_key = 'accesos.log'
    
    # Extraer IP del cliente
    ip_acceso = 'Desconocida'
    if event and 'requestContext' in event and 'http' in event['requestContext']:
        ip_acceso = event['requestContext']['http'].get('sourceIp', 'Desconocida')
    elif event and 'headers' in event and 'x-forwarded-for' in event['headers']:
        ip_acceso = event['headers']['x-forwarded-for'].split(',')[0].strip()
        
    hora_acceso = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    nueva_linea = f"IP: {ip_acceso} | Fecha/Hora: {hora_acceso}\n"
    
    # Leer archivo actual en S3
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        contenido_actual = response['Body'].read().decode('utf-8')
    except Exception:
        contenido_actual = ""
        
    # Guardar archivo actualizado
    contenido_actualizado = contenido_actual + nueva_linea
    
    s3.put_object(
        Bucket=bucket_name,
        Key=file_key,
        Body=contenido_actualizado.encode('utf-8'),
        ContentType='text/plain'
    )
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'Acceso registrado', 'ip': ip_acceso, 'timestamp': hora_acceso})
    }
