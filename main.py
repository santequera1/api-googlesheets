from fastapi import FastAPI
from pydantic import BaseModel
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime
from typing import Optional


app = FastAPI()

# ID de la hoja
SPREADSHEET_ID = "1SKHZBmxEsZgKjoEx_p5QtyOy21Z0o9twIsWWlICmuzE"
SHEET_NAME = "Transacciones"

# Credenciales (usa un service account en vez de OAuth normal)
SERVICE_ACCOUNT_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("sheets", "v4", credentials=creds)


class Transaccion(BaseModel):
    tipo: str   # "entrante" o "saliente"
    fecha: str
    importe: float
    descripcion: str
    categoria: Optional[str] = None

@app.post("/agregar")
def agregar_transaccion(data: Transaccion):
    hoja = service.spreadsheets()

    if data.tipo == "entrante":
        # Se guarda en "Ganancias" -> columnas G:J
        rango = f"{SHEET_NAME}!G4:J"
    else:
        # Se guarda en "Gastos" -> columnas B:E
        rango = f"{SHEET_NAME}!B4:E"

    # Valores a insertar como fila nueva
    valores = [[
        data.fecha,
        data.importe,
        data.descripcion,
        data.categoria
    ]]

    hoja.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=rango,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": valores}
    ).execute()

    return {"status": "ok", "inserted": valores}
