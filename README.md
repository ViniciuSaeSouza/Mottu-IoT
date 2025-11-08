# 🚦 SmartPatio IoT - Mottu Challenge

Sistema IoT para monitoramento e sinalização de motocicletas em pátios.

## 📌 Resumo da Implementação

✅ **IoT com 2 atuadores distintos**: LED NeoPixel e Buzzer  
✅ **Comunicação MQTT em tempo real**: Via broker público HiveMQ  
✅ **Dashboard web**: Interface simples com dados em tempo real  
✅ **Persistência de dados**: Oracle Database + CSV backup  
✅ **Banco de dados**: Oracle Database FIAP integrado  
✅ **Teste funcional**: Scripts de demonstração e validação  

---

## 🏗️ Arquitetura do Sistema

```
ESP32 (SmartPatio)
├── 💡 LED NeoPixel (sinalização visual)
├── 🔊 Buzzer (sinalização sonora)
├── 📡 WiFi + MQTT (comunicação)
└── 📊 Telemetria (status em tempo real)
    ↓
🌐 Broker MQTT (broker.hivemq.com)
    ↓
├── 🖥️ Dashboard Web (visualização)
├── 💾 Data Logger (Oracle + CSV)
├── 🗃️ Oracle Database (persistência principal)
└── 🧪 Scripts de Teste (demonstração)
```

---

## 🚀 Configuração Rápida

