from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
import boto3

app = FastAPI(title="Practica 4 - Mostrador")

REGION = "us-east-1"
DYNAMO_TABLE_NAME = "boletines_recibidos"

dynamo_client = boto3.resource('dynamodb', region_name=REGION)

def get_boletin(boletin_id: str):
    tabla = dynamo_client.Table(DYNAMO_TABLE_NAME)
    response = tabla.get_item(Key={'id': boletin_id})
    return response.get('Item')

def marcar_como_leido(boletin_id: str):
    tabla = dynamo_client.Table(DYNAMO_TABLE_NAME)
    tabla.update_item(
        Key={'id': boletin_id},
        UpdateExpression="SET leido = :val",
        ExpressionAttributeValues={':val': True}
    )

@app.get("/boletines/{boletinID}", response_class=HTMLResponse)
def mostrar_boletin(boletinID: str, correo: str):

    item = get_boletin(boletinID)
    
    if not item or item.get('correo') != correo:
        raise HTTPException(status_code=404, detail="Boletín no encontrado o correo inválido")
    
    marcar_como_leido(boletinID)
    
    imagen_url = item.get('imagen_s3')
    contenido = item.get('contenido', 'Sin texto')
    
    html_content = f"""
    <html>
        <head>
            <title>Tu Boletín</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }}
                img {{ max-width: 400px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}
                .btn {{ display: inline-block; margin-top: 20px; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>¡Aquí tienes tu Boletín!</h1>
            <p><strong>Mensaje:</strong> {contenido}</p>
            <img src="{imagen_url}" alt="Imagen del boletin" />
            <br>
            <a class="btn" href="{imagen_url}" target="_blank">Ver archivo original en S3</a>
        </body>
    </html>
    """
    return html_content