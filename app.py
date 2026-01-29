import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from bonos import obtener_cashflow

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Mi Portfolio PRO", layout="wide")

# Título y Diseño
st.title("🚀 Mi Gestor de Inversiones")
st.markdown("Controlá tus Acciones Argentinas (.BA) y CEDEARs en tiempo real.")

def obtener_precio_rava(ticker_buscado):
    try:
        url = "https://www.rava.com/cotizaciones/bonos"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Buscamos todas las filas de la tabla
            filas = soup.find_all('tr')
            
            for fila in filas:
                celdas = fila.find_all('td')
                if len(celdas) > 0:
                    # La primera celda suele ser el Ticker
                    ticker_tabla = celdas[0].text.strip()
                    
                    if ticker_tabla == ticker_buscado:
                        # La celda del precio suele ser la segunda o tercera (Cierre/Último)
                        # En Rava es la columna 'Último'
                        precio_raw = celdas[1].text.strip()
                        # Limpieza: 1.200,50 -> 1200.50
                        precio_f = float(precio_raw.replace('.', '').replace(',', '.'))
                        return precio_f
        return None
    except Exception as e:
        print(f"Error scraping Rava: {e}")
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
                # Mantenemos tu diseño de expander
                with st.expander(f"📌 {bono['Ticker']}", expanded=True):
                    try:
                        # --- 1. LLAMAMOS A RAVA EN LUGAR DE YAHOO ---
                        p_hoy = obtener_precio_rava(bono['Ticker'])
                        
                        if p_hoy:
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Precio Rava", f"$ {p_hoy:,.2f}")
                            c2.metric("V.N.", bono['Nominales'])
                            
                            paridad = (p_hoy / 100) * 100
                            c3.metric("Paridad", f"{paridad:.1f}%")

                            # --- 2. LLAMAMOS AL CASHFLOW DE bonos.py ---
                            cronograma = obtener_cashflow(bono['Ticker'])
                            if cronograma:
                                st.write("---")
                                st.write("📅 **Próximos Cobros (USD):**")
                                
                                pagos_calculados = []
                                for p in cronograma:
                                    # Calculamos el cobro según tus nominales
                                    monto = (bono['Nominales'] / 100) * p['cupon']
                                    pagos_calculados.append({
                                        "Fecha": p['fecha'], 
                                        "Monto (USD)": f"{monto:.2f}"
                                    })
                                st.table(pagos_calculados)
                        else:
                            st.warning(f"No se encontró cotización para {bono['Ticker']} en Rava.")

                    except Exception as e:
                        st.error(f"Error procesando {bono['Ticker']}")
        else:
            st.info("No hay bonos cargados.")
else:
    st.info("👈 Cargá tu primer activo en la barra lateral para empezar.")













































