"""
Script de Instalacion Automatica
Instala las dependencias y configura el proyecto automaticamente
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Ejecuta un comando y muestra progreso"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Compleatado: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR ejecutando: {description}")
        print(f"   Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("INSTALACION AUTOMATICA - CUBA JOBS BOT")
    print("="*60 + "\n")
    
    # Paso 1: Instalar dependencias
    print("\nPASO 1/3: Instalando dependencias...")
    print("-"*60)
    
    success = True
    
    # Instalar requisitos
    success &= run_command(
        "pip install -r requirements.txt",
        "Instalando dependencias Python"
    )
    
    # Paso 2: Crear directorio de cache
    print("\nPASO 2/3: Creando directorio de cache...")
    print("-"*60)
    
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)
    print("Directorio de cache creado")
    
    # Paso 3: Verificar archivos de configuracion
    print("\nPASO 3/3: Verificando archivos de configuracion...")
    print("-"*60)
    
    # Verificar archivo de proxies
    proxy_file = Path("scrapers/proxy_list.txt")
    if proxy_file.exists():
        print("Archivo de proxies encontrado")
        proxy_count = len([line.strip() for line in proxy_file.read_text().splitlines() 
                          if line.strip() and not line.strip().startswith('#')])
        print(f"   Contiene {proxy_count} proxies")
    else:
        print("Archivo de proxies no encontrado")
        print("   Creando archivo de proxies de ejemplo...")
        
        proxy_file.parent.mkdir(exist_ok=True)
        proxy_file.write_text("# Lista de proxies gratuitos\n# Formato: http://host:puerto\n# Agrega tus proxies aqui\n")
        print("Archivo de proxies de ejemplo creado")
    
    # Verificar archivo .env
    env_file = Path(".env")
    if env_file.exists():
        print("Archivo .env encontrado")
    else:
        print("Archivo .env no encontrado")
        print("   Copiando .env.example a .env...")
        
        env_example = Path(".env.example")
        if env_example.exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("Archivo .env creado")
        else:
            print("ERROR: Archivo .env.example no encontrado")
            success = False
    
    # Resumen
    print("\n" + "="*60)
    if success:
        print("INSTALACION COMPLETADA")
        print("="*60)
        print("\nSIGUIENTES PASOS:")
        print("1. Edita el archivo .env y configura tu TELEGRAM_BOT_TOKEN")
        print("2. Edita scrapers/proxy_list.txt y agrega mas proxies si quieres")
        print("3. Ejecuta: python run.py")
        print("4. En Telegram, escribe: Ofertas")
    else:
        print("INSTALACION INCOMPLETA")
        print("   Por favor, revisa los errores arriba")
    print("="*60 + "\n")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
