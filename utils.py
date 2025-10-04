# utils.py

import matplotlib.pyplot as plt
import streamlit as st

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
        for k,v in stats.items():
            st.write(f"- {k}: {v}")

def plot_multi_bars(df, cols, titulo):
    fig, ax = plt.subplots()
    df.set_index("Brazo")[cols].plot(kind="bar", ax=ax)
    st.pyplot(fig)
    st.markdown(f"**{titulo}**")
