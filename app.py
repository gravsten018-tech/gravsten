import streamlit as st
pip install yfinance
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date

# ---------------------------
# App config
# ---------------------------
st.set_page_config(
    page_title="Johans Aktier",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Johans Aktier")
st.markdown("Visualisera och analysera aktier med realtidsdata från Yahoo Finance.")

# ---------------------------
# Sidebar inputs
# ---------------------------
st.sidebar.header("Inställningar")

ticker = st.sidebar.text_input("Aktieticker", value="AAPL")
start_date = st.sidebar.date_input("Startdatum", date(2022, 1, 1))
end_date = st.sidebar.date_input("Slutdatum", date.today())

show_ma20 = st.sidebar.checkbox("Visa MA20", True)
show_ma50 = st.sidebar.checkbox("Visa MA50", True)

# ---------------------------
# Load data
# ---------------------------
@st.cache_data
def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data

if ticker:
    data = load_data(ticker, start_date, end_date)

    if data.empty:
        st.error("Ingen data hittades. Kontrollera tickern.")
        st.stop()

    # ---------------------------
    # Calculations
    # ---------------------------
    data["MA20"] = data["Close"].rolling(20).mean()
    data["MA50"] = data["Close"].rolling(50).mean()
    data["Daily Return"] = data["Close"].pct_change()

    # ---------------------------
    # Metrics
    # ---------------------------
    col1, col2, col3, col4 = st.columns(4)

    latest_price = data["Close"].iloc[-1]
    prev_price = data["Close"].iloc[-2]
    daily_change = (latest_price - prev_price) / prev_price * 100
    volatility = data["Daily Return"].std() * np.sqrt(252) * 100

    col1.metric("Senaste pris", f"${latest_price:.2f}")
    col2.metric("Daglig förändring", f"{daily_change:.2f}%", delta=f"{daily_change:.2f}%")
    col3.metric("Volatilitet (årlig)", f"{volatility:.2f}%")
    col4.metric("Antal handelsdagar", len(data))

    # ---------------------------
    # Candlestick chart
    # ---------------------------
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Pris"
    ))

    if show_ma20:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["MA20"],
            line=dict(color="orange", width=2),
            name="MA20"
        ))

    if show_ma50:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["MA50"],
            line=dict(color="blue", width=2),
            name="MA50"
        ))

    fig.update_layout(
        title=f"{ticker} – Prisdiagram",
        xaxis_title="Datum",
        yaxis_title="Pris",
        height=600,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------
    # Volume chart
    # ---------------------------
    vol_fig = go.Figure()

    vol_fig.add_trace(go.Bar(
        x=data.index,
        y=data["Volume"],
        name="Volym"
    ))

    vol_fig.update_layout(
        title="Handelsvolym",
        height=300
    )

    st.plotly_chart(vol_fig, use_container_width=True)

    # ---------------------------
    # Data table
    # ---------------------------
    with st.expander("Visa rådata"):
        st.dataframe(data.tail(50))
