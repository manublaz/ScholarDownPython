def verificar_proxies():
    """Verifica si hay proxies disponibles y ofrece validarlos"""
    if os.path.exists("proxies.txt"):
        try:
            with open("proxies.txt", "r") as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            if len(lines) == 0:
                print("[WARNING] proxies.txt existe pero está vacío o solo tiene comentarios")
                return False
            
            # Analizar tipos de proxies
            proxies_completos = [line for line in lines if ':' in line]
            ips_sin_puerto = [line for line in lines if ':' not in line and ('.' in line)]
            
            print(f"[INFO] Análisis de proxies detectados:")
            print(f"  • Proxies completos (IP:PUERTO): {len(proxies_completos)}")
            print(f"  • IPs sin puerto: {len(ips_sin_puerto)}")
            print(f"  • Total: {len(lines)} entradas")
            
            if ips_sin_puerto:
                print(f"[INFO] Se detectaron {len(ips_sin_puerto)} IPs sin puerto especificado")
                print(f"[INFO] El sistema auto-detectará los puertos automáticamente")
            
            # Preguntar si validar proxies ahora
            respuesta = input("¿Desea validar/auto-detectar proxies antes de comenzar? (recomendado) (s/n): ").lower().strip()
            if respuesta in ['s', 'si', 'yes', 'y']:
                if os.path.exists("proxy_validator.py"):
                    print("[INFO] Ejecutando validador avanzado de proxies...")
                    try:
                        resultado = subprocess.run("python proxy_validator.py", shell=True)
                        if resultado.returncode == 0:
                            print("[INFO] Validación/auto-detección de proxies completada")
                        else:
                            print("[WARNING] Hubo problemas en la validación, pero continuaremos")
                    except:
                        print("[WARNING] Error al ejecutar validador, pero continuaremos")
                else:
                    print("[WARNING] proxy_validator.py no encontrado. Los proxies se procesarán automáticamente durante la ejecución")
            
            return len(lines) > 0
        except:
            print("[WARNING] Error al leer proxies.txt")
            return False
    else:
        print("[WARNING] No se encontró proxies.txt")
        print("[INFO] Creando archivo de ejemplo...")
        
        # Crear archivo de ejemplo
        try:
            with open("proxies.txt", "w", encoding="utf-8") as f:
                f.write("# Archivo de configuración de proxies para ScholarDown Advanced\n")
                f.write("# Formatos soportados:\n")
                f.write("#   IP:PUERTO  (ej: 192.168.1.100:8080) - Listo para usar\n")
                f.write("#   IP         (ej: 192.168.1.100) - Auto-detectará puerto\n")
                f.write("# \n")
                f.write("# CARACTERÍSTICAS:\n")
                f.write("# • Auto-detección de puertos (15 puertos más comunes)\n")
                f.write("# • Validación automática de conectividad\n")
                f.write("# • Backup automático antes de modificaciones\n")
                f.write("# • Procesamiento paralelo para mayor velocidad\n")
                f.write("#\n")
                f.write("# Elimina estos comentarios y agrega tus proxies/IPs reales:\n")
                f.write("# 192.168.1.100:8080     # Proxy completo\n")
                f.write("# 10.0.0.50:3128         # Proxy completo\n")
                f.write("# 203.142.69.67          # Solo IP, se auto-detecta puerto\n")
                f.write("# 89.163.221.14          # Solo IP, se auto-detecta puerto\n")
                f.write("\n")
                f.write("# Para validar: python proxy_validator.py\n")
            print("[INFO] Archivo proxies.txt de ejemplo creado con soporte avanzado")
        except:
            pass
            
        return False#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ScholarDown Advanced - Sistema Completo de Extracción de Papers
Orquesta la ejecución de todos los scripts con funcionalidades avanzadas
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def verificar_archivos_necesarios():
    """Verifica que existan los archivos necesarios"""
    archivos_requeridos = [
        "scholardown_part1.py",
        "scholardown_part2.py", 
        "scholardown_part3.py"
    ]
    
    archivos_faltantes = []
    for archivo in archivos_requeridos:
        if not os.path.exists(archivo):
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print(f"[ERROR] Archivos faltantes: {', '.join(archivos_faltantes)}")
        return False
    
    return True

