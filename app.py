import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# 🔐 Login simples
senha = st.text_input("Senha", type="password")

if senha != "1234":
    st.stop()

st.title("Dashboard Financeiro")

# Upload
arquivo = st.file_uploader("Envie seu Excel", type=["xlsx"])

if arquivo:
    xls = pd.ExcelFile(arquivo)
    dados = []

    for aba in xls.sheet_names:
        if "_" in aba and "Cons" not in aba:
            try:
                df = pd.read_excel(arquivo, sheet_name=aba)

                if "Crédito" in df.columns and "Débito" in df.columns:
                    df["valor"] = df["Crédito"].fillna(0) - df["Débito"].fillna(0)
                    df["data"] = pd.to_datetime(df["Data"], errors="coerce")
                    df["mes"] = df["data"].dt.month
                    df["ano"] = df["data"].dt.year
                    df["categoria"] = df["Tipo"]

                    dados.append(df)
            except:
                pass

    df = pd.concat(dados)

    # Filtros
    ano = st.selectbox("Ano", sorted(df["ano"].dropna().unique()))
    mes = st.selectbox("Mês", sorted(df["mes"].dropna().unique()))

    df = df[(df["ano"] == ano) & (df["mes"] == mes)]

    # Ocultar valores
    ocultar = st.checkbox("Ocultar valores")

    def fmt(v):
        return "R$ •••••" if ocultar else f"R$ {v:,.2f}"

    entrada = df[df["valor"] > 0]["valor"].sum()
    saida = df[df["valor"] < 0]["valor"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Receita", fmt(entrada))
    col2.metric("Despesa", fmt(abs(saida)))
    col3.metric("Resultado", fmt(entrada + saida))

    st.subheader("Por categoria")
    st.bar_chart(df.groupby("categoria")["valor"].sum().abs())
