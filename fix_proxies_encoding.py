#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Solucionador de problemas de codificación en proxies.txt
Detecta y corrige automáticamente problemas de encoding
"""

import os
import chardet

def detect_encoding(filename):
    """Detecta la codificación de un archivo"""
    try:
        with open(filename, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'], result['confidence']
    except Exception as e:
        print(f"Error detectando codificación: {e}")
        return None, 0

def fix_proxies_file(filename="proxies.txt"):
    """Corrige problemas de codificación en el archivo de proxies"""
    print(f"🔍 Diagnosticando archivo: {filename}")
    
    if not os.path.exists(filename):
        print(f"❌ Archivo {filename} no existe")
        create_clean_file(filename)
        return
    
    # Detectar codificación actual
    detected_encoding, confidence = detect_encoding(filename)
    print(f"📊 Codificación detectada: {detected_encoding} (confianza: {confidence:.2f})")
    
    # Intentar leer con diferentes codificaciones
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', detected_encoding]
    
    content_lines = []
    successful_encoding = None
    
    for encoding in encodings_to_try:
        if encoding is None:
            continue
            
        try:
            print(f"🔄 Intentando leer con codificación: {encoding}")
            with open(filename, 'r', encoding=encoding) as f:
                content_lines = f.readlines()
            
            print(f"✅ Éxito con codificación: {encoding}")
            print(f"📄 Líneas leídas: {len(content_lines)}")
            successful_encoding = encoding
            break
            
        except UnicodeDecodeError as e:
            print(f"❌ Error con {encoding}: {e}")
            continue
        except Exception as e:
            print(f"❌ Error inesperado con {encoding}: {e}")
            continue
    
    if not content_lines:
        print("❌ No se pudo leer el archivo con ninguna codificación")
        print("🔧 Creando archivo nuevo...")
        create_clean_file(filename)
        return
    
    # Analizar contenido
    ips_sin_puerto = []
    proxies_completos = []
    comment_lines = []
    
    for line_num, line in enumerate(content_lines, 1):
        line = line.strip()
        if not line:
            continue
        elif line.startswith('#'):
            comment_lines.append(line)
        else:
            if ':' in line and not line.startswith('#'):
                # Verificar si es proxy completo IP:PUERTO
                try:
                    ip, port = line.split(':')
                    port = int(port)
                    if 1 <= port <= 65535:
                        proxies_completos.append(line)
                    else:
                        print(f"⚠️  Línea {line_num}: Puerto inválido - {line}")
                except:
                    print(f"⚠️  Línea {line_num}: Formato inválido - {line}")
            else:
                # Solo IP, puede ser auto-detectada
                if line.replace('.', '').replace(' ', '').isdigit() or '.' in line:
                    ips_sin_puerto.append(line)
                else:
                    print(f"⚠️  Línea {line_num}: No parece una IP válida - {line}")
    
    print(f"\n📊 Análisis del archivo:")
    print(f"  • Líneas de comentario: {len(comment_lines)}")
    print(f"  • Proxies completos (IP:PUERTO): {len(proxies_completos)}")
    print(f"  • IPs sin puerto: {len(ips_sin_puerto)}")
    print(f"  • Codificación original: {successful_encoding}")
    
    if len(proxies_completos) == 0 and len(ips_sin_puerto) == 0:
        print("⚠️  No se encontraron proxies o IPs válidas en el archivo")
        
        respuesta = input("¿Crear archivo limpio de ejemplo? (s/n): ").lower().strip()
        if respuesta in ['s', 'si', 'yes', 'y']:
            create_clean_file(filename)
        return
    
    # Crear archivo corregido
    backup_name = f"{filename}.backup"
    try:
        # Hacer backup del original
        os.rename(filename, backup_name)
        print(f"💾 Backup creado: {backup_name}")
        
        # Crear archivo corregido con UTF-8
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Archivo de proxies corregido - Codificación UTF-8\n")
            f.write("# Formatos soportados:\n")
            f.write("#   IP:PUERTO  (ej: 192.168.1.100:8080) - Listo para usar\n")
            f.write("#   IP         (ej: 192.168.1.100) - Auto-detectará puerto\n")
            f.write(f"# Archivo original respaldado como: {backup_name}\n")
            f.write(f"# Total encontrado: {len(proxies_completos)} proxies completos, {len(ips_sin_puerto)} IPs\n")
            f.write("\n")
            
            # Escribir proxies completos primero
            if proxies_completos:
                f.write("# Proxies completos (IP:PUERTO)\n")
                for proxy in proxies_completos:
                    f.write(f"{proxy}\n")
                f.write("\n")
            
            # Escribir IPs sin puerto
            if ips_sin_puerto:
                f.write("# IPs sin puerto (se auto-detectará)\n")
                for ip in ips_sin_puerto:
                    f.write(f"{ip}\n")
        
        print(f"✅ Archivo corregido exitosamente!")
        print(f"📝 {len(proxies_completos)} proxies completos y {len(ips_sin_puerto)} IPs guardadas con codificación UTF-8")
        
        if ips_sin_puerto:
            print(f"\n💡 Para auto-detectar puertos de las IPs, ejecuta:")
            print(f"   python proxy_validator.py")
        
    except Exception as e:
        print(f"❌ Error al corregir archivo: {e}")
    """Corrige problemas de codificación en el archivo de proxies"""
    print(f"🔍 Diagnosticando archivo: {filename}")
    
    if not os.path.exists(filename):
        print(f"❌ Archivo {filename} no existe")
        create_clean_file(filename)
        return
    
    # Detectar codificación actual
    detected_encoding, confidence = detect_encoding(filename)
    print(f"📊 Codificación detectada: {detected_encoding} (confianza: {confidence:.2f})")
    
    # Intentar leer con diferentes codificaciones
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', detected_encoding]
    
    content_lines = []
    successful_encoding = None
    
    for encoding in encodings_to_try:
        if encoding is None:
            continue
            
        try:
            print(f"🔄 Intentando leer con codificación: {encoding}")
            with open(filename, 'r', encoding=encoding) as f:
                content_lines = f.readlines()
            
            print(f"✅ Éxito con codificación: {encoding}")
            print(f"📄 Líneas leídas: {len(content_lines)}")
            successful_encoding = encoding
            break
            
        except UnicodeDecodeError as e:
            print(f"❌ Error con {encoding}: {e}")
            continue
        except Exception as e:
            print(f"❌ Error inesperado con {encoding}: {e}")
            continue
    
    if not content_lines:
        print("❌ No se pudo leer el archivo con ninguna codificación")
        print("🔧 Creando archivo nuevo...")
        create_clean_file(filename)
        return
    
    # Analizar contenido
    proxy_lines = []
    comment_lines = []
    
    for line_num, line in enumerate(content_lines, 1):
        line = line.strip()
        if not line:
            continue
        elif line.startswith('#'):
            comment_lines.append(line)
        else:
            # Verificar si parece un proxy válido
            if ':' in line and not line.startswith('#'):
                try:
                    ip, port = line.split(':')
                    port = int(port)
                    if 1 <= port <= 65535:
                        proxy_lines.append(line)
                    else:
                        print(f"⚠️  Línea {line_num}: Puerto inválido - {line}")
                except:
                    print(f"⚠️  Línea {line_num}: Formato inválido - {line}")
            else:
                print(f"⚠️  Línea {line_num}: No parece un proxy - {line}")
    
    print(f"\n📊 Análisis del archivo:")
    print(f"  • Líneas de comentario: {len(comment_lines)}")
    print(f"  • Proxies válidos: {len(proxy_lines)}")
    print(f"  • Codificación original: {successful_encoding}")
    
    if len(proxy_lines) == 0:
        print("⚠️  No se encontraron proxies válidos en el archivo")
        
        respuesta = input("¿Crear archivo limpio de ejemplo? (s/n): ").lower().strip()
        if respuesta in ['s', 'si', 'yes', 'y']:
            create_clean_file(filename)
        return
    
    # Crear archivo corregido
    backup_name = f"{filename}.backup"
    try:
        # Hacer backup del original
        os.rename(filename, backup_name)
        print(f"💾 Backup creado: {backup_name}")
        
        # Crear archivo corregido con UTF-8
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Archivo de proxies corregido - Codificación UTF-8\n")
            f.write("# Un proxy por línea en formato IP:PUERTO\n")
            f.write(f"# Archivo original respaldado como: {backup_name}\n")
            f.write(f"# Proxies válidos encontrados: {len(proxy_lines)}\n")
            f.write("\n")
            
            for proxy in proxy_lines:
                f.write(f"{proxy}\n")
        
        print(f"✅ Archivo corregido exitosamente!")
        print(f"📝 {len(proxy_lines)} proxies guardados con codificación UTF-8")
        
    except Exception as e:
        print(f"❌ Error al corregir archivo: {e}")

def create_clean_file(filename="proxies.txt"):
    """Crea un archivo de proxies limpio con información actualizada"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Archivo de proxies - Codificación UTF-8\n")
            f.write("# Formatos soportados:\n")
            f.write("#   IP:PUERTO  (ej: 192.168.1.100:8080) - Listo para usar\n")
            f.write("#   IP         (ej: 192.168.1.100) - Auto-detectará puerto\n")
            f.write("# \n")
            f.write("# CARACTERÍSTICAS AVANZADAS:\n")
            f.write("# • Auto-detección de puertos para IPs sin puerto\n")
            f.write("# • Validación automática de conectividad\n")
            f.write("# • Lista de 15 puertos prioritarios más comunes\n")
            f.write("# • Backup automático antes de modificaciones\n")
            f.write("# \n")
            f.write("# PUERTOS MÁS COMUNES DETECTADOS:\n")
            f.write("# 80, 8080, 3128, 8000, 8888, 1080, 3129, 8081,\n")
            f.write("# 9000, 9090, 8123, 8118, 3127, 8001, 8008\n")
            f.write("# \n")
            f.write("# INSTRUCCIONES:\n")
            f.write("# 1. Elimina estos comentarios\n")
            f.write("# 2. Agrega tus proxies en cualquiera de estos formatos:\n")
            f.write("#    • 192.168.1.100:8080  (proxy completo)\n")
            f.write("#    • 192.168.1.100       (solo IP, se auto-detecta puerto)\n")
            f.write("# 3. Ejecuta: python proxy_validator.py (para auto-detección)\n")
            f.write("# 4. O ejecuta: python scholardown.py (detección automática)\n")
            f.write("# \n")
            f.write("# Ejemplos de formato válido:\n")
            f.write("# 123.456.789.100:8080\n")
            f.write("# 98.765.432.100:3128\n")
            f.write("# 111.222.333.444       # <- Solo IP, se detectará puerto\n")
            f.write("# 87.654.321.200:8000\n")
            f.write("\n")
        
        print(f"✅ Archivo {filename} creado con codificación UTF-8 y soporte avanzado")
        print(f"📝 Incluye información sobre auto-detección de puertos")
        
    except Exception as e:
        print(f"❌ Error creando archivo: {e}")

