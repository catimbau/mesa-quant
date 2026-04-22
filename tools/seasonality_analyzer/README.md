# 📊 Market Seasonality Analyzer

Ferramenta de research para análise de padrões sazonais em mercados financeiros.

## Funcionalidades

- Retorno médio e mediano por mês
- Win rate (probabilidade histórica de fechar em alta)
- Volatilidade mensal (desvio padrão)
- Teste de significância estatística (p-valor)
- Dados ajustados por splits e dividendos

## Como rodar

```bash
cd tools/seasonality_analyzer
pip install -r requirements.txt
streamlit run app.py
```

## Fonte de dados

Yahoo Finance via biblioteca `yfinance`. Suporta tickers americanos 
(SPY, AAPL, etc.) e brasileiros com sufixo `.SA` (PETR4.SA, VALE3.SA).

## Disclaimer

Ferramenta de uso educacional e de research. Não constitui 
recomendação de investimento.
