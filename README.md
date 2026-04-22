# 📈 Mesa Quant

Mini mesa de trading quantitativo focada em mercados americanos: Ações, Opções, Futuros e Crypto.

## 🏗️ Arquitetura

```
Server
├── Coleta de Dados     → IB TWS API + CCXT
├── Banco de Dados      → TimescaleDB (PostgreSQL)
├── Backtesting         → VectorBT
├── Execução            → ib_insync
└── Monitoramento       → Grafana
```

## 📦 Mercados

| Mercado | Fonte | Status |
|---|---|---|
| Ações EUA | IB TWS API + yfinance | 🔧 Em desenvolvimento |
| Opções EUA | IB TWS API (OPRA) | 🔧 Em desenvolvimento |
| Futuros EUA | IB TWS API (CME/CBOT/NYMEX) | 🔧 Em desenvolvimento |
| Crypto | CCXT | 🔧 Em desenvolvimento |

## 🗂️ Estrutura do Projeto

```
mesa-quant/
├── src/
│   ├── collectors/     # Coleta e ingestão de dados
│   ├── backtest/       # Engine de backtesting
│   ├── execution/      # Execução de ordens
│   ├── risk/           # Gestão de risco
│   └── utils/          # Utilitários gerais
├── data/
│   ├── raw/            # Dados brutos
│   └── processed/      # Dados processados
├── notebooks/          # Jupyter notebooks de análise
├── configs/            # Configurações do sistema
├── tests/              # Testes automatizados
└── docs/               # Documentação técnica
```

## 🚀 Roadmap

- [ ] **Fase 1** — Infraestrutura (Ubuntu Server + TimescaleDB)
- [ ] **Fase 2** — Coleta de dados (IB API + CCXT)
- [ ] **Fase 3** — Backtesting (VectorBT)
- [ ] **Fase 4** — Paper Trading
- [ ] **Fase 5** — Live Trading

## ⚙️ Requisitos

- Python 3.10+
- Ubuntu Server 22.04+
- Interactive Brokers TWS / IB Gateway
- TimescaleDB

## 📥 Instalação

```bash
git clone https://github.com/seu-usuario/mesa-quant.git
cd mesa-quant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp configs/config.example.yaml configs/config.yaml
# Edite configs/config.yaml com suas credenciais
```

## 📄 Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuições

Projeto pessoal de aprendizado em quant trading. 
Issues e sugestões são bem-vindas!
