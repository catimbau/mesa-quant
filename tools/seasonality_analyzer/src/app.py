"""
Market Seasonality Analyzer
Analisa padrões históricos e probabilidades estatísticas por mês.

Parte do projeto Mesa Quant — ferramenta auxiliar para research de sazonalidade.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy import stats

# --- Configurações Iniciais ---
st.set_page_config(
    page_title="Market Seasonality Analyzer",
    layout="wide",
    page_icon="📈"
)

# Estilo CSS ajustado para tema escuro/claro
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Market Seasonality Analyzer")
st.markdown("Analise padrões históricos e probabilidades estatísticas por mês.")

# --- Constantes ---
MESES_MAP = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}
MIN_SAMPLES_WARNING = 5  # Anos mínimos para não exibir aviso de baixa amostra
SIGNIFICANCE_LEVEL = 0.05  # p-valor para considerar sazonalidade estatisticamente significativa

# --- Sidebar (Entradas do Usuário) ---
st.sidebar.header("Configurações da Análise")
ticker = st.sidebar.text_input(
    "Ticker (ex: SPY, AAPL, PETR4.SA)",
    value="SPY"
).upper().strip()
anos = st.sidebar.slider(
    "Período de histórico (anos)",
    min_value=2,
    max_value=30,
    value=10
)

show_median = st.sidebar.checkbox("Mostrar mediana (além da média)", value=True)
show_significance = st.sidebar.checkbox("Destacar meses estatisticamente significativos", value=True)


# --- Função de Coleta com Cache ---
@st.cache_data(show_spinner="Baixando dados históricos...")
def load_financial_data(symbol: str, period_years: int) -> pd.DataFrame:
    """
    Baixa dados históricos do Yahoo Finance com ajuste automático
    por dividendos e splits (auto_adjust=True).
    """
    end_date = datetime.now()
    # Usa relativedelta para evitar bugs em 29/fev
    start_date = end_date - relativedelta(years=period_years)

    df = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        auto_adjust=True,  # CRÍTICO: ajusta por splits e dividendos
        progress=False
    )
    return df


def calc_monthly_stats(df_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula estatísticas mensais: média, mediana, win rate, volatilidade,
    número de amostras e teste de significância.
    """
    grouped = df_stats.groupby(['Mês_Num', 'Mês'])['Retorno']

    stats_df = pd.DataFrame({
        'Retorno_Medio': grouped.mean() * 100,
        'Retorno_Mediano': grouped.median() * 100,
        'Volatilidade': grouped.std() * 100,
        'Probabilidade': grouped.apply(lambda x: (x > 0).sum() / len(x) * 100),
        'N_Amostras': grouped.count(),
    })

    # Teste t de uma amostra: média é estatisticamente diferente de zero?
    p_values = grouped.apply(
        lambda x: stats.ttest_1samp(x, 0).pvalue if len(x) >= 3 else np.nan
    )
    stats_df['p_valor'] = p_values
    stats_df['Significativo'] = stats_df['p_valor'] < SIGNIFICANCE_LEVEL

    return stats_df.reset_index()


