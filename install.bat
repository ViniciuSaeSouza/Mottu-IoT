@echo off
echo 🚦 SmartPatio IoT - Mottu Challenge
echo Instalando dependencias Python...
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado! Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo ✅ Python encontrado!
echo 📦 Instalando dependencias...

REM Tentar instalar via requirements.txt primeiro
if exist "requirements.txt" (
    echo 📄 Usando requirements.txt...
    pip install -r requirements.txt
) else (
    echo 📄 Instalando dependencias manualmente...
    pip install paho-mqtt matplotlib pandas numpy oracledb
)

if errorlevel 1 (
    echo ❌ Erro na instalacao das dependencias
    pause
    exit /b 1
)

echo.
echo ✅ Instalacao concluida!
echo.
echo �️ Configuracao Oracle Database:
echo    - Servidor: oracle.fiap.com.br:1521/orcl
echo    - Usuario: RM554456
echo    - O data_logger.py conecta automaticamente ao Oracle
echo.
echo �📋 Para testar o sistema:
echo    1. Abra o Wokwi ou ESP32 real com o codigo main.cpp
echo    2. Execute: python demo.py (modo interativo)
echo    3. Ou execute: python demo.py auto (demonstracao automatica)
echo    4. Execute: python data_logger.py (persistencia Oracle + CSV)
echo    5. Abra dashboard/index.html no navegador
echo.
pause
