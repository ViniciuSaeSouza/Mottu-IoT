#!/usr/bin/env python3
"""
Sistema de Persistência de Dados para SmartPatio IoT
Coleta dados MQTT e armazena no Oracle Database + CSV backup
"""

import paho.mqtt.client as mqtt
import csv
import json
import os
import threading
from datetime import datetime
import logging
import oracledb

# Configurações
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
CSV_FILE = "src/output/smartpatio_data.csv"
LOG_FILE = "mqtt_logger.log"

# Configurações Oracle Database
ORACLE_DSN = "oracle.fiap.com.br:1521/orcl"
ORACLE_USER = "RM554456"
ORACLE_PASSWORD = "080995"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SmartPatioDataLogger:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Conexão Oracle
        self.oracle_connection = None
        
        # Estatísticas
        self.stats = {
            'messages_received': 0,
            'messages_saved_oracle': 0,
            'oracle_errors': 0,
            'devices_seen': set(),
            'start_time': datetime.now(),
            'last_message_time': None
        }
        
        # Inicializar conexões
        self.init_oracle_connection()
        self.init_csv_file()
        
    def init_oracle_connection(self):
        """Inicializa a conexão com Oracle Database"""
        try:
            logger.info("Conectando ao Oracle Database...")
            self.oracle_connection = oracledb.connect(
                user=ORACLE_USER,
                password=ORACLE_PASSWORD,
                dsn=ORACLE_DSN
            )
            logger.info("Conectado ao Oracle Database com sucesso!")
            
            # Criar tabela se não existir
            self.create_oracle_table()
            
        except Exception as e:
            logger.error(f"Erro ao conectar Oracle: {e}")
            logger.info("Continuando apenas com CSV...")
            self.oracle_connection = None

    def create_oracle_table(self):
        """Cria a tabela no Oracle se não existir"""
        if not self.oracle_connection:
            return
            
        try:
            cursor = self.oracle_connection.cursor()
            
            # Criar tabela para dados IoT
            create_table_sql = """
                BEGIN
                    EXECUTE IMMEDIATE 'CREATE TABLE SMARTPATIO_IOT_DATA (
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
                    )';
                EXCEPTION
                    WHEN OTHERS THEN
                        IF SQLCODE != -955 THEN  -- Tabela já existe
                            RAISE;
                        END IF;
                END;
            """
            
            cursor.execute(create_table_sql)
            self.oracle_connection.commit()
            cursor.close()
            logger.info("Tabela SMARTPATIO_IOT_DATA criada/verificada")
            
        except Exception as e:
            logger.error(f"Erro ao criar tabela Oracle: {e}")

    def init_csv_file(self):
        """Inicializa o arquivo CSV com cabeçalhos se não existir"""
        # Criar diretório se não existir
        csv_dir = os.path.dirname(CSV_FILE)
        if csv_dir and not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
            logger.info(f"Diretório criado: {csv_dir}")
            
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp',
                    'iso_timestamp', 
                    'topic',
                    'message_type',
                    'device_id',
                    'group_id',
                    'status',
                    'temperature',
                    'device_active',
                    'led_blinking',
                    'buzzer_active',
                    'wifi_rssi',
                    'raw_message'
                ])
            logger.info(f"Arquivo CSV criado: {CSV_FILE}")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback de conexão MQTT"""
        if rc == 0:
            logger.info("Conectado ao broker MQTT")
            # Subscrever aos tópicos do SmartPatio
            topics = [
                "smartpatio/status/+",
                "smartpatio/telemetry/+",
                "smartpatio/commands/+"
            ]
            
            for topic in topics:
                client.subscribe(topic)
                logger.info(f"Subscrito ao tópico: {topic}")
        else:
            logger.error(f"Falha na conexão MQTT: {rc}")

    def on_disconnect(self, client, userdata, rc, properties=None):
        """Callback de desconexão MQTT"""
        logger.warning("Desconectado do broker MQTT")

    def on_message(self, client, userdata, msg):
        """Callback de mensagem MQTT"""
        try:
            topic = msg.topic
            message = msg.payload.decode('utf-8')
            timestamp = datetime.now()
            
            # Incrementar estatísticas
            self.stats['messages_received'] += 1
            self.stats['last_message_time'] = timestamp
            
            logger.info(f"Mensagem recebida: {topic} -> {message}")
            
            # Processar mensagem baseado no tipo
            if "/status/" in topic:
                self.process_status_message(topic, message, timestamp)
            elif "/telemetry/" in topic:
                self.process_telemetry_message(topic, message, timestamp)
            elif "/commands/" in topic:
                self.process_command_message(topic, message, timestamp)
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    def process_status_message(self, topic, message, timestamp):
        """Processa mensagens de status"""
        try:
            # Extrair device_id do tópico
            device_id = topic.split('/')[-1]
            self.stats['devices_seen'].add(device_id)
            
            # Parse da mensagem de status: "GroupID|DeviceID|Status"
            parts = message.split('|')
            
            data = {
                'timestamp': timestamp.timestamp(),
                'iso_timestamp': timestamp.isoformat(),
                'topic': topic,
                'message_type': 'status',
                'device_id': device_id,
                'group_id': parts[0] if len(parts) > 0 else '',
                'status': parts[2] if len(parts) > 2 else '',
                'temperature': None,
                'device_active': None,
                'led_blinking': None,
                'buzzer_active': None,
                'wifi_rssi': None,
                'raw_message': message
            }
            
            self.save_data(data)
            
        except Exception as e:
            logger.error(f"Erro ao processar status: {e}")

    def process_telemetry_message(self, topic, message, timestamp):
        """Processa mensagens de telemetria"""
        try:
            # Extrair device_id do tópico
            device_id = topic.split('/')[-1]
            self.stats['devices_seen'].add(device_id)
            
            # Parse JSON da telemetria
            telemetry = json.loads(message)
            
            data = {
                'timestamp': timestamp.timestamp(),
                'iso_timestamp': timestamp.isoformat(),
                'topic': topic,
                'message_type': 'telemetry',
                'device_id': device_id,
                'group_id': 'SmartPatio',
                'status': None,
                'temperature': telemetry.get('temperature'),
                'device_active': telemetry.get('device_active'),
                'led_blinking': telemetry.get('led_blinking'),
                'buzzer_active': telemetry.get('buzzer_active'),
                'wifi_rssi': telemetry.get('wifi_rssi'),
                'raw_message': message
            }
            
            self.save_data(data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON da telemetria: {e}")
        except Exception as e:
            logger.error(f"Erro ao processar telemetria: {e}")

    def process_command_message(self, topic, message, timestamp):
        """Processa mensagens de comando"""
        try:
            # Extrair device_id do tópico
            device_id = topic.split('/')[-1]
            
            data = {
                'timestamp': timestamp.timestamp(),
                'iso_timestamp': timestamp.isoformat(),
                'topic': topic,
                'message_type': 'command',
                'device_id': device_id,
                'group_id': 'SmartPatio',
                'status': message,  # Comando enviado
                'temperature': None,
                'device_active': None,
                'led_blinking': None,
                'buzzer_active': None,
                'wifi_rssi': None,
                'raw_message': message
            }
            
            self.save_data(data)
            
        except Exception as e:
            logger.error(f"Erro ao processar comando: {e}")

    def save_data(self, data):
        """Salva dados no Oracle Database e CSV (backup)"""
        # Salvar no Oracle Database
        if self.oracle_connection:
            self.save_to_oracle(data)
        
        # Salvar no CSV como backup
        self.save_to_csv(data)

    def save_to_oracle(self, data):
        """Salva dados no Oracle Database"""
        try:
            cursor = self.oracle_connection.cursor()
            
            # Converter valores booleanos para número Oracle (0/1)
            device_active = 1 if data['device_active'] is True else (0 if data['device_active'] is False else None)
            led_blinking = 1 if data['led_blinking'] is True else (0 if data['led_blinking'] is False else None)
            buzzer_active = 1 if data['buzzer_active'] is True else (0 if data['buzzer_active'] is False else None)
            
            # Preparar dados para inserção
            oracle_data = {
                'timestamp_orig': data['timestamp'],
                'iso_timestamp': datetime.fromisoformat(data['iso_timestamp']),
                'topic': data['topic'],
                'message_type': data['message_type'],
                'device_id': data['device_id'],
                'group_id': data['group_id'],
                'status': data['status'],
                'temperature': data['temperature'],
                'device_active': device_active,
                'led_blinking': led_blinking,
                'buzzer_active': buzzer_active,
                'wifi_rssi': data['wifi_rssi'],
                'raw_message': data['raw_message']
            }
            
            # Inserir no Oracle
            cursor.execute("""
                INSERT INTO SMARTPATIO_IOT_DATA 
                (TIMESTAMP_ORIG, ISO_TIMESTAMP, TOPIC, MESSAGE_TYPE, DEVICE_ID, 
                 GROUP_ID, STATUS, TEMPERATURE, DEVICE_ACTIVE, LED_BLINKING, 
                 BUZZER_ACTIVE, WIFI_RSSI, RAW_MESSAGE)
                VALUES (:timestamp_orig, :iso_timestamp, :topic, :message_type, :device_id,
                        :group_id, :status, :temperature, :device_active, :led_blinking,
                        :buzzer_active, :wifi_rssi, :raw_message)
            """, oracle_data)
            
            self.oracle_connection.commit()
            cursor.close()
            
            self.stats['messages_saved_oracle'] += 1
            
        except Exception as e:
            logger.error(f"Erro ao salvar no Oracle: {e}")
            self.stats['oracle_errors'] += 1
            
            # Tentar reconectar se a conexão foi perdida
            if "not connected" in str(e).lower() or "connection" in str(e).lower():
                logger.info("Tentando reconectar ao Oracle...")
                self.init_oracle_connection()

    def save_to_csv(self, data):
        """Salva dados no arquivo CSV"""
        try:
            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    data['timestamp'],
                    data['iso_timestamp'],
                    data['topic'],
                    data['message_type'],
                    data['device_id'],
                    data['group_id'],
                    data['status'],
                    data['temperature'],
                    data['device_active'],
                    data['led_blinking'],
                    data['buzzer_active'],
                    data['wifi_rssi'],
                    data['raw_message']
                ])
        except Exception as e:
            logger.error(f"Erro ao salvar no CSV: {e}")

    def print_stats(self):
        """Imprime estatísticas do sistema"""
        uptime = datetime.now() - self.stats['start_time']
        
        print("\n" + "="*60)
        print("ESTATISTICAS DO SISTEMA SMARTPATIO")
        print("="*60)
        print(f"Tempo de execucao: {uptime}")
        print(f"Mensagens MQTT recebidas: {self.stats['messages_received']}")
        print(f"Mensagens salvas no Oracle: {self.stats['messages_saved_oracle']}")
        print(f"Erros Oracle: {self.stats['oracle_errors']}")
        print(f"Dispositivos unicos: {len(self.stats['devices_seen'])}")
        print(f"Dispositivos: {', '.join(self.stats['devices_seen']) if self.stats['devices_seen'] else 'Nenhum'}")
        
        if self.stats['last_message_time']:
            time_since_last = datetime.now() - self.stats['last_message_time']
            print(f"Ultima mensagem: {time_since_last.total_seconds():.1f}s atras")
        
        # Status das conexões
        oracle_status = "Conectado" if self.oracle_connection else "Desconectado"
        print(f"Oracle Database: {oracle_status}")
        print(f"Arquivo CSV backup: {CSV_FILE}")
        
        # Mostrar resumo do Oracle se conectado
        if self.oracle_connection:
            self.show_oracle_summary()
            
        print("="*60)
        
    def show_oracle_summary(self):
        """Mostra resumo dos dados no Oracle"""
        try:
            cursor = self.oracle_connection.cursor()
            
            # Contar total de registros
            cursor.execute("SELECT COUNT(*) FROM SMARTPATIO_IOT_DATA")
            total_records = cursor.fetchone()[0]
            
            # Contar por tipo de mensagem
            cursor.execute("""
                SELECT MESSAGE_TYPE, COUNT(*) 
                FROM SMARTPATIO_IOT_DATA 
                GROUP BY MESSAGE_TYPE 
                ORDER BY COUNT(*) DESC
            """)
            message_types = cursor.fetchall()
            
            cursor.close()
            
            print(f"Total de registros no Oracle: {total_records}")
            if message_types:
                print("Por tipo de mensagem:")
                for msg_type, count in message_types:
                    print(f"   - {msg_type or 'vazio'}: {count}")
                    
        except Exception as e:
            logger.error(f"Erro ao obter resumo Oracle: {e}")

    def start(self):
        """Inicia o sistema de coleta de dados"""
        logger.info("Iniciando sistema de persistência SmartPatio...")
        
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            logger.info(f"Conectando ao broker {MQTT_BROKER}:{MQTT_PORT}")
            
            # Iniciar thread para estatísticas
            stats_thread = threading.Timer(30.0, self.periodic_stats)
            stats_thread.daemon = True
            stats_thread.start()
            
            # Loop principal
            self.client.loop_forever()
            
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no sistema: {e}")
        finally:
            self.client.disconnect()
            if self.oracle_connection:
                self.oracle_connection.close()
                logger.info("Conexao Oracle fechada")
            self.print_stats()

    def periodic_stats(self):
        """Imprime estatísticas periodicamente"""
        self.print_stats()
        # Reagendar próxima execução
        stats_thread = threading.Timer(30.0, self.periodic_stats)
        stats_thread.daemon = True
        stats_thread.start()

if __name__ == "__main__":
    print("SmartPatio Data Logger - Mottu IoT Challenge")
    print("Salvando dados IoT no Oracle Database + CSV backup")
    print("Pressione Ctrl+C para parar\n")
    
    data_logger = SmartPatioDataLogger()
    data_logger.start()
