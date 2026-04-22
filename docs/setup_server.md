# Setup do Ubuntu Server — Mesa Quant

## 1. Atualizar o sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-pip python3-venv build-essential
```

## 2. Instalar TimescaleDB
```bash
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y gnupg apt-transport-https lsb-release wget
echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/timescaledb.list
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -
sudo apt update && sudo apt install -y timescaledb-2-postgresql-15
sudo timescaledb-tune --quiet --yes
sudo systemctl restart postgresql
```

## 3. Criar banco de dados
```bash
sudo -u postgres psql << SQL
CREATE USER quant WITH PASSWORD 'sua_senha';
CREATE DATABASE mesa_quant OWNER quant;
\c mesa_quant
CREATE EXTENSION IF NOT EXISTS timescaledb;
SQL
```

## 4. Configurar o projeto
```bash
git clone https://github.com/seu-usuario/mesa-quant.git
cd mesa-quant
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp configs/config.example.yaml configs/config.yaml
nano configs/config.yaml
```

## 5. IB Gateway headless
```bash
wget https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh
chmod +x ibgateway-stable-standalone-linux-x64.sh
./ibgateway-stable-standalone-linux-x64.sh
# Rodar headless com Xvfb:
sudo apt install -y xvfb
Xvfb :1 -screen 0 1024x768x24 &
DISPLAY=:1 ibgateway &
```

## 6. Verificar
```bash
python -c "import ib_insync, vectorbt, ccxt; print('✅ Tudo instalado!')"
```
