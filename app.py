import streamlit as st
import yfinance as yf
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Mi Portfolio PRO", layout="wide")

# Título y Diseño
st.title("🚀 Mi Gestor de Inversiones")
st.markdown("Controlá tus Acciones Argentinas (.BA) y CEDEARs en tiempo real.")

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
                    try:
                        data = yf.Ticker(bono['Ticker'])
                        p_hoy = data.history(period="1d")['Close'].iloc[0]
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Precio Actual", f"USD {p_hoy:.2f}")
                        c2.metric("V.N.", bono['Nominales'])
                        c3.metric("Paridad", f"{(p_hoy/100)*100:.1f}%")
                    except: st.error(f"Error con {bono['Ticker']}")
        else:
            st.info("No hay bonos cargados.")
else:
    st.info("👈 Cargá tu primer activo en la barra lateral para empezar.")











































