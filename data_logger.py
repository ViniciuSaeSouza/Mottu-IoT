#!/usr/bin/env python3
"""
Sistema de Persistência de Dados para SmartPatio IoT
Coleta dados MQTT e armazena em arquivo CSV
"""

import paho.mqtt.client as mqtt
import csv
import json
import os
import threading
from datetime import datetime
import logging

# Configurações
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
CSV_FILE = "src/output/smartpatio_data.csv"
LOG_FILE = "mqtt_logger.log"

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
        
        # Estatísticas
        self.stats = {
            'messages_received': 0,
            'devices_seen': set(),
            'start_time': datetime.now(),
            'last_message_time': None
        }
        
        # Inicializar arquivo CSV se não existir
        self.init_csv_file()
        
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
            
            self.save_to_csv(data)
            
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
            
            self.save_to_csv(data)
            
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
            
            self.save_to_csv(data)
            
        except Exception as e:
            logger.error(f"Erro ao processar comando: {e}")

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
        
        print("\n" + "="*50)
        print("📊 ESTATÍSTICAS DO SISTEMA")
        print("="*50)
        print(f"⏱️  Tempo de execução: {uptime}")
        print(f"📨 Mensagens recebidas: {self.stats['messages_received']}")
        print(f"📱 Dispositivos únicos: {len(self.stats['devices_seen'])}")
        print(f"🔧 Dispositivos: {', '.join(self.stats['devices_seen']) if self.stats['devices_seen'] else 'Nenhum'}")
        
        if self.stats['last_message_time']:
            time_since_last = datetime.now() - self.stats['last_message_time']
            print(f"📡 Última mensagem: {time_since_last.total_seconds():.1f}s atrás")
        
        print(f"💾 Arquivo de dados: {CSV_FILE}")
        print("="*50)

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
            self.print_stats()

    def periodic_stats(self):
        """Imprime estatísticas periodicamente"""
        self.print_stats()
        # Reagendar próxima execução
        stats_thread = threading.Timer(30.0, self.periodic_stats)
        stats_thread.daemon = True
        stats_thread.start()

if __name__ == "__main__":
    print("🚦 SmartPatio Data Logger - Mottu IoT Challenge")
    print("Pressione Ctrl+C para parar\n")
    
    data_logger = SmartPatioDataLogger()
    data_logger.start()