def verificar_progreso():
    """Verifica si hay progreso previo y pregunta al usuario"""
    if os.path.exists("progress.json"):
        try:
            with open("progress.json", "r", encoding="utf-8") as f:
                progress = json.load(f)
            
            print(f"[INFO] Se detectó progreso previo:")
            print(f"  - Procesadas: {progress['processed']} URLs")
            print(f"  - Total: {progress['total']} URLs") 
            print(f"  - Resultados: {progress['results_count']} enlaces")
            print(f"  - Fecha: {progress['timestamp']}")
            
            respuesta = input("\n¿Desea continuar desde donde se quedó? (s/n): ").lower().strip()
            if respuesta in ['s', 'si', 'yes', 'y']:
                return True
            else:
                # Limpiar archivos de progreso
                try:
                    os.remove("progress.json")
                    if os.path.exists("papers2.txt"):
                        os.remove("papers2.txt")
                    print("[INFO] Progreso anterior eliminado. Comenzando desde cero.")
                except:
                    pass
                return False
        except:
            print("[WARNING] Archivo de progreso corrupto. Comenzando desde cero.")
            return False
    
    return False

def ejecutar_programa(comando, descripcion=""):
    """Ejecuta un programa y maneja errores"""
    try:
        print(f"\n{'='*60}")
        print(f"[INFO] {descripcion}")
        print(f"[INFO] Ejecutando: {comando}")
        print(f"{'='*60}")
        
        # Ejecuta el programa y espera a que termine
        resultado = subprocess.run(comando, shell=True)
        
        if resultado.returncode != 0:
            print(f"\n[ERROR] El comando '{comando}' falló con código {resultado.returncode}.")
            respuesta = input("¿Desea continuar con el siguiente paso? (s/n): ").lower().strip()
            if respuesta not in ['s', 'si', 'yes', 'y']:
                sys.exit(resultado.returncode)
        else:
            print(f"\n[OK] {descripcion} completado exitosamente.")
            
    except KeyboardInterrupt:
        print(f"\n[INFO] Ejecución interrumpida por el usuario.")
        print("[INFO] El progreso se ha guardado automáticamente.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error al ejecutar '{comando}': {e}")
        respuesta = input("¿Desea continuar con el siguiente paso? (s/n): ").lower().strip()
        if respuesta not in ['s', 'si', 'yes', 'y']:
            sys.exit(1)

def mostrar_estadisticas():
    """Muestra estadísticas finales del proceso"""
    archivos_resultados = ["papers.txt", "papers2.txt"]
    
    print(f"\n{'='*60}")
    print("📊 ESTADÍSTICAS FINALES")
    print(f"{'='*60}")
    
    for archivo in archivos_resultados:
        if os.path.exists(archivo):
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    lineas = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                print(f"📄 {archivo}: {len(lineas)} enlaces")
            except:
                print(f"❌ {archivo}: Error al leer")
        else:
            print(f"❌ {archivo}: No encontrado")
    
    # Verificar carpeta de PDFs
    if os.path.exists("pdf"):
        try:
            pdfs = [f for f in os.listdir("pdf") if f.endswith(".pdf")]
            print(f"📁 Carpeta PDF: {len(pdfs)} archivos descargados")
        except:
            print("📁 Carpeta PDF: Error al acceder")
    
    print(f"{'='*60}")

def verificar_tor():
    """Verifica si TOR está disponible"""
    tor_exe = r"C:\Tor Browser\Browser\TorBrowser\Tor\tor.exe"
    if not os.path.exists(tor_exe):
        print(f"[WARNING] No se encontró TOR en: {tor_exe}")
        print("[WARNING] El script funcionará solo con proxies (si están disponibles)")
        return False
    return True

