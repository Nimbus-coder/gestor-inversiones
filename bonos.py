# --- Base de Datos de Flujo de Fondos (Cashflow) ---

CALENDARIO_PAGOS = {
    "AL30": [
        {"fecha": "2026-07-09", "cupon": 4.25}, # Interés + Amortización
        {"fecha": "2027-01-09", "cupon": 4.25},
        {"fecha": "2027-07-09", "cupon": 4.25},
        {"fecha": "2028-01-09", "cupon": 4.25},
    ],
    "AL30D": [
        {"fecha": "2026-07-09", "cupon": 4.25},
        {"fecha": "2027-01-09", "cupon": 4.25},
        {"fecha": "2027-07-09", "cupon": 4.25},
    ],
    "GD30": [
        {"fecha": "2026-07-09", "cupon": 4.0},
        {"fecha": "2027-01-09", "cupon": 4.0},
    ],
    "GD35": [
        {"fecha": "2026-07-09", "cupon": 4.125},
        {"fecha": "2027-01-09", "cupon": 4.125},
    ]
}

def obtener_cashflow(ticker):
    """Retorna la lista de pagos para un ticker dado o una lista vacía si no existe."""

    return CALENDARIO_PAGOS.get(ticker, [])

mep_hoy = dolares.get('mep', 1) # Si no hay MEP, usamos 1 para no romper la cuenta
valor_pesos = p_base * mep_hoy
st.write(f"💰 Valor estimado en pesos: **${valor_pesos:,.2f}**")
