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

pip install paho-mqtt matplotlib pandas numpy

if errorlevel 1 (
    echo ❌ Erro na instalacao das dependencias
    pause
    exit /b 1
)

echo.
echo ✅ Instalacao concluida!
echo.
echo 📋 Para testar o sistema:
echo    1. Abra o Wokwi ou ESP32 real com o codigo main.cpp
echo    2. Execute: python demo.py (modo interativo)
echo    3. Ou execute: python demo.py auto (demonstracao automatica)
echo    4. Abra dashboard/index.html no navegador
echo.
pause