# --- Execução Principal ---
try:
    data = load_financial_data(ticker, anos)

    # Validação explícita dos dados
    if data.empty:
        st.error(f"❌ Ticker '{ticker}' não encontrado ou sem dados no período selecionado.")
        st.info("💡 Verifique o símbolo. Exemplos válidos: SPY, AAPL, MSFT, PETR4.SA, VALE3.SA")
        st.stop()

    # Trata MultiIndex que o yfinance pode retornar
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Com auto_adjust=True, 'Close' já está ajustado por splits e dividendos
    if 'Close' not in data.columns:
        st.error("❌ Coluna 'Close' não encontrada nos dados.")
        st.stop()

    price_col = 'Close'

    # 1. Transformando dados diários em mensais (último preço do mês)
    monthly_prices = data[price_col].resample('ME').last()

    # 2. Calculando retornos mensais
    monthly_returns = monthly_prices.pct_change().dropna()

    if len(monthly_returns) < 12:
        st.error(f"❌ Apenas {len(monthly_returns)} meses de dados — insuficiente para análise sazonal.")
        st.stop()

    # 3. Organizando o DataFrame de trabalho
    df_stats = monthly_returns.to_frame(name='Retorno')
    df_stats['Mês_Num'] = df_stats.index.month
    df_stats['Mês'] = df_stats['Mês_Num'].map(MESES_MAP)

    # --- Cálculos Estatísticos ---
    plot_data = calc_monthly_stats(df_stats)

    # Ordena pelos meses corretamente
    plot_data = plot_data.sort_values('Mês_Num').reset_index(drop=True)

    # --- Aviso de baixa amostra ---
    min_samples = plot_data['N_Amostras'].min()
    if anos < MIN_SAMPLES_WARNING:
        st.warning(
            f"⚠️ **Atenção:** apenas {anos} anos de histórico. "
            f"Cada mês tem no mínimo {min_samples} observações. "
            "Resultados têm **baixa significância estatística** — use com cautela."
        )

    # --- Info geral ---
    st.markdown(f"### 📈 {ticker} — Últimos {anos} anos")
    col_info1, col_info2, col_info3 = st.columns(3)
    col_info1.metric("Total de meses", len(monthly_returns))
    col_info2.metric("Retorno médio mensal", f"{monthly_returns.mean() * 100:.2f}%")
    col_info3.metric("Volatilidade mensal", f"{monthly_returns.std() * 100:.2f}%")

    st.divider()

    # --- Layout de Colunas ---
    col1, col2 = st.columns([2, 1])

    with col1:
        # Gráfico de Retorno Médio (e Mediano, se ativado)
        fig = go.Figure()

        # Define cores baseadas em significância estatística (se ativado)
        if show_significance:
            colors = [
                '#2ecc71' if (r > 0 and sig) else
                '#e74c3c' if (r < 0 and sig) else
                '#95a5a6'  # Cinza para não-significativos
                for r, sig in zip(plot_data['Retorno_Medio'], plot_data['Significativo'])
            ]
        else:
            colors = [
                '#2ecc71' if x > 0 else '#e74c3c'
                for x in plot_data['Retorno_Medio']
            ]

        fig.add_trace(go.Bar(
            x=plot_data['Mês'],
            y=plot_data['Retorno_Medio'],
            marker_color=colors,
            name='Média',
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Retorno Médio: %{y:.2f}%<br>"
                "Amostras: %{customdata[0]}<br>"
                "p-valor: %{customdata[1]:.3f}<br>"
                "<extra></extra>"
            ),
            customdata=plot_data[['N_Amostras', 'p_valor']].values
        ))

        # Adiciona mediana como linha sobreposta, se ativado
        if show_median:
            fig.add_trace(go.Scatter(
                x=plot_data['Mês'],
                y=plot_data['Retorno_Mediano'],
                mode='markers+lines',
                name='Mediana',
                line=dict(color='#3498db', width=2, dash='dot'),
                marker=dict(size=10, symbol='diamond'),
                hovertemplate="<b>%{x}</b><br>Mediana: %{y:.2f}%<extra></extra>"
            ))

        title_suffix = " (cinza = não significativo)" if show_significance else ""
        fig.update_layout(
            title=f"Sazonalidade: Retorno Mensal ({ticker}){title_suffix}",
            yaxis_title="Retorno (%)",
            xaxis_title="",
            template="plotly_white",
            height=450,
            hovermode="x unified"
        )
        st.plotly_chart(fig, width='stretch')

    with col2:
        # Tabela de Probabilidade e Amostras
        st.subheader("📋 Estatísticas por Mês")
        st.caption(f"Significância com p < {SIGNIFICANCE_LEVEL}")

        display_df = plot_data[['Mês', 'Probabilidade', 'N_Amostras', 'Significativo']].copy()
        display_df['Probabilidade'] = display_df['Probabilidade'].map('{:.1f}%'.format)
        display_df['Significativo'] = display_df['Significativo'].map({True: '✅', False: '—'})
        display_df.columns = ['Mês', 'Win Rate', 'N', 'Sig.']

        st.dataframe(
            display_df.set_index('Mês'),
            width='stretch',
            height=460
        )

    # --- Gráfico de Volatilidade ---
    st.divider()
    st.subheader("⚡ Risco: Volatilidade Mensal")
    st.write(
        "Desvio padrão dos retornos mensais — quanto maior a barra, "
        "mais imprevisível foi o comportamento desse mês historicamente."
    )

    fig_vol = go.Figure()
    fig_vol.add_trace(go.Bar(
        x=plot_data['Mês'],
        y=plot_data['Volatilidade'],
        marker_color='#f39c12',
        hovertemplate="<b>%{x}</b><br>Desvio Padrão: %{y:.2f}%<extra></extra>"
    ))
    fig_vol.update_layout(
        yaxis_title="Desvio Padrão (%)",
        template="plotly_white",
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_vol, width='stretch')

    # --- Insights Finais ---
    st.divider()
    st.subheader("🎯 Destaques")

    melhor_mes = plot_data.loc[plot_data['Retorno_Medio'].idxmax()]
    pior_mes = plot_data.loc[plot_data['Retorno_Medio'].idxmin()]
    maior_prob = plot_data.loc[plot_data['Probabilidade'].idxmax()]
    menor_vol = plot_data.loc[plot_data['Volatilidade'].idxmin()]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "🏆 Melhor mês (média)",
        melhor_mes['Mês'],
        f"{melhor_mes['Retorno_Medio']:.2f}%"
    )
    c2.metric(
        "🔻 Pior mês (média)",
        pior_mes['Mês'],
        f"{pior_mes['Retorno_Medio']:.2f}%",
        delta_color="inverse"
    )
    c3.metric(
        "🎯 Maior win rate",
        maior_prob['Mês'],
        f"{maior_prob['Probabilidade']:.1f}%"
    )
    c4.metric(
        "🛡️ Menor volatilidade",
        menor_vol['Mês'],
        f"{menor_vol['Volatilidade']:.2f}%"
    )

    # --- Nota sobre significância ---
    if show_significance:
        sig_months = plot_data[plot_data['Significativo']]['Mês'].tolist()
        if sig_months:
            st.info(
                f"📊 **Meses com sazonalidade estatisticamente significativa** "
                f"(p < {SIGNIFICANCE_LEVEL}): {', '.join(sig_months)}"
            )
        else:
            st.info(
                "📊 Nenhum mês apresenta sazonalidade estatisticamente significativa "
                f"com p < {SIGNIFICANCE_LEVEL} — os padrões observados podem ser apenas ruído."
            )

    # --- Disclaimer ---
    st.divider()
    st.caption(
        "⚠️ **Disclaimer:** Esta análise é baseada em dados históricos e "
        "não constitui recomendação de investimento. Padrões passados não garantem "
        "comportamento futuro. Dados ajustados por dividendos e splits via yfinance."
    )

except KeyError as e:
    st.error(f"❌ Coluna esperada não encontrada nos dados: {e}")
except ValueError as e:
    st.error(f"❌ Dados inválidos ou período incorreto: {e}")
except ConnectionError:
    st.error("❌ Erro de conexão. Verifique sua internet e tente novamente.")
except Exception as e:
    st.error(f"❌ Erro inesperado: {e}")
    with st.expander("Detalhes técnicos (para debug)"):
        st.exception(e)