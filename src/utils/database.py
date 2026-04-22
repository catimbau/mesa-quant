"""
Database Manager — TimescaleDB
"""
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
import yaml


class DatabaseManager:
    def __init__(self, config_path="configs/config.yaml"):
        with open(config_path) as f:
            cfg = yaml.safe_load(f)["database"]
        conn_str = (
            f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}"
            f"@{cfg['host']}:{cfg['port']}/{cfg['name']}"
        )
        self.engine = create_engine(conn_str)
        logger.info("Database manager inicializado")

    def create_ohlcv_table(self, table_name="ohlcv"):
        """Cria tabela OHLCV como hypertable no TimescaleDB."""
        with self.engine.connect() as conn:
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    time        TIMESTAMPTZ NOT NULL,
                    symbol      TEXT NOT NULL,
                    exchange    TEXT NOT NULL,
                    open        DOUBLE PRECISION,
                    high        DOUBLE PRECISION,
                    low         DOUBLE PRECISION,
                    close       DOUBLE PRECISION,
                    volume      DOUBLE PRECISION,
                    PRIMARY KEY (time, symbol, exchange)
                );
            """))
            conn.execute(text(f"""
                SELECT create_hypertable('{table_name}', 'time', if_not_exists => TRUE);
            """))
            conn.commit()
        logger.info(f"Tabela {table_name} criada/verificada")

    def save_ohlcv(self, df: pd.DataFrame, table_name="ohlcv"):
        df.to_sql(table_name, self.engine, if_exists="append",
                  index=True, index_label="time", method="multi")
        logger.info(f"{len(df)} registros salvos em {table_name}")

    def load_ohlcv(self, symbol: str, start: str, end: str,
                   table_name="ohlcv") -> pd.DataFrame:
        query = f"""
            SELECT * FROM {table_name}
            WHERE symbol = '{symbol}'
              AND time BETWEEN '{start}' AND '{end}'
            ORDER BY time ASC;
        """
        return pd.read_sql(query, self.engine, index_col="time", parse_dates=["time"])
