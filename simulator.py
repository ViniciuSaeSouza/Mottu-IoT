#!/usr/bin/env python3
"""
Simulador de Múltiplos Dispositivos IoT para SmartPatio
Simula 3 dispositivos ESP32 em paralelo para demonstração
"""

import paho.mqtt.client as mqtt
import json
import random
import time
import threading
from datetime import datetime
import logging

# Configurações
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
NUM_DEVICES = 3

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(threadName)s] - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class SmartPatioSimulator:
    def __init__(self, device_id):
        self.device_id = device_id
        self.group_id = "SmartPatio"
        
        # Estado do dispositivo
        self.state = {
            'connected': False,
            'active': False,
            'led_blinking': False,
            'buzzer_active': False,
            'wifi_rssi': random.randint(-80, -40)
        }
        
        # Cliente MQTT
        self.client = mqtt.Client(client_id=f"Simulator-{device_id}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Tópicos
        self.topic_status = f"smartpatio/status/{device_id}"
        self.topic_telemetry = f"smartpatio/telemetry/{device_id}"
        self.topic_commands = f"smartpatio/commands/{device_id}"
        
        # Threads de controle
        self.running = False
        self.telemetry_thread = None

    def on_connect(self, client, userdata, flags, rc):
        """Callback de conexão MQTT"""
        if rc == 0:
            logger.info(f"[{self.device_id}] Conectado ao broker MQTT")
            self.state['connected'] = True
            
            # Subscrever aos comandos
            client.subscribe(self.topic_commands)
            logger.info(f"[{self.device_id}] Subscrito a {self.topic_commands}")
            
            # Publicar status de conexão
            self.publish_status("CONNECTED")
            
        else:
            logger.error(f"[{self.device_id}] Falha na conexão MQTT: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback de desconexão MQTT"""
        logger.warning(f"[{self.device_id}] Desconectado do broker MQTT")
        self.state['connected'] = False

    def on_message(self, client, userdata, msg):
        """Callback de mensagem MQTT"""
        try:
            topic = msg.topic
            message = msg.payload.decode('utf-8')
            
            logger.info(f"[{self.device_id}] Comando recebido: {message}")
            
            if message == "ACTIVATE":
                self.activate_device()
            elif message == "DEACTIVATE":
                self.deactivate_device()
            elif message == "RESET":
                self.reset_device()
                
        except Exception as e:
            logger.error(f"[{self.device_id}] Erro ao processar comando: {e}")

    def activate_device(self):
        """Ativa o dispositivo (simula ativação)"""
        logger.info(f"[{self.device_id}] 🟢 Ativando dispositivo...")
        self.state['active'] = True
        self.state['led_blinking'] = True
        self.state['buzzer_active'] = True
        self.publish_status("DEVICE_ACTIVE")

    def deactivate_device(self):
        """Desativa o dispositivo (simula desativação)"""
        logger.info(f"[{self.device_id}] 🔴 Desativando dispositivo...")
        self.state['active'] = False
        self.state['led_blinking'] = False
        self.state['buzzer_active'] = False
        self.publish_status("DEVICE_DEACTIVATED")

    def reset_device(self):
        """Reinicia o dispositivo (simula reset)"""
        logger.info(f"[{self.device_id}] 🔄 Reiniciando dispositivo...")
        self.publish_status("RESTARTING")
        
        # Simula reinicialização
        time.sleep(2)
        
        # Reconecta e envia status inicial
        self.state['active'] = False
        self.state['led_blinking'] = False
        self.state['buzzer_active'] = False
        self.publish_status("CONNECTED")

    def publish_status(self, status):
        """Publica status do dispositivo"""
        if self.client.is_connected():
            message = f"{self.group_id}|{self.device_id}|{status}"
            self.client.publish(self.topic_status, message)
            logger.info(f"[{self.device_id}] 📤 Status: {status}")

    def simulate_wifi_rssi(self):
        """Simula variação do sinal Wi-Fi"""
        variation = random.randint(-5, 5)
        self.state['wifi_rssi'] += variation
        
        # Limites do RSSI
        if self.state['wifi_rssi'] < -90:
            self.state['wifi_rssi'] = -90
        elif self.state['wifi_rssi'] > -30:
            self.state['wifi_rssi'] = -30

    def publish_telemetry(self):
        """Publica dados de telemetria"""
        if not self.client.is_connected():
            return
            
        # Simula sensor Wi-Fi
        self.simulate_wifi_rssi()
        
        # Cria dados de telemetria
        telemetry = {
            "device_id": self.device_id,
            "timestamp": int(time.time() * 1000),
            "device_active": self.state['active'],
            "led_blinking": self.state['led_blinking'],
            "buzzer_active": self.state['buzzer_active'],
            "wifi_rssi": self.state['wifi_rssi']
        }
        
        message = json.dumps(telemetry)
        self.client.publish(self.topic_telemetry, message)
        
        logger.info(f"[{self.device_id}] 📊 Telemetria: "
                   f"RSSI={telemetry['wifi_rssi']}dBm, Ativo={telemetry['device_active']}")

    def telemetry_loop(self):
        """Loop principal de telemetria"""
        while self.running:
            try:
                if self.state['connected']:
                    self.publish_telemetry()
                time.sleep(5)  # Publica a cada 5 segundos
            except Exception as e:
                logger.error(f"[{self.device_id}] Erro na telemetria: {e}")

    def start(self):
        """Inicia o simulador"""
        logger.info(f"[{self.device_id}] 🚀 Iniciando simulador...")
        
        try:
            # Conectar ao MQTT
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            
            # Iniciar telemetria
            self.running = True
            self.telemetry_thread = threading.Thread(
                target=self.telemetry_loop,
                name=f"Telemetry-{self.device_id}"
            )
            self.telemetry_thread.daemon = True
            self.telemetry_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"[{self.device_id}] Erro ao iniciar: {e}")
            return False

    def stop(self):
        """Para o simulador"""
        logger.info(f"[{self.device_id}] 🛑 Parando simulador...")
        
        self.running = False
        
        if self.client.is_connected():
            self.publish_status("DISCONNECTED")
            self.client.loop_stop()
            self.client.disconnect()

class MultiDeviceSimulator:
    """Gerenciador de múltiplos simuladores"""
    
    def __init__(self, num_devices=3):
        self.num_devices = num_devices
        self.simulators = []
        
        # Criar simuladores
        for i in range(num_devices):
            device_id = f"SIM{i+1:02d}"  # SIM01, SIM02, SIM03
            simulator = SmartPatioSimulator(device_id)
            self.simulators.append(simulator)

    def start_all(self):
        """Inicia todos os simuladores"""
        logger.info(f"🚀 Iniciando {self.num_devices} simuladores SmartPatio...")
        
        started = 0
        for simulator in self.simulators:
            if simulator.start():
                started += 1
                time.sleep(1)  # Delay entre inicializações
        
        logger.info(f"✅ {started}/{self.num_devices} simuladores iniciados com sucesso!")
        return started == self.num_devices

    def stop_all(self):
        """Para todos os simuladores"""
        logger.info("🛑 Parando todos os simuladores...")
        
        for simulator in self.simulators:
            simulator.stop()
        
        logger.info("✅ Todos os simuladores foram parados!")

    def print_status(self):
        """Imprime status de todos os dispositivos"""
        print("\n" + "="*60)
        print("📊 STATUS DOS DISPOSITIVOS SIMULADOS")
        print("="*60)
        
        for simulator in self.simulators:
            status = "🟢 ATIVO" if simulator.state['active'] else "🔴 INATIVO"
            connection = "🔗 CONECTADO" if simulator.state['connected'] else "❌ DESCONECTADO"
            rssi = f"{simulator.state['wifi_rssi']}dBm"
            
            print(f"📱 {simulator.device_id}: {status} | {connection} | 📡 {rssi}")
        
        print("="*60)

    def run(self):
        """Executa o simulador com interface de controle"""
        if not self.start_all():
            logger.error("Falha ao iniciar simuladores!")
            return
        
        print("\n🚦 SIMULADOR SMARTPATIO - MOTTU IOT CHALLENGE")
        print("="*50)
        print("Comandos disponíveis:")
        print("  status - Mostra status dos dispositivos")
        print("  activate <device> - Ativa dispositivo (ex: activate SIM01)")
        print("  deactivate <device> - Desativa dispositivo")
        print("  reset <device> - Reinicia dispositivo")
        print("  quit - Sair do simulador")
        print("="*50)
        
        try:
            while True:
                command = input("\n📟 SmartPatio> ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "status":
                    self.print_status()
                elif command.startswith("activate "):
                    device_id = command.split()[1].upper()
                    self.send_command(device_id, "ACTIVATE")
                elif command.startswith("deactivate "):
                    device_id = command.split()[1].upper()
                    self.send_command(device_id, "DEACTIVATE")
                elif command.startswith("reset "):
                    device_id = command.split()[1].upper()
                    self.send_command(device_id, "RESET")
                elif command == "":
                    continue
                else:
                    print("❌ Comando não reconhecido!")
                    
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro na interface: {e}")
        finally:
            self.stop_all()

    def send_command(self, device_id, command):
        """Envia comando para um dispositivo específico"""
        simulator = next((s for s in self.simulators if s.device_id == device_id), None)
        
        if simulator and simulator.client.is_connected():
            simulator.client.publish(f"smartpatio/commands/{device_id}", command)
            logger.info(f"📤 Comando '{command}' enviado para {device_id}")
        else:
            print(f"❌ Dispositivo {device_id} não encontrado ou desconectado!")

if __name__ == "__main__":
    print("🚦 SmartPatio Multi-Device Simulator")
    print("Mottu IoT Challenge - FIAP 2025\n")
    
    # Criar e executar simulador
    simulator = MultiDeviceSimulator(NUM_DEVICES)
    simulator.run()
