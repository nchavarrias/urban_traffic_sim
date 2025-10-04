import streamlit as st
import simpy
import numpy as np
import pandas as pd
from intersection import model_plus, model_tee, model_star
from simulation import simulate_intersection
from params import get_arrival_rates, get_sim_time
from utils import (
    draw_intersection, 
    plot_bar_metric, 
    show_stats, 
    executive_summary_and_advice,
    detailed_problem_description,
    assign_verde_por_brazo
)

# --- SELECCIÓN DE MODELO DE CRUCE ---
st.title("Simulador de Tráfico Urbano por Cruce Multi-Fase")
modelo = st.sidebar.selectbox("Modelo de cruce", ["X / +", "T", "Estrella"])
if modelo == "X / +":
    intersection = model_plus(4)
elif modelo == "T":
    intersection = model_tee()
elif modelo == "Estrella":
    intersection = model_star()

n_arms = intersection.n_arms
n_fases = len(intersection.phases)

# --- CONFIGURACIÓN DE CICLO Y VERDES ---
ciclo = st.sidebar.slider("Ciclo semafórico total (s)", 20, 180, 90)
st.sidebar.markdown("##### Proporción de verde por fase (%)")
verdes = []
proporcion_total = 0
for idx, phase in enumerate(intersection.phases):
    value = st.sidebar.slider(
        f"{phase.name} (%)", 0, 100, int(100 / n_fases), key=f"v_{idx}"
    )
    verdes.append(value)
    proporcion_total += value

if proporcion_total > 100:
    st.sidebar.error(f"¡La suma de proporciones supera el 100% ({proporcion_total}%)!")
else:
    st.sidebar.success(f"Suma total: {proporcion_total}%")

# Asignar segundos reales a cada fase
segundos_verde = [int(ciclo * verde / 100) for verde in verdes]
for idx, phase in enumerate(intersection.phases):
    phase.green_time = segundos_verde[idx]
    st.sidebar.markdown(f"**{phase.name}**: {verdes[idx]}% → {segundos_verde[idx]}s")

# --- CONFIGURACIÓN DE FLUJOS POR BRAZO ---
llegadas = [st.sidebar.slider(f"Flujo brazo {i+1} (veh/h)", 50, 1200, 400) for i in range(n_arms)]

# --- CONFIGURACIÓN DE CAPACIDAD MÁXIMA POR BRAZO ---
st.sidebar.markdown("### Capacidad máxima (veh/h) por brazo")
capacidades_max = []
for i in range(n_arms):
    cap = st.sidebar.number_input(
        f"Capacidad brazo {i+1} (veh/h)",
        min_value=500, max_value=5000,
        value=1800,
        step=100,
        key=f"cap_{i}"
    )
    capacidades_max.append(cap)

# --- DIAGRAMA DEL CRUCE ---
st.markdown("### Esquema del cruce y fases")
selected_fase = st.selectbox(
    "Visualiza o resalta la fase:", 
    range(n_fases),
    format_func=lambda i: intersection.phases[i].name
)
draw_intersection(
    n_arms=intersection.n_arms,
    phases=intersection.phases,
    active_phase=intersection.phases[selected_fase]
)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("### Configuración actual del cruce")
for idx, phase in enumerate(intersection.phases):
    acc = ', '.join([f"Brazo {i+1}" for i in phase.arms_active])
    st.markdown(f"- **{phase.name}**: {segundos_verde[idx]}s (<span style='color:red'>{acc}</span>)", unsafe_allow_html=True)

# --- DURACIÓN DE SIMULACIÓN Y BOTÓN ---
sim_time = st.slider("Duración de simulación total (s)", 600, 3600, 1800)
resultados = {}

# --- EJECUCIÓN DE SIMULACIÓN ---
if st.button("Ejecutar simulación", disabled=(proporcion_total > 100)):
    env = simpy.Environment()
    env.process(simulate_intersection(env, intersection, llegadas, sim_time, resultados))
    env.run()
    df = pd.DataFrame({
        "Brazo": [f"Brazo {i+1}" for i in range(n_arms)],
        "Demora promedio (s)": resultados['demora_prom'],
        "Cola máxima": resultados['cola_max'],
        "Atendidos": resultados['atendidos']
    })

    # Calcular y añadir la saturación por brazo
    tiempos_verde_brazo = assign_verde_por_brazo(intersection, segundos_verde)
    saturacion = []
    for i, q in enumerate(llegadas):
        if tiempos_verde_brazo[i] == 0:
            sat_i = 0
        else:
            cap_ef = capacidades_max[i] * (tiempos_verde_brazo[i] / ciclo)
            sat_i = q / cap_ef if cap_ef > 0 else 0
        saturacion.append(sat_i)
    df["Saturación"] = saturacion

    # Mostrar DF con color según saturación
    def color_saturation(val):
        if val >= 1:
            color = "background-color: #ff4c4c"  # rojo fuerte
        elif val >= 0.85:
            color = "background-color: #ffd966"  # amarillo
        else:
            color = "background-color: #a9d18e"  # verde
        return color

    st.markdown("### Métricas por brazo")
    st.dataframe(df.style.applymap(color_saturation, subset=["Saturación"]))
    plot_bar_metric(df, "Demora promedio (s)", "Demora media por brazo")
    plot_bar_metric(df, "Cola máxima", "Cola máxima por brazo")
    plot_bar_metric(df, "Atendidos", "Vehículos atendidos por brazo")
    show_stats(df)

    # Alertas saturación
    for i, v in enumerate(saturacion):
        if v >= 1:
            st.error(f"¡Brazo {i+1} está saturado (S≥1)! Considera aumentar tiempo verde o capacidad.")
        elif v >= 0.85:
            st.warning(f"Brazo {i+1} está próximo a saturarse (S≥0.85). Vigila la demanda o ajuste semafórico.")

    consejo = executive_summary_and_advice(df, segundos_verde, intersection, ciclo)
    st.markdown(f"### Consejo ejecutivo")
    st.info(consejo)

    descripcion_problemas = detailed_problem_description(df, segundos_verde, intersection, ciclo)
    st.markdown(descripcion_problemas)

else:
    st.info("Ajusta los parámetros y pulsa 'Ejecutar simulación' para ver resultados. No puedes simular si la suma de verdes supera el 100%.")

st.markdown("---")
st.markdown("Desarrollado para simulaciones de cruces urbanos. Modifica el modelo, el ciclo y los verdes para experimentar con diferentes estrategias semafóricas.")