### 1. Hardware/Simulação
- **Opção A**: Use o simulador [Wokwi](https://wokwi.com/) com o código `src/main.cpp`
- **Opção B**: ESP32 real com LED NeoPixel (pino 2) e Buzzer (pino 4)

### 2. Software
```bash
# Instalar dependências Python
./install.sh        # Linux/Mac
install.bat         # Windows

# Ou manualmente:
pip install paho-mqtt matplotlib pandas numpy oracledb
```

### 3. Execução
```bash
# 1. Subir o ESP32/Wokwi com src/main.cpp
# 2. Teste interativo
python demo.py

# 3. Demonstração automática
python demo.py auto

# 4. Data logger com Oracle Database
python data_logger.py

# 5. Abrir dashboard/index.html no navegador
```

---

## 🧪 Demonstração Funcional

### Cenário de Teste
1. **Dispositivo inativo**: LED verde fixo, buzzer desligado
2. **Comando ACTIVATE**: LED pisca (verde/vermelho/azul) + buzzer toca melodia
3. **Comando DEACTIVATE**: Volta ao estado inativo
4. **Telemetria**: Dados enviados a cada 5 segundos via MQTT

### Scripts de Teste
- `demo.py` - Interface interativa para envio de comandos
- `data_logger.py` - Coleta e armazena dados no Oracle Database + CSV backup
- `dashboard/index.html` - Visualização web em tempo real

---

## 📊 Dados e Métricas

### Telemetria Coletada
```json
{
  "device_id": "TESTE",
  "timestamp": 1696175431000,
  "device_active": true,
  "led_blinking": true,
  "buzzer_active": true,
  "wifi_rssi": -45
}
```

### Persistência
- **Principal**: Oracle Database (tabela `SMARTPATIO_IOT_DATA`)
- **Backup**: CSV com timestamp, tópico, dados JSON
- **Localização CSV**: `src/output/smartpatio_data.csv`
- **Conexão Oracle**: `oracle.fiap.com.br:1521/orcl`
- **Frequência**: Todos os eventos MQTT são registrados em tempo real

---

## �️ Oracle Database Integration

### Configuração do Banco
- **Servidor**: oracle.fiap.com.br:1521/orcl
- **Usuário**: RM554456
- **Tabela Principal**: `SMARTPATIO_IOT_DATA`

### Estrutura da Tabela
```sql
CREATE TABLE SMARTPATIO_IOT_DATA (
    ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    TIMESTAMP_ORIG NUMBER,
    ISO_TIMESTAMP TIMESTAMP,
    TOPIC VARCHAR2(200),
    MESSAGE_TYPE VARCHAR2(50),
    DEVICE_ID VARCHAR2(50),
    GROUP_ID VARCHAR2(50),
    STATUS VARCHAR2(100),
    TEMPERATURE NUMBER,
    DEVICE_ACTIVE NUMBER(1),
    LED_BLINKING NUMBER(1), 
    BUZZER_ACTIVE NUMBER(1),
    WIFI_RSSI NUMBER,
    RAW_MESSAGE CLOB,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Funcionalidades
- ✅ **Conexão automática** ao iniciar o data_logger
- ✅ **Criação automática** da tabela se não existir
- ✅ **Reconexão automática** em caso de perda de conexão
- ✅ **Backup em CSV** como redundância
- ✅ **Logs detalhados** de todas as operações
- ✅ **Estatísticas em tempo real** do banco

---

## �📡 Comunicação MQTT

### Tópicos
```
smartpatio/commands/TESTE   → Comandos (ACTIVATE/DEACTIVATE/RESET)
smartpatio/status/TESTE     → Status do dispositivo
smartpatio/telemetry/TESTE  → Dados de telemetria JSON
```

### Broker
- **Host**: broker.hivemq.com
- **Porta**: 1883 (público, sem autenticação)
- **Protocolo**: MQTT v3.1.1

---

## 🎯 Atendimento aos Requisitos

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| **3 sensores/atuadores** | ✅ | LED NeoPixel + Buzzer + WiFi RSSI |
| **Comunicação MQTT** | ✅ | Tempo real via HiveMQ |
| **Dashboard simples** | ✅ | HTML5 + JavaScript + Chart.js |
| **Persistência dados** | ✅ | Oracle Database + CSV backup |
| **Banco de dados** | ✅ | Oracle Database FIAP integrado |
| **Teste funcional** | ✅ | Scripts demo + logs automáticos |

---

## 📁 Estrutura do Projeto

```
smartPatio/
├── src/
│   └── main.cpp              # Firmware ESP32
├── dashboard/
│   └── index.html            # Dashboard web
├── demo.py                   # Script de teste interativo
├── data_logger.py            # Sistema de persistência Oracle + CSV
├── requirements.txt          # Dependências Python
├── install.bat / install.sh  # Scripts de instalação
└── README.md                 # Esta documentação
```

---

## 🔧 Tecnologias Utilizadas

- **Hardware**: ESP32, LED NeoPixel, Buzzer
- **Firmware**: Arduino/PlatformIO, WiFi, MQTT
- **Backend**: Python, paho-mqtt, pandas, oracledb
- **Banco de Dados**: Oracle Database 19c
- **Frontend**: HTML5, JavaScript, Chart.js
- **Comunicação**: MQTT (HiveMQ Cloud)
- **Dados**: Oracle Database, CSV, JSON

---

## 📈 Resultados Esperados

### Performance
- **Latência MQTT**: < 500ms (rede local)
- **Frequência telemetria**: 5 segundos
- **Disponibilidade**: 99%+ (dependente da rede)

### Funcionalidades
- ✅ Ativação/desativação remota
- ✅ Feedback visual (LED colorido)
- ✅ Feedback sonoro (melodia)
- ✅ Monitoramento em tempo real
- ✅ Histórico persistente
- ✅ Dashboard responsivo

---

## 🎥 Demonstração

O sistema funciona com:
1. **ESP32/Wokwi** executando o firmware
2. **Dashboard** mostrando dados em tempo real
3. **Scripts Python** para controle e logging
4. **Comunicação MQTT** conectando tudo

**Resultado**: Sistema IoT funcional demonstrando integração completa entre hardware, comunicação, interface web e banco de dados Oracle.

---

## 📊 Monitoramento e Logs

### Data Logger - Saída do Sistema
```
SmartPatio Data Logger - Mottu IoT Challenge
Salvando dados IoT no Oracle Database + CSV backup
Pressione Ctrl+C para parar

Conectando ao Oracle Database...
Conectado ao Oracle Database com sucesso!
Tabela SMARTPATIO_IOT_DATA criada/verificada
Iniciando sistema de persistência SmartPatio...
Conectando ao broker broker.hivemq.com:1883
Conectado ao broker MQTT
Subscrito ao tópico: smartpatio/status/+
Subscrito ao tópico: smartpatio/telemetry/+
Subscrito ao tópico: smartpatio/commands/+
Mensagem recebida: smartpatio/telemetry/TESTE -> {"device_id":"TESTE",...}
```

### Estatísticas Automáticas
O sistema exibe a cada 30 segundos:
- Tempo de execução
- Mensagens MQTT recebidas
- Mensagens salvas no Oracle
- Erros Oracle (se houver)
- Dispositivos únicos detectados
- Status da conexão Oracle
- Total de registros no banco

### Arquivos de Log
- **mqtt_logger.log**: Log detalhado de todas as operações
- **src/output/smartpatio_data.csv**: Backup em CSV dos dados

---

## 👥 Equipe

- **Laura de Oliveira Cintra** - RM 558843
- **Maria Eduarda Alves da Paixão** - RM 558832
- **Vinicius Saes de Souza** - RM 554456

---
