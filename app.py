import streamlit as st
import yfinance as yf
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Mi Portfolio PRO", layout="wide")

# Título y Diseño
st.title("🚀 Mi Gestor de Inversiones")
st.markdown("Controlá tus acciones argentinas (.BA) y CEDEARs en tiempo real.")

# --- BARRA LATERAL (Donde cargamos datos) ---
with st.sidebar:
    st.header("📥 Cargar Operación")
    ticker = st.text_input("Ticker (ej: GGAL.BA)", value="GGAL.BA").upper()
    cantidad = st.number_input("Cantidad", min_value=1, value=10)
    precio_compra = st.number_input("Precio de Compra (ARS)", min_value=0.0, value=1000.0)
    
    if st.button("Agregar a Cartera"):
        # Guardamos en la "memoria" de la sesión (Session State)
        if 'portfolio' not in st.session_state:
            st.session_state['portfolio'] = []
            
        nueva_posicion = {
            "Ticker": ticker,
            "Cantidad": cantidad,
            "Precio Compra": precio_compra
        }
        st.session_state['portfolio'].append(nueva_posicion)
        st.success(f"✅ {ticker} Agregado!")
        st.rerun()
        
    st.divider()

if st.button("🗑️ Borrar Todo"):
    if 'portfolio' in st.session_state:
        del st.session_state['portfolio']
    st.rerun()
    

# --- PANTALLA PRINCIPAL ---

# Verificamos si hay datos cargados
if 'portfolio' in st.session_state and len(st.session_state['portfolio']) > 0:
    
    lista_resultados = []
    total_invertido = 0
    total_actual = 0
    
    # Barra de progreso visual
    progreso = st.progress(0)
    total_items = len(st.session_state['portfolio'])
    
    for i, item in enumerate(st.session_state['portfolio']):
        try:
            # Buscamos precio en vivo
            stock = yf.Ticker(item['Ticker'])
            history = stock.history(period="1d")
            precio_hoy = history['Close'].iloc[0]
            
            val_actual = precio_hoy * item['Cantidad']
            val_compra = item['Precio Compra'] * item['Cantidad']
            diff = val_actual - val_compra
            pct = ((val_actual - val_compra) / val_compra) * 100
            
            lista_resultados.append({
                "Ticker": item['Ticker'],
                "Cantidad": item['Cantidad'],
                "Precio Hoy": precio_hoy,
                "Invertido ($)": val_compra,
                "Valor Hoy ($)": val_actual,
                "Ganancia ($)": diff,
                "Rendimiento (%)": pct
            })
            
            total_invertido += val_compra
            total_actual += val_actual
            
            # Actualizamos barrita
            progreso.progress((i + 1) / total_items)
            
        except Exception as e:
            st.error(f"Error con {item['Ticker']}: {e}")

    # CREAMOS LA TABLA DE PANDAS
    df = pd.DataFrame(lista_resultados)
    
    # --- MÉTRICAS GRANDES (KIPs) ---
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Invertido", f"$ {total_invertido:,.0f}")
    col2.metric("Valor Actual", f"$ {total_actual:,.0f}")
    
    ganancia_total = total_actual - total_invertido
    color_delta = "normal" # Verde o Rojo automático
    col3.metric("Resultado Global", f"$ {ganancia_total:,.0f}", delta=f"{ganancia_total:,.0f}")

    # --- TABLA Y GRÁFICOS ---
    st.subheader("📊 Detalle de Activos")

    mis_reglas = {
        "Precio Hoy": "${:,.2f}",
        "Ganancia ($)": "${:,.2f}",
        "Rendimiento (%)": "${:.2f}%",
        "Valor Hoy ($)": "${:,.2f}",
        "Invertido ($)": "${:,.2f}",
    }
        
    # Mostramos la tabla con colores automáticos en la columna de Rendimiento
    st.dataframe(df.style.format(mis_reglas), use_container_width=True)
    
    # Gráfico
    st.subheader("Distribución de Cartera")
    st.bar_chart(df.set_index("Ticker")["Valor Hoy ($)"])

else:

    st.info("👈 Cargá tu primera acción en el menú de la izquierda para empezar.")












