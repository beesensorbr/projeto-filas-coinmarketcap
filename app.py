import math

import pandas as pd
import streamlit as st

# -----------------------------
# Configuração básica da página
# -----------------------------
st.set_page_config(
    page_title="Desempenho CoinMarketCap - Teoria das Filas",
    layout="wide"
)

st.title("Análise de Desempenho com Teoria das Filas")
st.caption("Exemplo aplicado ao CoinMarketCap usando dataset histórico (Kaggle).")


# -----------------------------
# Função para calcular métricas M/M/1
# -----------------------------
def mm1_metrics(lmbda, mu):
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
    L = rho / (1 - rho)  # Número médio de clientes no sistema
    Lq = rho ** 2 / (1 - rho)  # Número médio na fila
    W = 1 / (mu - lmbda)  # Tempo médio no sistema (segundos)
    Wq = lmbda / (mu * (mu - lmbda))  # Tempo médio na fila (segundos)

    return {
        "rho": rho,
        "L": L,
        "Lq": Lq,
        "W": W,
        "Wq": Wq,
    }


# -----------------------------
# Abas do site
# -----------------------------
aba_instrucoes, aba_medicoes, aba_upload = st.tabs(
    ["📘 Instruções", "📏 Medições Teóricas", "📂 Upload do Dataset"]
)


# -----------------------------
# ABA 1 – INSTRUÇÕES
# -----------------------------
with aba_instrucoes:
    st.header("Como usar este site")

    st.markdown(
        """
        Este site foi desenvolvido para um projeto de avaliação de desempenho de sistemas,
        aplicando **Teoria das Filas (modelo M/M/1)** a um contexto inspirado no site
        **CoinMarketCap**, utilizando um dataset público do Kaggle.

        ### Estrutura das abas

        **1. Instruções (esta aba)**  
        - Explica o objetivo do projeto.  
        - Mostra como usar as demais abas.  

        **2. Medições Teóricas**  
        - Você informa os valores de:
            - Taxa de chegada (λ) em requisições por segundo (req/s);
            - Taxa de serviço (μ) em requisições por segundo (req/s).  
        - O sistema calcula automaticamente:
            - Utilização do servidor (ρ);
            - Número médio de requisições no sistema (L);
            - Número médio na fila (Lq);
            - Tempo médio no sistema (W);
            - Tempo médio de espera na fila (Wq).  

        **3. Upload do Dataset**  
        - Você faz upload de um arquivo **CSV** (por exemplo, o dataset histórico do CoinMarketCap do Kaggle);  
        - Escolhe:
            - A coluna de data;
            - A coluna de volume (por exemplo, `Volume` ou similar);  
        - O sistema:
            - Calcula uma **taxa média de chegadas λ** aproximada, considerando o volume diário;
            - Permite informar um valor de μ (capacidade do servidor);
            - Apresenta as métricas M/M/1 para:
                - Um dia médio;
                - O dia de maior volume (pico).  

        ### Observação importante

        Este site é um **protótipo acadêmico**:
        - Ele não acessa o CoinMarketCap em tempo real;
        - Usa o dataset histórico como aproximação para a carga (volume de operações/consultas);
        - Serve para ilustrar como aplicar **Teoria das Filas** na análise de desempenho de sistemas web.
        """
    )

    st.info(
        "Dica: você pode adaptar os textos desta aba para descrever exatamente o escopo do seu projeto "
        "(como se fosse a introdução/metodologia da sua monografia ou relatório)."
    )


# -----------------------------
# ABA 2 – MEDIÇÕES TEÓRICAS
# -----------------------------
with aba_medicoes:
    st.header("Medições Teóricas (modelo M/M/1)")

    st.markdown(
        """
        Nesta aba você pode fazer **experimentos teóricos** com o modelo M/M/1:

        - **λ (lambda)**: taxa de chegada de requisições (req/s);  
        - **μ (mi)**: taxa de serviço do servidor (req/s).  

        Lembre-se: para o sistema ser estável, é necessário que **λ < μ** (ou seja, ρ = λ/μ < 1).
        """
    )

    col1, col2 = st.columns(2)

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
            "Taxa de serviço μ (req/s)",
            min_value=0.0,
            value=50.0,
            step=1.0,
            help="Quantidade média de requisições que o servidor consegue atender por segundo."
        )

    if st.button("Calcular métricas M/M/1", type="primary"):
        resultados = mm1_metrics(lmbda, mu)

        if resultados is None:
            st.error(
                "Não foi possível calcular as métricas. "
                "Verifique se λ > 0, μ > 0 e λ < μ (o sistema precisa ser estável)."
            )
        else:
            rho = resultados["rho"]
            L = resultados["L"]
            Lq = resultados["Lq"]
            W = resultados["W"]
            Wq = resultados["Wq"]

            st.subheader("Resultados")

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Utilização ρ", f"{rho:.3f}")
                st.metric("Nº médio no sistema L", f"{L:.3f}")
            with col_b:
                st.metric("Nº médio na fila Lq", f"{Lq:.3f}")
            with col_c:
                st.metric("Tempo médio no sistema W (s)", f"{W:.3f}")
                st.metric("Tempo médio na fila Wq (s)", f"{Wq:.3f}")

            st.markdown(
                """
                **Interpretação rápida:**
                - Quanto mais próximo de 1 for ρ, maior o risco de saturação do servidor;
                - L e Lq indicam a quantidade média de requisições “presas” no sistema e na fila;
                - W e Wq indicam quanto tempo, em média, uma requisição gasta esperando e sendo atendida.
                """
            )