def verificar_proxies():
    """Verifica si hay proxies disponibles y ofrece validarlos"""
    if os.path.exists("proxies.txt"):
        try:
            with open("proxies.txt", "r") as f:
                proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            if len(proxies) == 0:
                print("[WARNING] proxies.txt existe pero está vacío o solo tiene comentarios")
                return False
                
            print(f"[INFO] {len(proxies)} proxies detectados en proxies.txt")
            
            # Preguntar si validar proxies ahora
            respuesta = input("¿Desea validar los proxies antes de comenzar? (recomendado) (s/n): ").lower().strip()
            if respuesta in ['s', 'si', 'yes', 'y']:
                if os.path.exists("proxy_validator.py"):
                    print("[INFO] Ejecutando validador de proxies...")
                    try:
                        resultado = subprocess.run("python proxy_validator.py", shell=True)
                        if resultado.returncode == 0:
                            print("[INFO] Validación de proxies completada")
                        else:
                            print("[WARNING] Hubo problemas en la validación, pero continuaremos")
                    except:
                        print("[WARNING] Error al ejecutar validador, pero continuaremos")
                else:
                    print("[WARNING] proxy_validator.py no encontrado. Los proxies se validarán automáticamente durante la ejecución")
            
            return len(proxies) > 0
        except:
            print("[WARNING] Error al leer proxies.txt")
            return False
    else:
        print("[WARNING] No se encontró proxies.txt")
        print("[INFO] Creando archivo de ejemplo...")
        
        # Crear archivo de ejemplo
        try:
            with open("proxies.txt", "w", encoding="utf-8") as f:
                f.write("# Archivo de configuración de proxies para ScholarDown Advanced\n")
                f.write("# Un proxy por línea en formato IP:PUERTO\n")
                f.write("# \n")
                f.write("# IMPORTANTE: Los proxies se validan automáticamente antes de usar\n")
                f.write("# El sistema detecta automáticamente:\n")
                f.write("#   ✓ Proxies funcionales\n")
                f.write("#   ✗ Proxies que requieren autenticación\n")
                f.write("#   ✗ Proxies que no responden\n")
                f.write("#   ✗ Proxies bloqueados\n")
                f.write("#\n")
                f.write("# Elimina estos comentarios y agrega tus proxies reales:\n")
                f.write("# 192.168.1.100:8080\n")
                f.write("# 10.0.0.50:3128\n")
                f.write("# 203.142.69.67:8080\n")
                f.write("\n")
                f.write("# Para validar tus proxies: python proxy_validator.py\n")
            print("[INFO] Archivo proxies.txt de ejemplo creado")
        except:
            pass
            
        return False

def verificar_dependencias():
    """Verifica que estén instaladas las dependencias necesarias"""
    dependencias = ['requests', 'beautifulsoup4', 'stem']
    faltantes = []
    
    for dep in dependencias:
        try:
            __import__(dep if dep != 'beautifulsoup4' else 'bs4')
        except ImportError:
            faltantes.append(dep)
    
    if faltantes:
        print(f"[ERROR] Dependencias faltantes: {', '.join(faltantes)}")
        print(f"[INFO] Instalar con: pip install {' '.join(faltantes)}")
        return False
    
    return True

def mostrar_banner():
    """Muestra el banner del programa"""
    print("="*70)
    print("🎓 SCHOLARDOWN ADVANCED - Sistema Completo de Extracción")
    print("="*70)
    print("✨ Características avanzadas:")
    print("  • Simulación de comportamiento humano")
    print("  • Rotación inteligente de fingerprints")
    print("  • Headers coherentes y realistas")
    print("  • Gestión avanzada de cookies y sesiones")
    print("  • Auto-detección de puertos para proxies")
    print("  • Validación automática de proxies")
    print("  • Escritura incremental con recuperación")
    print("  • Detección proactiva de bloqueos")
    print("="*70)

