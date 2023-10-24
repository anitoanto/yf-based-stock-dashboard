import streamlit as st
import pandas as pd
import time
from backend import load_metrics


def set_page_config():
    st.set_page_config(layout="wide")

    st.markdown(
        """
        <style>
            header {display: none !important;}
            footer {display: none !important;}
            .block-container {
                padding-top: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


set_page_config()

st.title("Dashboard")

NSE_SYMBOLS = pd.read_csv("./MCAP31032023_0.csv")["Symbol"].to_list()


ticker = st.selectbox("SELECT NSE TICKER", NSE_SYMBOLS)

if st.button("Load Metrics"):
    with st.spinner("Please wait ..."):
        res = load_metrics(ticker)

    st.dataframe(res["metrics"], use_container_width=True, hide_index=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Current Market Price",
            value=round(res["metrics"]["CMP"], 2),
            delta=str(round(res["metrics"]["% Change"][0], 2)) + "% today",
        )
    with col2:
        st.write("Major Share Holdings")
        st.dataframe(
            res["dfs"]["major_holders"], use_container_width=True, hide_index=True
        )

    st.write("Cash Flow Report")
    st.dataframe(res["dfs"]["cf_yearly"], use_container_width=True)

    st.write("Balance Sheet")
    st.dataframe(res["dfs"]["bls_yearly"], use_container_width=True)

    st.write("Income Statement")
    st.dataframe(res["dfs"]["inc_yearly"], use_container_width=True)
