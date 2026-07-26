import json
import boto3
import os
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    file_key = 'accesos.log'
    
    # Extraer la IP del cliente que llama al endpoint
    ip_acceso = 'Desconocida'
    if 'requestContext' in event and 'http' in event['requestContext']:
        ip_acceso = event['requestContext']['http'].get('sourceIp', 'Desconocida')
    elif 'headers' in event and 'x-forwarded-for' in event['headers']:
        ip_acceso = event['headers']['x-forwarded-for'].split(',')[0].strip()
        
    hora_acceso = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    nueva_linea = f"IP: {ip_acceso} | Fecha/Hora: {hora_acceso}\n"
    
    # Leer el contenido actual de accesos.log desde S3
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        contenido_actual = response['Body'].read().decode('utf-8')
    except Exception:
        contenido_actual = ""
        
    # Añadir el registro y actualizar en S3
    contenido_actualizado = contenido_actual + nueva_linea
    
    s3.put_object(
        Bucket=bucket_name,
        Key=file_key,
        Body=contenido_actualizado.encode('utf-8'),
        ContentType='text/plain'
    )
    
    # Respuesta con cabeceras CORS
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': '*'
        },
        'body': json.dumps({'message': 'Acceso registrado correctamente', 'ip': ip_acceso, 'timestamp': hora_acceso})
    }