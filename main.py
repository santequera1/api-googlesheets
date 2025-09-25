from fastapi import FastAPI
from pydantic import BaseModel
from googleapiclient.discovery import build
from google.oauth2 import service_account
from typing import Optional

app = FastAPI()

# ID de la hoja
SPREADSHEET_ID = "1SKHZBmxEsZgKjoEx_p5QtyOy21Z0o9twIsWWlICmuzE"

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
    categoria: Optional[str] = ""


@app.post("/agregar")
def agregar_transaccion(data: Transaccion):
    hoja = service.spreadsheets()

    # Selección de hoja según el tipo
    if data.tipo.lower() == "entrante":
        sheet_name = "Entradas"
    elif data.tipo.lower() == "saliente":
        sheet_name = "Salidas"
    else:
        return {"status": "error", "message": "El campo 'tipo' debe ser 'entrante' o 'saliente'"}

    # Rango a partir de la fila 2 (porque A1:D1 son los headers)
    rango = f"{sheet_name}!A2:D"

    # Valores a insertar como fila nueva
    valores = [[
        data.fecha,
        data.importe,
        data.descripcion,
        data.categoria or ""
    ]]

    hoja.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=rango,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": valores}
    ).execute()

    return {"status": "ok", "hoja": sheet_name, "inserted": valores}
