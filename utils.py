import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

def draw_intersection(n_arms=4, phases=None, active_phase=None):
    """
    Dibuja un diagrama esquemático del cruce con n brazos.
    Colorea los brazos activos en la fase (si se indica active_phase).
    """
    fig, ax = plt.subplots(figsize=(4, 4))
    angles = np.linspace(0, 2 * np.pi, n_arms, endpoint=False)
    for idx, angle in enumerate(angles):
        x = [0, np.cos(angle)]
        y = [0, np.sin(angle)]
        color = "tab:blue"
        # Destaca brazos de la fase activa
        if active_phase is not None and idx in active_phase.arms_active:
            color = "tab:red"
        ax.plot(x, y, lw=12, color=color, solid_capstyle="round")
        # Marca los números de brazo
        ax.text(1.25 * np.cos(angle), 1.25 * np.sin(angle), f"B{idx + 1}", ha="center", va="center", fontsize=14)
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.axis("off")
    plt.tight_layout()
    st.pyplot(fig)

def plot_bar_metric(df, col, title):
    st.bar_chart(df.set_index("Brazo")[col])
    st.markdown(f"**{title}**")

def summary_stats(series):
    return {
        "Media": round(series.mean(), 2),
        "Máximo": int(series.max()),
        "Mínimo": int(series.min()),
        "Desv. típica": round(series.std(), 2)
    }

def show_stats(df):
    st.markdown("### Resumen Estadístico")
    for col in ["Demora promedio (s)", "Cola máxima", "Atendidos"]:
        stats = summary_stats(df[col])
        st.markdown(f"#### {col}")
        for k, v in stats.items():
            st.write(f"- {k}: {v}")

def executive_summary_and_advice(df, segundos_verde, intersection, ciclo):
    consejo = ""
    max_demora = df["Demora promedio (s)"].max()
    max_cola = df["Cola máxima"].max()
    brazo_peor = df.iloc[df["Demora promedio (s)"].idxmax()]["Brazo"]
    idx_fase_peor = None

    # Buscar qué fase abre ese brazo
    for i, phase in enumerate(intersection.phases):
        if df["Brazo"].iloc[df["Demora promedio (s)"].idxmax()] in [f"Brazo {a+1}" for a in phase.arms_active]:
            idx_fase_peor = i
            break

    # Reglas simples para el consejo
    if max_demora > 100:
        consejo = f"Considera aumentar el ciclo total o incrementar el verde en la fase que atiende a {brazo_peor} (actualmente {segundos_verde[idx_fase_peor]}s)."
    elif max_demora > 60 or max_cola > 30:
        consejo = f"Sube el verde de la fase prioritaria para {brazo_peor} o baja el verde en fases con menos tráfico."
    elif (df['Demora promedio (s)'] < 20).all():
        consejo = "El cruce está operando eficientemente. Puedes considerar acortar ligeramente el ciclo para reducir esperas generales."
    else:
        consejo = "Prueba equilibrar mejor los verdes entre fases y revisa si el ciclo total es suficiente."

    # Posibles mejoras avanzadas
    if ciclo < 40:
        consejo += " El ciclo es muy corto; podrías perder eficiencia por tiempos de pérdida."
    elif ciclo > 150:
        consejo += " Cuidado con ciclos demasiado largos: pueden aumentar esperas en fases con baja demanda."

    return consejo
