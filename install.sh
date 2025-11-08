#!/bin/bash
echo "🚦 SmartPatio IoT - Mottu Challenge"
echo "Instalando dependências Python..."
echo

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado! Instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python3 encontrado!"
echo "📦 Instalando dependências..."

# Tentar instalar via requirements.txt primeiro
if [ -f "requirements.txt" ]; then
    echo "📄 Usando requirements.txt..."
    pip3 install -r requirements.txt
else
    echo "📄 Instalando dependências manualmente..."
    pip3 install paho-mqtt matplotlib pandas numpy oracledb
fi

if [ $? -ne 0 ]; then
    echo "❌ Erro na instalação das dependências"
    exit 1
fi

echo
echo "✅ Instalação concluída!"
echo
echo "�️ Configuração Oracle Database:"
echo "   - Servidor: oracle.fiap.com.br:1521/orcl"
echo "   - Usuário: RM554456"
echo "   - O data_logger.py conecta automaticamente ao Oracle"
echo
echo "�📋 Para testar o sistema:"
echo "   1. Abra o Wokwi ou ESP32 real com o código main.cpp"
echo "   2. Execute: python3 demo.py (modo interativo)"
echo "   3. Ou execute: python3 demo.py auto (demonstração automática)"
echo "   4. Execute: python3 data_logger.py (persistência Oracle + CSV)"
echo "   5. Abra dashboard/index.html no navegador"
echo
