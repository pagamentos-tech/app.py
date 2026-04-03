import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# 🔐 LOGIN
senha = st.text_input("Senha", type="password")

if senha != "1234":
    st.stop()

st.title("📊 Dashboard Financeiro")

# 📤 Upload
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

    # 🎛️ FILTROS
    colf1, colf2 = st.columns(2)
    ano = colf1.selectbox("Ano", sorted(df["ano"].dropna().unique()))
    mes = colf2.selectbox("Mês", sorted(df["mes"].dropna().unique()))

    ocultar = st.checkbox("👁 Ocultar valores")

    def fmt(v):
        return "R$ •••••" if ocultar else f"R$ {v:,.2f}"

    # 📅 CONSOLIDADO ANUAL
    st.subheader("📅 Consolidado do Ano")

    df_ano = df[df["ano"] == ano]

    entrada_ano = df_ano[df_ano["valor"] > 0]["valor"].sum()
    saida_ano = df_ano[df_ano["valor"] < 0]["valor"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Receita Ano", fmt(entrada_ano))
    c2.metric("Despesa Ano", fmt(abs(saida_ano)))
    c3.metric("Resultado Ano", fmt(entrada_ano + saida_ano))

    # 📈 EVOLUÇÃO MENSAL
    st.subheader("📈 Evolução Mensal")
    mensal = df_ano.groupby("mes")["valor"].sum()
    st.line_chart(mensal)

    # 📊 DADOS DO MÊS
    df_mes = df[(df["ano"] == ano) & (df["mes"] == mes)]

    entrada = df_mes[df_mes["valor"] > 0]["valor"].sum()
    saida = df_mes[df_mes["valor"] < 0]["valor"].sum()

    st.subheader("📊 Resultado do Mês")

    m1, m2, m3 = st.columns(3)
    m1.metric("Receita", fmt(entrada))
    m2.metric("Despesa", fmt(abs(saida)))
    m3.metric("Resultado", fmt(entrada + saida))

    # 🔥 TOP 10 CATEGORIAS (AGORA LEGÍVEL)
    st.subheader("📊 Top 10 Despesas")

    cat = df_mes.groupby("categoria")["valor"].sum().abs()
    cat = cat.sort_values(ascending=False)

    top10 = cat.head(10)
    outros = pd.Series({"Outros": cat[10:].sum()})

    cat_final = pd.concat([top10, outros])

    # encurtar nomes grandes
    cat_final.index = [
        str(i)[:25] + "..." if len(str(i)) > 25 else i
        for i in cat_final.index
    ]

    fig, ax = plt.subplots(figsize=(8,5))
    cat
