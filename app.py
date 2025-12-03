import math

import pandas as pd
import streamlit as st

import matplotlib.pyplot as plt


# ----------------------------------------
# Configuração básica da página
# ----------------------------------------
st.set_page_config(
    page_title="Desempenho CoinMarketCap - Teoria das Filas",
    layout="wide"
)

# ----------------------------------------
# CSS personalizado (cores + banner Bitcoin)
# ----------------------------------------
st.markdown(
    """
    <style>
    /* Fundo geral com gradiente suave */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top left, #1b2838 0, #cc9999 40%, #cccccc 100%);
        color: #66ff33;
    }

    /* Remove fundo branco de alguns containers */
    [data-testid="stHeader"] {
        background: transparent;
    }

    /* Banner com imagem grande do Bitcoin */
   .btc-banner {
    position: absolute;
    width: 30%;
    height: 260px;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 1.5rem;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.55);
}

/* imagem do bitcoin */
.btc-banner::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image: url("https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=032");
    background-position: center;
    background-repeat: no-repeat;
    background-size: 85%;
    opacity: 0.50;                           /* MAIS VISÍVEL */
    filter: saturate(1.4) contrast(1.2);
}

/* camada colorida por cima para dar brilho e destacar a imagem */
.btc-banner-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        120deg,
        rgba(255, 165, 0, 0.70),     /* cor principal forte */
        rgba(255, 200, 80, 0.50),
        rgba(255, 255, 255, 0.35)
    );
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 2.5rem 3rem;
}

    .btc-banner-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #ccff33;
        text-shadow: 0 0 10px rgba(0,0,0,0.7);
        margin-bottom: 0.3rem;
    }

    .btc-banner-subtitle {
        font-size: 1.05rem;
        max-width: 780px;
        color: #000000;
    }

    .btc-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(251, 191, 36, 0.18);
        color: #ccccff;
        border: 1px solid rgba(251, 191, 36, 0.4);
        margin-bottom: 0.8rem;
    }

    /* Abas */
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
    }

    /* Cartões de métrica */
[data-testid="stMetric"] {
    background: rgba(255, 200, 80, 0.45);  /* dourado claro */
    padding: 0.75rem 0.75rem;
    border-radius: 0.9rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.25);
    border: 1px solid rgba(255,180,60,0.8);
    color: #1b1b1b;
}

    /* Caixas de informação */
    .block-container {
        padding-top: 1.2rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------
# Banner customizado com imagem do Bitcoin
# ----------------------------------------
st.markdown(
    """
    <div class="btc-banner">
      <div class="btc-banner-overlay">
        <div class="btc-badge">
          🔢 Filas & Criptomoedas
        </div>
        <div class="btc-banner-title">
          Avaliação de Desempenho do CoinMarketCap
        </div>
        <div class="btc-banner-subtitle">
          Protótipo interativo em Streamlit para análise de desempenho de um sistema inspirado no CoinMarketCap, 
          utilizando Teoria das Filas (modelos M/M/1 e M/M/c) e dataset histórico de criptomoedas.
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Projeto de Modelagem: Teoria das Filas aplicada a um sistema web de alta demanda.")


# ----------------------------------------
# Funções de métricas de fila
# ----------------------------------------
def mm1_metrics(lmbda: float, mu: float):
    """
    Calcula métricas do modelo M/M/1.
    λ (lmbda) e μ (mu) em requisições por segundo.
    Retorna dict ou None se o sistema for instável.
    """
    if lmbda <= 0 or mu <= 0:
        return None

    if lmbda >= mu:
        # Sistema instável (ρ >= 1)
        return None

    rho = lmbda / mu  # Utilização
    L = rho / (1 - rho)  # Número médio no sistema
    Lq = (rho ** 2) / (1 - rho)  # Número médio na fila
    W = 1 / (mu - lmbda)  # Tempo médio no sistema (s)
    Wq = lmbda / (mu * (mu - lmbda))  # Tempo médio na fila (s)

    return {
        "rho": rho,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
    }


def mmc_metrics(lmbda: float, mu: float, c: int):
    """
    Calcula métricas do modelo M/M/c (c servidores idênticos).
    Fórmulas clássicas com Erlang C.
    λ e μ em req/s.

    Retorna dict ou None se sistema for instável ou parâmetros inválidos.
    """
    if lmbda <= 0 or mu <= 0 or c <= 0:
        return None

    # taxa de utilização global
    rho = lmbda / (c * mu)
    if rho >= 1:
        # sistema instável
        return None

    a = lmbda / mu  # tráfego oferecido

    # cálculo de P0 (probabilidade de zero clientes no sistema)
    sum_terms = 0.0
    for n in range(c):
        sum_terms += (a ** n) / math.factorial(n)

    last_term = (a ** c) / (math.factorial(c) * (1 - rho))
    P0 = 1.0 / (sum_terms + last_term)

    # Lq (clientes médios em fila) - fórmula de Erlang C
    Lq = (
        P0
        * (a ** c)
        * rho
        / (math.factorial(c) * ((1 - rho) ** 2))
    )

    L = Lq + a            # clientes médios no sistema
    Wq = Lq / lmbda       # tempo médio em fila
    W = Wq + 1 / mu       # tempo médio no sistema

    return {
        "rho": rho,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
        "P0": P0,
    }


# ----------------------------------------
# Abas do site
# ----------------------------------------
aba_instrucoes, aba_medicoes, aba_upload = st.tabs(
    ["📘 Instruções", "📏 Medições Teóricas (M/M/1 e M/M/c)", "📂 Upload do Dataset"]
)


# ----------------------------------------
# ABA 1 – INSTRUÇÕES
# ----------------------------------------
with aba_instrucoes:
    st.header("Como usar este site")

    st.markdown(
        """
        Este site foi desenvolvido como parte de um projeto de **modelagem e avaliação de desempenho**,
        aplicando **Teoria das Filas** a um cenário inspirado no site **CoinMarketCap**.

        Ele está dividido em três partes principais:

        ### 1. Instruções
        - Apresenta o objetivo geral do projeto.
        - Explica a lógica do uso de filas M/M/1 e M/M/c.

        ### 2. Medições Teóricas
        - Permite experimentar com os modelos:
          - **M/M/1** (um servidor lógico)
          - **M/M/c** (vários servidores em paralelo)
        - Você escolhe:
          - A taxa de chegada **λ** (req/s);
          - A taxa de serviço **μ** (req/s);
          - Opcionalmente, o número de servidores **c** (para M/M/c).
        - O sistema calcula automaticamente:
          - Utilização **ρ**
          - Número médio de requisições no sistema **L**
          - Número médio na fila **Lq**
          - Tempo médio no sistema **W**
          - Tempo médio na fila **Wq**

        ### 3. Upload do Dataset
        - Permite enviar um arquivo **CSV**;
        - A partir da coluna de volume diário, o sistema:
          - Estima um **λ médio** e um **λ de pico**;
          - Calcula as métricas de desempenho usando M/M/1 ou M/M/c.

        ---
        **Observação:**  
        Este é um protótipo acadêmico, focado em **conceitos de modelagem e análise de desempenho**, 
        e não em representar com precisão a infraestrutura real do CoinMarketCap.
        """
    )

    st.info(
        "Desenvolvido por: Leandro Queiroz e Irismar Neris."
    )


# ----------------------------------------
# ABA 2 – MEDIÇÕES TEÓRICAS (M/M/1 e M/M/c)
# ----------------------------------------
with aba_medicoes:
    st.header("Medições Teóricas – Modelos M/M/1 e M/M/c")

    st.markdown(
        """
        Selecione o **modelo de fila** que deseja analisar e informe os parâmetros:

        - **λ (lambda)**: taxa de chegada de requisições (req/s);
        - **μ (mi)**: taxa de serviço do servidor (req/s);
        - **c**: número de servidores (somente para M/M/c).

        Lembre-se:
        - Para **M/M/1**, é necessário que **λ < μ**;
        - Para **M/M/c**, é necessário que **λ < c·μ** (ou seja, ρ < 1).
        """
    )

    model_type = st.radio(
        "Escolha o modelo de fila:",
        ["M/M/1", "M/M/c"],
        horizontal=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        lmbda = st.number_input(
            "Taxa de chegada λ (req/s)",
            min_value=0.0,
            value=30.0,
            step=1.0,
            help="Quantidade média de requisições que chegam ao sistema a cada segundo."
        )

    with col2:
        mu = st.number_input(
            "Taxa de serviço μ (req/s) por servidor",
            min_value=0.0,
            value=50.0,
            step=1.0,
            help="Quantidade média de requisições que cada servidor consegue atender por segundo."
        )

    if model_type == "M/M/c":
        with col3:
            c = st.number_input(
                "Número de servidores c",
                min_value=1,
                value=2,
                step=1,
                help="Quantidade de servidores (ou instâncias) atendendo em paralelo."
            )
    else:
        c = 1  # apenas para manter referência, não usado em M/M/1

    if st.button("Calcular métricas do modelo selecionado", type="primary"):
        if model_type == "M/M/1":
            resultados = mm1_metrics(lmbda, mu)
        else:
            resultados = mmc_metrics(lmbda, mu, c)

        if resultados is None:
            st.error(
                "Não foi possível calcular as métricas. "
                "Verifique se λ > 0, μ > 0 e que o sistema é estável (λ < μ para M/M/1 ou λ < c·μ para M/M/c)."
            )
        else:
            rho = resultados["rho"]
            L = resultados["L"]
            Lq = resultados["Lq"]
            W = resultados["W"]
            Wq = resultados["Wq"]

            st.subheader("Resultados")

            col_a, col_b, col_c2 = st.columns(3)
            with col_a:
                st.metric("Utilização ρ", f"{rho:.3f}")
                st.metric("Nº médio no sistema L", f"{L:.3f}")
            with col_b:
                st.metric("Nº médio na fila Lq", f"{Lq:.3f}")
            with col_c2:
                st.metric("Tempo médio no sistema W (s)", f"{W:.3f}")
                st.metric("Tempo médio na fila Wq (s)", f"{Wq:.3f}")

            if model_type == "M/M/c":
                st.markdown(
                    f"**Modelo M/M/c com c = {c} servidores.** "
                    "A utilização ρ representa a fração média de ocupação global do sistema."
                )
            else:
                st.markdown("**Modelo M/M/1** (um servidor lógico atendendo todas as requisições).")

            st.markdown(
                """
                **Interpretação rápida:**
                - Quanto mais próximo de 1 for ρ, maior o risco de saturação do sistema;
                - L e Lq indicam o número médio de requisições em atendimento + fila;
                - W e Wq indicam, em segundos, o tempo médio gasto no sistema e na fila.
                """
            )


# ---------------- GRÁFICO (TEÓRICO) ----------------
            st.subheader("Gráfico das métricas")

            metricas = {
                "ρ (utilização)": rho,
                "L (no sistema)": L,
                "Lq (na fila)": Lq,
                "W (tempo no sistema)": W,
                "Wq (tempo na fila)": Wq,
            }

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(list(metricas.keys()), list(metricas.values()))
            ax.set_ylabel("Valor")
            ax.set_title(f"Métricas do modelo {model_type}")
            plt.xticks(rotation=45)
            st.pyplot(fig)


# ----------------------------------------
# ABA 3 – UPLOAD DO DATASET
# ----------------------------------------
with aba_upload:
    st.header("Upload do Dataset (CoinMarketCap / outro CSV)")

    st.markdown(
        """
        Nesta aba você pode fazer upload de um arquivo **CSV** contendo dados históricos
        agregados.

        A ideia é usar a coluna de **volume diário** como aproximação da carga de trabalho 
        (número de operações ou requisições associadas àquele dia).
        """
    )

    arquivo = st.file_uploader(
        "Envie o arquivo CSV com volume diário agregado",
        type=["csv"],
        help="Use, por exemplo, o arquivo historical_daily_volume_reduzido.csv com colunas 'date' e 'volume_24h_total'."
    )

    if arquivo is not None:
        try:
            df = pd.read_csv(arquivo)
        except Exception as e:
            st.error(f"Erro ao ler o CSV: {e}")
            st.stop()

        st.success("CSV carregado com sucesso! Pré-visualização:")
        st.dataframe(df.head())

        colunas = df.columns.tolist()

        st.subheader("Configurações de colunas")

        col_data = st.selectbox(
            "Coluna de data (opcional, mas recomendado)",
            options=["<nenhuma>"] + colunas,
            index=1 if "date" in colunas else 0,
        )

        col_volume = st.selectbox(
            "Coluna de volume (por dia)",
            options=colunas,
            index=colunas.index("volume_24h_total") if "volume_24h_total" in colunas else 0
        )

        if col_data != "<nenhuma>":
            try:
                df[col_data] = pd.to_datetime(df[col_data])
            except Exception:
                st.warning(
                    "Não foi possível converter a coluna de data automaticamente. "
                    "Verifique o formato da coluna selecionada."
                )

        # Limpeza básica de volume
        df_limp = df.dropna(subset=[col_volume]).copy()
        df_limp[col_volume] = pd.to_numeric(df_limp[col_volume], errors="coerce")
        df_limp = df_limp.dropna(subset=[col_volume])

        st.subheader("Resumo do volume diário")

        volume_medio = df_limp[col_volume].mean()
        volume_max = df_limp[col_volume].max()

        st.write(f"**Volume médio por linha** (ex.: por dia): `{volume_medio:,.2f}`")
        st.write(f"**Maior volume em uma linha** (pico): `{volume_max:,.2f}`")


        # Gráfico simples do volume ao longo do tempo (se houver data)
        if col_data != "<nenhuma>":
            st.subheader("Evolução do volume diário")
            fig_vol, ax_vol = plt.subplots(figsize=(9, 3))
            ax_vol.plot(df_limp[col_data], df_limp[col_volume])
            ax_vol.set_xlabel("Data")
            ax_vol.set_ylabel("Volume diário")
            ax_vol.set_title("Volume diário ao longo do tempo")
            plt.xticks(rotation=30)
            st.pyplot(fig_vol)    

        st.markdown("---")

        st.subheader("Estimativa de λ (taxa de chegada)")

        st.markdown(
            """
            Assumindo que cada linha representa **um dia**, aproximamos:

            - Taxa de chegada média:
              \\[
                  \\lambda_{médio} = \\frac{\\text{volume médio por dia}}{24 \\times 3600}
              \\]

            - Taxa de chegada no pico:
              \\[
                  \\lambda_{pico} = \\frac{\\text{maior volume por dia}}{24 \\times 3600}
              \\]
            """,
            unsafe_allow_html=True,
        )

        segundos_dia = 24 * 3600
        lambda_medio = volume_medio / segundos_dia
        lambda_pico = volume_max / segundos_dia

        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.write(f"**λ médio (req/s)** ≈ `{lambda_medio:.6f}`")
        with col_l2:
            st.write(f"**λ pico (req/s)** ≈ `{lambda_pico:.6f}`")

        st.markdown("---")

        st.subheader("Parâmetros da fila para o dataset")

        model_type_ds = st.radio(
            "Modelo para análise com base no dataset:",
            ["M/M/1", "M/M/c"],
            horizontal=True,
        )

        col_par1, col_par2 = st.columns(2)

        with col_par1:
            mu_dataset = st.number_input(
                "Taxa de serviço μ (req/s) por servidor",
                min_value=0.0,
                value=float(max(lambda_pico * 2, 1.0)),
                step=1.0,
                help="Capacidade média de atendimento de cada servidor (req/s)."
            )

        if model_type_ds == "M/M/c":
            with col_par2:
                c_dataset = st.number_input(
                    "Número de servidores c",
                    min_value=1,
                    value=2,
                    step=1,
                    help="Quantidade de servidores (ou instâncias) atendendo em paralelo."
                )
        else:
            c_dataset = 1

        if st.button("Calcular métricas com base no dataset", type="primary"):
            if model_type_ds == "M/M/1":
                res_medio = mm1_metrics(lambda_medio, mu_dataset)
                res_pico = mm1_metrics(lambda_pico, mu_dataset)
            else:
                res_medio = mmc_metrics(lambda_medio, mu_dataset, c_dataset)
                res_pico = mmc_metrics(lambda_pico, mu_dataset, c_dataset)

            if res_medio is None or res_pico is None:
                st.error(
                    "Não foi possível calcular as métricas. "
                    "Verifique se μ é maior do que λ médio e λ pico (para M/M/1) "
                    "ou se λ < c·μ (para M/M/c), garantindo estabilidade do sistema."
                )
            else:
                st.subheader("Resultados - Dia Médio")
                colm1, colm2, colm3 = st.columns(3)
                with colm1:
                    st.metric("ρ médio", f"{res_medio['rho']:.4f}")
                    st.metric("L médio", f"{res_medio['L']:.4f}")
                with colm2:
                    st.metric("Lq médio", f"{res_medio['Lq']:.4f}")
                with colm3:
                    st.metric("W médio (s)", f"{res_medio['W']:.4f}")
                    st.metric("Wq médio (s)", f"{res_medio['Wq']:.4f}")

                st.subheader("Resultados - Dia de Pico")
                colp1, colp2, colp3 = st.columns(3)
                with colp1:
                    st.metric("ρ pico", f"{res_pico['rho']:.4f}")
                    st.metric("L pico", f"{res_pico['L']:.4f}")
                with colp2:
                    st.metric("Lq pico", f"{res_pico['Lq']:.4f}")
                with colp3:
                    st.metric("W pico (s)", f"{res_pico['W']:.4f}")
                    st.metric("Wq pico (s)", f"{res_pico['Wq']:.4f}")

                if model_type_ds == "M/M/c":
                    st.markdown(
                        f"**Modelo M/M/c com c = {c_dataset} servidores aplicado ao dia médio e ao dia de pico.**"
                    )
                else:
                    st.markdown("**Modelo M/M/1 aplicado ao dia médio e ao dia de pico.**")

  # --------- GRÁFICO COMPARATIVO (Médio x Pico) ----------
                st.subheader("Gráfico comparativo – Dia Médio x Dia de Pico")

                metricas_medio = {
                    "ρ": res_medio["rho"],
                    "L": res_medio["L"],
                    "Lq": res_medio["Lq"],
                    "W": res_medio["W"],
                    "Wq": res_medio["Wq"],
                }

                metricas_pico = {
                    "ρ": res_pico["rho"],
                    "L": res_pico["L"],
                    "Lq": res_pico["Lq"],
                    "W": res_pico["W"],
                    "Wq": res_pico["Wq"],
                }

                fig2, ax2 = plt.subplots(figsize=(9, 4))
                indices = range(len(metricas_medio))
                larg = 0.35

                ax2.bar(
                    [i - larg/2 for i in indices],
                    list(metricas_medio.values()),
                    width=larg,
                    label="Dia Médio",
                )
                ax2.bar(
                    [i + larg/2 for i in indices],
                    list(metricas_pico.values()),
                    width=larg,
                    label="Dia de Pico",
                )

                ax2.set_xticks(list(indices))
                ax2.set_xticklabels(list(metricas_medio.keys()))
                ax2.set_ylabel("Valor")
                ax2.set_title("Métricas – comparação Dia Médio x Dia de Pico")
                ax2.legend()

                st.pyplot(fig2)
                   
                st.markdown(
                    """
                    **Interpretação:**

                    - No **dia médio**, ρ mostra o quanto o sistema está ocupado em situação típica;
                    - No **dia de pico**, ρ se aproxima mais de 1, indicando maior risco de saturação;
                    - W e Wq podem ser usados para discutir impacto no tempo de resposta percebido pelos usuários;
                    - Ao variar μ e (quando aplicável) c, você consegue simular melhorias na infraestrutura.
                    """
                )
    else:
        st.info("Envie um arquivo CSV para habilitar as análises desta aba.")








