def main():
    mostrar_banner()
    
    # Verificaciones previas
    print("\n[INFO] Realizando verificaciones previas...")
    
    # Verificar dependencias
    if not verificar_dependencias():
        print("[ERROR] Instala las dependencias necesarias antes de continuar.")
        sys.exit(1)
    
    # Verificar archivos necesarios
    if not verificar_archivos_necesarios():
        print("[ERROR] Archivos necesarios faltantes. Abortando.")
        sys.exit(1)
    
    # Verificar TOR y proxies
    tor_ok = verificar_tor()
    proxies_ok = verificar_proxies()
    
    if not tor_ok and not proxies_ok:
        print("[ERROR] Ni TOR ni proxies están disponibles. No se puede continuar.")
        print("[INFO] Necesitas al menos uno de estos:")
        print("  1. TOR Browser instalado en C:\\Tor Browser\\")
        print("  2. Archivo proxies.txt con proxies válidos")
        sys.exit(1)
    
    # Verificar si continuar progreso anterior
    continuar_progreso = verificar_progreso()
    
    # Definir programas a ejecutar
    programas = []
    
    if not continuar_progreso:
        # Ejecutar desde el inicio
        programas = [
            ("python scholardown_part1.py", "PASO 1: Extracción de enlaces del perfil de Google Scholar"),
            ("python scholardown_part2.py", "PASO 2: Búsqueda avanzada de enlaces de descarga con anti-detección"),
            ("python scholardown_part3.py", "PASO 3: Descarga masiva de archivos PDF")
        ]
    else:
        # Solo ejecutar desde el paso 2 (el script detectará automáticamente el progreso)
        programas = [
            ("python scholardown_part.py", "PASO 2: Continuando búsqueda avanzada de enlaces de descarga"),
            ("python scholardown_part3.py", "PASO 3: Descarga masiva de archivos PDF")
        ]
    
    print(f"\n[INFO] Iniciando ejecución de {len(programas)} pasos...")
    print(f"[INFO] Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tiempo_inicio = datetime.now()
    
    # Ejecutar programas secuencialmente
    for i, (cmd, descripcion) in enumerate(programas, 1):
        print(f"\n🚀 EJECUTANDO PASO {i}/{len(programas)}")
        ejecutar_programa(cmd, descripcion)
    
    tiempo_total = datetime.now() - tiempo_inicio
    
    # Mostrar estadísticas finales
    mostrar_estadisticas()
    
    print(f"\n🎉 ¡Todos los procesos completados exitosamente!")
    print(f"⏰ Tiempo total de ejecución: {tiempo_total}")
    print(f"🏁 Proceso finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Limpiar archivos temporales opcionales
    archivos_temp = ["torrc_temp.txt"]
    limpiados = 0
    for archivo in archivos_temp:
        try:
            if os.path.exists(archivo):
                os.remove(archivo)
                limpiados += 1
        except:
            pass
    
    if limpiados > 0:
        print(f"🧹 {limpiados} archivos temporales eliminados.")
    
    # Mantener progress.json para posibles reanudaciones futuras
    if os.path.exists("progress.json"):
        print("💾 Archivo progress.json mantenido para futuras reanudaciones.")
    
    # Mostrar archivos generados
    print(f"\n📁 Archivos generados:")
    archivos_salida = [
        ("papers.txt", "Enlaces de papers extraídos"),
        ("papers2.txt", "Enlaces de descarga encontrados"),
        ("pdf/", "Carpeta con PDFs descargados"),
        ("proxy_validation_results.json", "Resultados de validación de proxies"),
        ("proxies_original_backup_*.txt", "Backup de proxies originales")
    ]
    
    for archivo, descripcion in archivos_salida:
        if "*" in archivo:
            # Buscar archivos con patrón
            import glob
            matches = glob.glob(archivo)
            if matches:
                print(f"  ✅ {matches[-1]}: {descripcion}")
            else:
                print(f"  ❌ {archivo}: No generado")
        elif os.path.exists(archivo):
            print(f"  ✅ {archivo}: {descripcion}")
        else:
            print(f"  ❌ {archivo}: No generado")
    
    print(f"\n💡 Consejos para el futuro:")
    print(f"  • Ejecuta 'python proxy_validator.py' para validar nuevos proxies")
    print(f"  • El sistema auto-detecta puertos faltantes automáticamente")
    print(f"  • Los archivos de progreso permiten reanudar procesos interrumpidos")
    print(f"  • Revisa los logs para optimizar configuraciones")
    print(f"  • Los backups de proxies se crean automáticamente")
    
    print("\n" + "="*70)
    print("🙏 Gracias por usar ScholarDown Advanced!")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n[INFO] Programa interrumpido por el usuario.")
        print("[INFO] El progreso se ha guardado automáticamente.")
        print("🔄 Puedes reanudar ejecutando el script nuevamente.")
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] Error inesperado: {e}")
        print("💡 Si el problema persiste, verifica:")
        print("  • Permisos de archivos y carpetas")
        print("  • Conexión a internet")
        print("  • Configuración de TOR/proxies")
        sys.exit(1)