def main():
    print("="*70)
    print("🔧 SOLUCIONADOR DE PROBLEMAS DE CODIFICACIÓN AVANZADO")
    print("="*70)
    print("Este script diagnostica y corrige problemas de codificación")
    print("en el archivo proxies.txt, con soporte para auto-detección de puertos.")
    print("="*70)
    
    filename = "proxies.txt"
    
    if os.path.exists(filename):
        print(f"📁 Archivo encontrado: {filename}")
        fix_proxies_file(filename)
    else:
        print(f"📁 Archivo no encontrado: {filename}")
        create_clean_file(filename)
    
    print("\n" + "="*70)
    print("🎯 SOLUCIÓN COMPLETADA")
    print("="*70)
    print("💡 Nuevas características disponibles:")
    print("  • Auto-detección de puertos para IPs sin puerto")
    print("  • Soporte para formato mixto (IP:PUERTO e IP)")
    print("  • Validación paralela de conectividad")
    print("  • Backup automático antes de modificaciones")
    print("\n🚀 Próximos pasos:")
    print("  • Edita proxies.txt con tus IPs/proxies")
    print("  • Ejecuta: python proxy_validator.py (validación completa)")
    print("  • O ejecuta: python scholardown.py (proceso completo)")
    print("="*70)
    """Crea un archivo de proxies limpio"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Archivo de proxies - Codificación UTF-8\n")
            f.write("# Un proxy por línea en formato IP:PUERTO\n")
            f.write("# Ejemplo: 192.168.1.100:8080\n")
            f.write("# \n")
            f.write("# IMPORTANTE:\n")
            f.write("# • Usa solo proxies HTTP/HTTPS (no SOCKS)\n")
            f.write("# • Evita proxies que requieran autenticación\n")
            f.write("# • Formato correcto: IP:PUERTO\n")
            f.write("# \n")
            f.write("# Elimina estos comentarios y agrega tus proxies reales:\n")
            f.write("# 123.456.789.100:8080\n")
            f.write("# 98.765.432.100:3128\n")
            f.write("# 111.222.333.444:80\n")
            f.write("\n")
        
        print(f"✅ Archivo {filename} creado con codificación UTF-8")
        print(f"📝 Edita el archivo y agrega tus proxies reales")
        
    except Exception as e:
        print(f"❌ Error creando archivo: {e}")

def main():
    print("="*60)
    print("🔧 SOLUCIONADOR DE PROBLEMAS DE CODIFICACIÓN")
    print("="*60)
    print("Este script diagnostica y corrige problemas de")
    print("codificación en el archivo proxies.txt")
    print("="*60)
    
    filename = "proxies.txt"
    
    if os.path.exists(filename):
        print(f"📁 Archivo encontrado: {filename}")
        fix_proxies_file(filename)
    else:
        print(f"📁 Archivo no encontrado: {filename}")
        create_clean_file(filename)
    
    print("\n" + "="*60)
    print("🎯 SOLUCIÓN COMPLETADA")
    print("="*60)
    print("💡 Consejos:")
    print("  • Siempre guarda archivos de texto con codificación UTF-8")
    print("  • Evita copiar/pegar desde fuentes con caracteres especiales")
    print("  • Usa editores de texto que soporten UTF-8 (Notepad++, VSCode)")
    print("="*60)

if __name__ == "__main__":
    main()