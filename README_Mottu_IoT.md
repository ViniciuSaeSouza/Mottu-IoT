
# 📦 Mottu-IoT

Este repositório contém o firmware e a documentação técnica do projeto **Sistema de Monitoramento de Zonas - Mottu Challenge**, desenvolvido pela equipe **Prisma** (FIAP - Maio/2025).

## 📌 Visão Geral

O projeto visa otimizar a localização de motocicletas nos pátios da empresa Mottu, utilizando dispositivos IoT baseados em ESP32, comunicação via protocolo MQTT e uma interface de controle desenvolvida no MIT App Inventor.

## 🧰 Tecnologias Utilizadas

- **ESP32**: Microcontrolador com suporte a Wi-Fi.
- **MQTT (HiveMQ Cloud)**: Protocolo leve de comunicação para IoT.
- **MIT App Inventor**: Plataforma para desenvolvimento do aplicativo de controle.
- **Tinkercad / Wokwi**: Simuladores para testes de circuitos e firmware.
- **Fusion 360**: Modelagem 3D do case protetor.

## 🛠️ Funcionalidades

- Ativação remota de sinalização sonora e visual em motocicletas específicas.
- Comunicação eficiente entre o aplicativo e os dispositivos via MQTT.
- Modo de economia de energia com uso do deep sleep no ESP32.
- Interface amigável para operadores selecionarem e ativarem motos.

## 📁 Estrutura do Repositório

```
Mottu-IoT/
├── firmware/             # Código-fonte para o ESP32
├── app_inventor/         # Arquivos do aplicativo desenvolvido no MIT App Inventor
├── simulacoes/           # Arquivos de simulação no Tinkercad e Wokwi
├── modelagem_3d/         # Arquivos do case 3D no Fusion 360
├── imagens/              # Imagens e diagramas do projeto
└── README.md             # Este documento
```

## 🚀 Como Utilizar

1. **Configurar o ESP32**:
   - Carregue o firmware localizado na pasta `firmware/` utilizando o Arduino IDE ou outra plataforma compatível.
   - Certifique-se de configurar as credenciais Wi-Fi e os tópicos MQTT conforme necessário.

2. **Configurar o Aplicativo**:
   - Importe o projeto do MIT App Inventor localizado em `app_inventor/` para a plataforma [MIT App Inventor](https://appinventor.mit.edu/).
   - Ajuste as configurações de broker MQTT e tópicos conforme sua necessidade.

3. **Simulações**:
   - Utilize os arquivos em `simulacoes/` para testar o funcionamento do sistema nos simuladores Tinkercad ou Wokwi.

## 📊 Resultados Esperados

- Redução significativa no tempo de localização de motocicletas nos pátios.
- Diminuição de custos operacionais relacionados à logística interna.
- Melhoria na eficiência dos processos de entrega e retirada de veículos.

## 👥 Equipe

- **Laura de Oliveira Cintra** - RM 558843
- **Maria Eduarda Alves da Paixão** - RM 558832
- **Vinicius Saes de Souza** - RM 554456

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
