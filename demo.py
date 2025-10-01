#!/usr/bin/env python3
"""
Sistema de Demonstração SmartPatio IoT - Mottu Challenge
Script simples para testar e demonstrar o sistema IoT com 1 dispositivo e 2 atuadores
"""

import paho.mqtt.client as mqtt
import json
import time
import sys
from datetime import datetime

# Configurações
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
DEVICE_ID = "TESTE"

class SmartPatioDemo:
    def __init__(self):
        self.client = mqtt.Client(client_id="SmartPatio-Demo")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.connected = False
        self.messages_received = 0
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Conectado ao broker MQTT")
            self.connected = True
            
            # Subscrever aos tópicos do dispositivo
            topics = [
                f"smartpatio/status/{DEVICE_ID}",
                f"smartpatio/telemetry/{DEVICE_ID}"
            ]
            
            for topic in topics:
                client.subscribe(topic)
                print(f"📡 Subscrito a: {topic}")
        else:
            print(f"❌ Falha na conexão MQTT: {rc}")
    
    def on_message(self, client, userdata, msg):
        self.messages_received += 1
        topic = msg.topic
        message = msg.payload.decode('utf-8')
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n📨 [{timestamp}] Mensagem recebida:")
        print(f"   📂 Tópico: {topic}")
        
        if "/status/" in topic:
            print(f"   📊 Status: {message}")
        elif "/telemetry/" in topic:
            try:
                data = json.loads(message)
                print(f"   📊 Telemetria:")
                print(f"      🔧 Dispositivo Ativo: {'✅ Sim' if data.get('device_active') else '❌ Não'}")
                print(f"      💡 LED Piscando: {'✅ Sim' if data.get('led_blinking') else '❌ Não'}")
                print(f"      🔊 Buzzer Ativo: {'✅ Sim' if data.get('buzzer_active') else '❌ Não'}")
                print(f"      📡 WiFi RSSI: {data.get('wifi_rssi', 'N/A')} dBm")
            except json.JSONDecodeError:
                print(f"   📊 Dados: {message}")
    
    def send_command(self, command):
        if self.connected:
            topic = f"smartpatio/commands/{DEVICE_ID}"
            self.client.publish(topic, command)
            print(f"📤 Comando '{command}' enviado para {DEVICE_ID}")
        else:
            print("❌ Não conectado ao broker MQTT")
    
    def print_menu(self):
        print("\n" + "="*50)
        print("🚦 SMARTPATIO - DEMO INTERATIVO")
        print("="*50)
        print("Comandos disponíveis:")
        print("  1 - Ativar dispositivo (LED + Buzzer)")
        print("  2 - Desativar dispositivo")
        print("  3 - Reiniciar dispositivo")
        print("  s - Mostrar estatísticas")
        print("  q - Sair")
        print("="*50)
    
    def print_stats(self):
        print("\n📊 ESTATÍSTICAS:")
        print(f"   📨 Mensagens recebidas: {self.messages_received}")
        print(f"   🔗 Status conexão: {'✅ Conectado' if self.connected else '❌ Desconectado'}")
        print(f"   📱 Dispositivo monitorado: {DEVICE_ID}")
    
    def run(self):
        print("🚦 SmartPatio Demo - Mottu IoT Challenge")
        print("Pressione Ctrl+C para sair\n")
        
        try:
            print("🔄 Conectando ao broker MQTT...")
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            
            # Aguardar conexão
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(1)
                timeout -= 1
            
            if not self.connected:
                print("❌ Timeout na conexão MQTT")
                return
            
            # Menu interativo
            while True:
                self.print_menu()
                choice = input("\n📟 SmartPatio> ").strip().lower()
                
                if choice == 'q':
                    break
                elif choice == '1':
                    self.send_command("ACTIVATE")
                elif choice == '2':
                    self.send_command("DEACTIVATE")
                elif choice == '3':
                    self.send_command("RESET")
                elif choice == 's':
                    self.print_stats()
                elif choice == '':
                    continue
                else:
                    print("❌ Opção inválida!")
                
                # Pausa para ver resultado
                if choice in ['1', '2', '3']:
                    print("⏳ Aguardando resposta do dispositivo...")
                    time.sleep(2)
        
        except KeyboardInterrupt:
            print("\n🛑 Demo interrompido pelo usuário")
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            print("👋 Demo finalizado!")

def run_auto_demo():
    """Executa uma demonstração automática"""
    print("🚦 SmartPatio - Demonstração Automática")
    print("="*50)
    
    demo = SmartPatioDemo()
    
    try:
        demo.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        demo.client.loop_start()
        
        # Aguardar conexão
        timeout = 10
        while not demo.connected and timeout > 0:
            time.sleep(1)
            timeout -= 1
        
        if not demo.connected:
            print("❌ Timeout na conexão MQTT")
            return
        
        print("✅ Iniciando demonstração automática...")
        
        # Sequência de demonstração
        commands = [
            ("ACTIVATE", "Ativando dispositivo (LED piscando + Buzzer tocando)"),
            ("DEACTIVATE", "Desativando dispositivo"),
            ("ACTIVATE", "Ativando novamente"),
            ("DEACTIVATE", "Desativando para finalizar")
        ]
        
        for command, description in commands:
            print(f"\n🔄 {description}")
            demo.send_command(command)
            print("⏳ Aguardando 8 segundos para observar o comportamento...")
            time.sleep(8)
        
        print("\n✅ Demonstração concluída!")
        demo.print_stats()
        
    except KeyboardInterrupt:
        print("\n🛑 Demonstração interrompida")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        demo.client.loop_stop()
        demo.client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        run_auto_demo()
    else:
        demo = SmartPatioDemo()
        demo.run()
