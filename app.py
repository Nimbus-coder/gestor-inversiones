import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from bonos import obtener_cashflow

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Mi Portfolio PRO", layout="wide")

# Título y Diseño
st.markdown("Controlá tus Acciones Argentinas (.BA) y CEDEARs en tiempo real.")
st.title("🚀 Mi Gestor de Inversiones")

def obtener_dolares():
    try:
        # Consultamos la API que ya nos da todos los tipos de cambio
        response = requests.get("https://dolarapi.com/v1/dolares", timeout=10)
        datos = response.json()
        
        # Transformamos la lista en un diccionario fácil de usar
        return {d['casa']: d['venta'] for d in datos}
        return precios
    except Exception as e:
        st.error(f"Error al conectar  con la API de dólares: {e}")
        return None

# --- PANEL DE COTIZACIONES ---
dolares = obtener_dolares()

if dolares:
    # Creamos 5 columnas para que entren todos los dólares
    c1, c2, c3, c4, c5 = st.columns(5)
    
    # Mostramos cada uno con su precio de venta
    c1.metric("Oficial", f"${dolares.get('oficial', 0):,.2f}")
    c2.metric("MEP", f"${dolares.get('mep', 0):,.2f}")
    c3.metric("CCL", f"${dolares.get('ccl', 0):,.2f}")
    c4.metric("Blue", f"${dolares.get('blue', 0):,.2f}")
    c5.metric("Tarjeta", f"${dolares.get('tarjeta', 0):,.2f}")
    st.divider()

def obtener_precio_rava(ticker_buscado):
    try:
        url = "https://www.rava.com/cotizaciones/bonos"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Rava pone los datos en un div con id 'cotizaciones' o una tabla
            tabla = soup.find('table') 
            if not tabla:
                return None
                
            filas = tabla.find_all('tr')
            for fila in filas:
                celdas = [td.text.strip() for td in fila.find_all('td')]
                
                # Verificamos si el ticker está en la fila
                if celdas and ticker_buscado == celdas[0]:
                    # Buscamos el primer valor que parezca un número en las siguientes celdas
                    for valor in celdas[1:5]: # Revisamos las primeras columnas de precios
                        if valor and ',' in valor:
                            precio_f = float(valor.replace('.', '').replace(',', '.'))
                            return precio_f
        return None
    except Exception as e:
        return None

# --- BARRA LATERAL (Donde cargamos datos) ---
# --- BARRA LATERAL (Carga de Datos) ---
with st.sidebar:
    st.header("📥 Cargar Operación")
    tipo_activo = st.radio("Seleccionar tipo:", ["Acciones/CEDEARs", "Bonos/ONs"])
    st.divider()

    if tipo_activo == "Acciones/CEDEARs":
        ticker = st.text_input("Ticker (ej: GGAL.BA)", value="GGAL.BA").upper()
        cantidad = st.number_input("Cantidad", min_value=1, value=10)
        p_compra = st.number_input("Precio de Compra (ARS)", min_value=0.0, value=1000.0)

        if st.button("Agregar a Cartera"):
            if 'portfolio' not in st.session_state:
                st.session_state['portfolio'] = []
            st.session_state['portfolio'].append({"Ticker": ticker, "Cantidad": cantidad, "Precio Compra": p_compra})
            st.success(f"✅ {ticker} Agregado!")
            st.rerun()

    else: # MODO BONOS
        t_bono = st.text_input("Ticker Bono (ej: AL30D.BA)", key="t_bono_sidebar").upper()
        vn_bono = st.number_input("Valor Nominal (V.N.)", min_value=1, value=1000, key="vn_sidebar")
        p_bono = st.number_input("Precio Compra USD", min_value=0.0, value=50.0, key="p_sidebar")

        if st.button("Guardar Bono"):
            if 'portfolio_bonos' not in st.session_state:
                st.session_state['portfolio_bonos'] = []
            st.session_state['portfolio_bonos'].append({"Ticker": t_bono, "Nominales": vn_bono, "Precio Compra": p_bono})
            st.success(f"✅ Bono {t_bono} guardado!")
            st.rerun()

    st.divider()
    st.header("🗑️ Gestión de Salida")
    if st.button("💣 Resetear Todo"):
        st.session_state.clear()
        st.rerun()

# --- PANTALLA PRINCIPAL ---
# Verificamos si hay algo cargado en cualquiera de las dos carteras
hay_acciones = 'portfolio' in st.session_state and len(st.session_state['portfolio']) > 0
hay_bonos = 'portfolio_bonos' in st.session_state and len(st.session_state['portfolio_bonos']) > 0

if hay_acciones or hay_bonos:
    tab_acciones, tab_bonos = st.tabs(["📈 Acciones y CEDEARs", "🏦 Renta Fija (Bonos/ONs)"])

    with tab_acciones:
        if hay_acciones:
            lista_resultados = []
            total_invertido = 0
            total_actual = 0
            for item in st.session_state['portfolio']:
                try:
                    stock = yf.Ticker(item['Ticker'])
                    precio_hoy = stock.history(period="1d")['Close'].iloc[0]
                    val_actual = precio_hoy * item['Cantidad']
                    val_compra = item['Precio Compra'] * item['Cantidad']
                    lista_resultados.append({
                        "Ticker": item['Ticker'], "Cantidad": item['Cantidad'],
                        "Precio Hoy": precio_hoy, "Invertido ($)": val_compra,
                        "Valor Hoy ($)": val_actual, "Rendimiento (%)": ((val_actual-val_compra)/val_compra)*100
                    })
                    total_invertido += val_compra
                    total_actual += val_actual
                except: st.error(f"Error con {item['Ticker']}")
            
                df_acc = pd.DataFrame(lista_resultados)
                st.metric("Resultado Global", f"$ {total_actual:,.0f}", delta=f"${total_actual-total_invertido:,.0f}")
                st.dataframe(df_acc, use_container_width=True)
                st.bar_chart(df_acc.set_index("Ticker")["Valor Hoy ($)"])
        else:
            st.info("No hay acciones cargadas.")

    with tab_bonos:
        if hay_bonos:
            for bono in st.session_state['portfolio_bonos']:
                with st.expander(f"📌 {bono['Ticker']}", expanded=True):
                    # Usamos el precio que vos cargaste manualmente en la barra lateral
                    p_base = bono['Precio Compra'] 
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Precio Compra (USD)", f"$ {p_base:,.2f}")
                    c2.metric("V.N. Poseído", bono['Nominales'])
                    c3.metric("Paridad Ref.", f"{(p_base/100)*100:.1f}%")

                    # --- El Cashflow que ya tenés en bonos.py ---
                    cronograma = obtener_cashflow(bono['Ticker'])
                    if cronograma:
                        st.write("---")
                        st.write("📅 **Flujo de Fondos Proyectado (USD):**")
                        
                        pagos_v_n = []
                        for p in cronograma:
                            # Calculamos el cobro según tus nominales
                            monto = (bono['Nominales'] / 100) * p['cupon']
                            pagos_v_n.append({
                                "Fecha": p['fecha'], 
                                "Cobro Estimado (USD)": f"{monto:.2f}"
                            })
                        st.table(pagos_v_n)
                    else:
                        st.warning("Cargá este ticker en bonos.py para ver los pagos.")
        else:
            st.info("Cargá un bono en la barra lateral para empezar.")
else:
    st.info("👈 Cargá tu primer activo en la barra lateral para empezar.")






















































