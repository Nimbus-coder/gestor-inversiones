import streamlit as st
import yfinance as yf
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Mi Portfolio PRO", layout="wide")

# Título y Diseño
st.title("🚀 Mi Gestor de Inversiones")
st.markdown("Controlá tus Acciones Argentinas (.BA) y CEDEARs en tiempo real.")

# --- BARRA LATERAL (Donde cargamos datos) ---
with st.sidebar:
    st.header("📥 Cargar Operación")
    
    tipo_activo = st.radio("Seleccionar tipo:", ["Acciones/CEDEARs", "Bonos/ONs"])
    st.divider()

    if tipo_activo == "Acciones/CEDEARs":
        ticker = st.text_input("Ticker (ej: GGAL.BA)", value="GGAL.BA").upper()
        cantidad = st.number_input("Cantidad", min_value=1, value=10)
        precio_compra = st.number_input("Precio de Compra (ARS)", min_value=0.0, value=1000.0)

    else:
        t_bono = st.text_input("Ticker del Bono (ej: AL30D)").upper()
        vn_bono = st.number_input("Valor Nominal (V.N.)", min_value=1, value=1000)
        p_bono = st.number_input("Precio de Compra USD", min_value=0.0, value=50.0)

        if st.button("Guardar Bono"):
            if 'portfolio_bono' not in st.session_state:
                st.session_state['portfolio_bonos'] = []
                
            st.session_state['portfolio_bonos'].append({
                "Ticker": t_bono,
                "VN": vn_bono,
                "Precio": p_bono,
            })
            st.succes(f"Bono {t_bono} guardado!")
            st.rerun()
                
    
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

    else:
        t_bono = st.text_input("Ticker del Bono (ej: AL30D)").upper()
        vn_bono = st.number_input("Valor Nominal(VN)", min_value=1, value=1000)
        p_bono = st.number_input("Precio de compra USD", min_value=0.0, value=50.0)

        if st.button("Guardar Bono"):
            if 'portfolio_bonos' not in st.session_state:
                st.session_state['portfolio_bonos'] = []

            st.session_state['portfolio bonos'].append({
                "Ticker": t_bono,
                "VN": vn_bono,
                "Precio": p_bono
            })
        st.success(f"Bono {t_bono} guardado!")
        st.rerun()
                                        
        
    st.divider()
    st.header("🗑️ Gestion de Salida")

    if 'portfolio' in st.session_state and len(st.session_state['portfolio']) > 0:

        lista_tickers = [item['Ticker'] for item in st.session_state['portfolio']]
        seleccionados = st.multiselect("Selecciona para quitar:", lista_tickers)
        
        if st.button("Eliminar Seleccionados"):
            if seleccionados:
                st.session_state['portfolio'] = [
                    item for item in  st.session_state['portfolio']
                    if item['Ticker'] not in seleccionados
                ]
                st.rerun()

    st.write("")

    if st.button("💣 Resetear Todo"):
        del st.session_state['portfolio']
        st.rerun()

    else: 
        st.info("La Cartera está Vacía.")
        
    st.divider()
    

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

    # --- CREACIÓN DE PESTAÑAS ---
    tab_acciones, tab_bonos = st.tabs(["📈 Acciones y CEDEARs", "🏦 Renta Fija (Bonos/ONs)"])

    # --- CONTENIDO DE LA PESTAÑA 1 (Todo lo que ya tenías) ---
    with tab_acciones:
        st.write("Tu panel de acciones actual") # Esto es solo un placeholder

    # --- CONTENIDO DE LA PESTAÑA 2 (Lo nuevo) ---
    with tab_bonos:
        st.header("Gestión de Renta Fija")
        st.info("Próximamente: Análisis de TIR, Cupones y Cashflow.")
        st.subheader("📥 Cargar mis Bonos/ONs")
    with tab_bonos:
        st.header("🏦 Panel de Renta Fija")

    # Formulario de carga exclusivo para Bonos
    with st.expander("➕ Cargar Nuevo Bono / ON"):
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            t_bono = st.text_input("Ticker (ej: AL30D.BA)").upper()
        with col_b2:
            nominales = st.number_input("Valor Nominal (V.N.)", min_value=1, value=1000)
        with col_b3:
            p_compra = st.number_input("Precio de Compra USD", min_value=0.0, value=50.0)
        
        if st.button("Guardar Bono"):
            if 'portfolio_bonos' not in st.session_state:
                st.session_state['portfolio_bonos'] = []
            
            # Guardamos los datos en una caja distinta a la de acciones
            st.session_state['portfolio_bonos'].append({
                "Ticker": t_bono,
                "Nominales": nominales,
                "Precio Compra": p_compra
            })
            st.success(f"Bono {t_bono} guardado!")
            st.rerun()

    # Mostramos los bonos si existen
    if 'portfolio_bonos' in st.session_state and len(st.session_state['portfolio_bonos']) > 0:
        st.subheader("Mis Tenencias en Renta Fija")
        
        for bono in st.session_state['portfolio_bonos']:
            with st.container():
                # Buscamos precio real para calcular métricas
                data = yf.Ticker(bono['Ticker'])
                precio_hoy = data.history(period="1d")['Close'].iloc[0]
                
                # Diseño de ficha de bono
                c1, c2, c3 = st.columns(3)
                c1.metric(bono['Ticker'], f"USD {precio_hoy:.2f}")
                c2.write(f"**V.N.:** {bono['Nominales']}")
                c3.write(f"**Paridad:** {(precio_hoy/100)*100:.1f}%")
                
                # Acá es donde pondremos el Cashflow que hicimos antes
                st.divider()
    else:
        st.info("Aún no cargaste bonos en esta sección.")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        ticker_b = st.text_input("Ticker del Bono (ej: AL30D.BA)", value="AL30D.BA").upper()
    with col_b2:
        nominales = st.number_input("Cantidad de Nominales", min_value=1, value=1000)
    with col_b3:
        precio_pago = st.number_input("Precio pagado (USD)", min_value=0.0, value=58.0)

    if st.button("Analizar Bono"):
        # 2. Buscamos precio en vivo para comparar
        data_b = yf.Ticker(ticker_b)
        precio_actual_b = data_b.history(period="1d")['Close'].iloc[0]
        
        # 3. Cálculo de métricas básicas
        paridad = (precio_actual_b / 100) * 100 # Los bonos valen 100 al final
        st.metric("Precio Actual", f"USD {precio_actual_b:.2f}", delta=f"{precio_actual_b - precio_pago:.2f}")

    # Definimos el cronograma (esto después lo haremos dinámico)
        cronograma = [
            {"fecha": "2026-07-09", "monto": 8.0}, # paga 8 dólares cada 100 nominales
            {"fecha": "2027-01-09", "monto": 8.0},
            {"fecha": "2027-07-09", "monto": 8.0},
        ]

        st.write("### 💰 Tus próximos cobros estimados")
        cobros_reales = []
        total_a_cobrar = 0

        for c in cronograma:
            # Lógica: (Nominales / 100) * monto del cupón
            mi_cobro = (nominales / 100) * c["monto"]
            cobros_reales.append({
                "Fecha": c["fecha"],
                "Monto a recibir (USD)": mi_cobro
            })
            total_a_cobrar += mi_cobro

        st.table(pd.DataFrame(cobros_reales))
        st.info(f"💵 En total, vas a recibir **USD {total_actual_cobrar:.2f}** hasta el vencimiento.")
    
    # Aquí es donde empezaremos a construir la lógica de bonos
    # Defininimos el activo y sus pagos futuros
    ticket_bono = "AL30"
    precio_bono_usd = 58.50 # Esto después lo buscaremos con yfinance (AL30D.BA)
    
    # Lista de cupones (Fecha, Monto de interés, Monto de amortización)
    # Valores aproximados para el ejemplo
    cronograma = [
        {"fecha": "2026-07-09", "interes": 0.25, "amort": 4.0},
        {"fecha": "2027-01-09", "interes": 0.25, "amort": 4.0},
        {"fecha": "2027-07-09", "interes": 0.25, "amort": 4.0},
    ]

    st.subheader(f"Análisis de Flujo de Fondos: {ticket_bono}")

    from datetime import datetime

    hoy = datetime.now()
    proximos_pagos = []

    for pago in cronograma:
        fecha_dt = datetime.strptime(pago["fecha"], "%Y-%m-%d")
        if fecha_dt > hoy:
            dias_faltantes = (fecha_dt - hoy).days
            proximos_pagos.append({
                "Fecha": pago["fecha"],
                "Cobro Total": pago["interes"] + pago["amort"],
                "Días Faltantes": dias_faltantes
            })

    if proximos_pagos:
        df_bono = pd.DataFrame(proximos_pagos)
        
        # Mostramos un cartel destacado con el pago más cercano
        next_p = proximos_pagos[0]
        st.info(f"💰 El próximo cobro es en **{next_p['Días Faltantes']} días** ({next_p['Fecha']})")
        
        # Tabla de Cashflow
        st.write("### 📅 Cronograma de Cobros")
        st.table(df_bono)

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









