# -----------------------------
# ABA 3 – UPLOAD DO DATASET
# -----------------------------
with aba_upload:
    st.header("Upload do Dataset (CoinMarketCap / outro CSV)")

    st.markdown(
        """
        Nesta aba você pode fazer upload de um arquivo **CSV** contendo dados históricos,
        como o dataset do CoinMarketCap (preço, volume, market cap, etc.).

        A ideia é **usar o volume diário como proxy da carga** no sistema
        (por exemplo, número de negociações, consultas ou acessos referentes àquele dia).

        O fluxo geral é:
        1. Fazer upload do CSV;  
        2. Escolher a coluna de data e a coluna de **volume**;  
        3. O sistema calcula uma taxa de chegada **λ (req/s)** aproximada;  
        4. Você informa um valor de **μ (req/s)**;  
        5. São calculadas as métricas M/M/1 para:
            - Um dia médio;
            - O dia de **maior volume** (pior caso / pico).
        """
    )

    arquivo = st.file_uploader(
        "Envie o arquivo CSV",
        type=["csv"],
        help="Use, por exemplo, o dataset histórico do CoinMarketCap baixado do Kaggle."
    )

    if arquivo is not None:
        try:
            df = pd.read_csv(arquivo)
        except Exception as e:
            st.error(f"Erro ao ler o CSV: {e}")
            st.stop()

        st.success("CSV carregado com sucesso!")
        st.write("Visualização inicial dos dados:")
        st.dataframe(df.head())

        colunas = df.columns.tolist()

        st.subheader("Configurações de colunas")

        col_data = st.selectbox(
            "Coluna de data (opcional, mas recomendado)",
            options=["<nenhuma>"] + colunas,
            index=0
        )

        col_volume = st.selectbox(
            "Coluna de volume (quantidade por dia/linha)",
            options=colunas
        )

        st.info(
            "Assumindo que **cada linha** representa um período (por exemplo, um dia) e que a coluna de volume "
            "representa o total de operações/consultas daquele período."
        )

        # Converter data, se selecionada
        if col_data != "<nenhuma>":
            try:
                df[col_data] = pd.to_datetime(df[col_data])
            except Exception:
                st.warning("Não foi possível converter a coluna de data automaticamente. "
                           "Verifique o formato no CSV.")

        # Remover linhas com volume nulo/Nan
        df_limp = df.dropna(subset=[col_volume]).copy()

        # Garantir que o volume é numérico
        df_limp[col_volume] = pd.to_numeric(df_limp[col_volume], errors="coerce")
        df_limp = df_limp.dropna(subset=[col_volume])

        st.subheader("Resumo do volume")

        volume_medio = df_limp[col_volume].mean()
        volume_max = df_limp[col_volume].max()

        st.write(f"**Volume médio por linha** (ex.: por dia): `{volume_medio:.2f}`")
        st.write(f"**Maior volume em uma linha** (pico): `{volume_max:.2f}`")

        st.markdown("---")

        st.subheader("Parâmetros da fila")

        st.markdown(
            """
            Vamos assumir que cada linha representa **um dia** de observação.

            - A taxa de chegada média λ será aproximada como:

              \\[
                  \\lambda_{médio} = \\frac{\\text{volume médio por dia}}{24 \\times 3600}
              \\]

            - E a taxa de chegada no pico será:

              \\[
                  \\lambda_{pico} = \\frac{\\text{maior volume por dia}}{24 \\times 3600}
              \\]
            """
        )

        segundos_dia = 24 * 3600
        lambda_medio = volume_medio / segundos_dia
        lambda_pico = volume_max / segundos_dia

        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.write(f"**λ médio (req/s)** ≈ `{lambda_medio:.6f}`")
        with col_l2:
            st.write(f"**λ pico (req/s)** ≈ `{lambda_pico:.6f}`")

        mu_dataset = st.number_input(
            "Informe a taxa de serviço μ (req/s) do servidor hipotético",
            min_value=0.0,
            value=float(max(lambda_pico * 2, 1.0)),
            step=1.0,
            help="Capacidade média de atendimento do servidor em requisições por segundo."
        )

        if st.button("Calcular métricas com base no dataset", type="primary"):
            res_medio = mm1_metrics(lambda_medio, mu_dataset)
            res_pico = mm1_metrics(lambda_pico, mu_dataset)

            if res_medio is None or res_pico is None:
                st.error(
                    "Não foi possível calcular as métricas. "
                    "Verifique se μ é maior do que λ médio e λ pico (o sistema precisa ser estável)."
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

                st.markdown(
                    """
                    **Interpretação:**

                    - No **dia médio**, ρ indica o quanto o servidor está ocupado em situação típica;
                    - No **dia de pico**, ρ se aproxima de 1 se o servidor estiver perto de saturar;
                    - W e Wq permitem discutir o impacto da carga no **tempo de resposta** percebido pelos usuários;
                    - Você pode variar μ para simular melhorias na infraestrutura (mais recursos, otimização, etc.).
                    """
                )
    else:
        st.info("Envie um arquivo CSV para habilitar as análises desta aba.")
