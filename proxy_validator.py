#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validador de Proxies Avanzado para ScholarDown
Verifica la funcionalidad de proxies y auto-detecta puertos faltantes
"""

import time
import requests
import os
import json
from datetime import datetime
import concurrent.futures
import threading

PROXIES_FILE = "proxies.txt"
RESULTS_FILE = "proxy_validation_results.json"
MAX_WORKERS = 10  # Número de threads para validación paralela
TIMEOUT = 15  # Timeout en segundos para cada test

# Lista de puertos prioritarios para auto-detección
PUERTOS_PRIORITARIOS = [
    80,     # HTTP estándar
    8080,   # HTTP alternativo más común
    3128,   # Squid proxy estándar
    8000,   # Desarrollo/testing
    8888,   # Proxy alternativo
    1080,   # SOCKS/HTTP
    3129,   # Squid alternativo
    8081,   # HTTP alternativo
    9000,   # Proxy corporativo
    9090,   # Proxy alternativo
    8123,   # Polipo proxy
    8118,   # Privoxy
    3127,   # Squid alternativo
    8001,   # HTTP alternativo
    8008    # HTTP alternativo
]

class ProxyValidator:
    def __init__(self):
        self.valid_proxies = []
        self.invalid_proxies = []
        self.lock = threading.Lock()
        
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://icanhazip.com/", 
            "https://api.ipify.org/",
            "http://checkip.amazonaws.com/",
            "https://ipinfo.io/ip"
        ]
    
    def validate_single_proxy(self, proxy_ip, verbose=True):
        """
        Valida un único proxy
        Retorna: dict con información del resultado
        """
        if verbose:
            print(f"🔍 Validando: {proxy_ip}")
        
        # Verificar formato
        if ':' not in proxy_ip:
            return self._create_result(proxy_ip, False, "Formato inválido (falta puerto)")
        
        try:
            ip, port = proxy_ip.split(':')
            port = int(port)
            if not (1 <= port <= 65535):
                return self._create_result(proxy_ip, False, "Puerto fuera de rango")
        except ValueError:
            return self._create_result(proxy_ip, False, "Formato de puerto inválido")
        
        # Test de conectividad
        for test_url in self.test_urls:
            try:
                start_time = time.time()
                
                session = requests.Session()
                session.proxies = {
                    'http': f'http://{proxy_ip}',
                    'https': f'http://{proxy_ip}'
                }
                session.headers.update({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                })
                
                response = session.get(test_url, timeout=TIMEOUT)
                response_time = time.time() - start_time
                
                if response.status_code == 200 and len(response.text.strip()) > 0:
                    # Verificar que no sea página de error
                    error_keywords = ['login', 'password', 'authentication', 'unauthorized', 
                                    'forbidden', 'error', 'access denied', 'proxy authentication']
                    
                    if not any(keyword in response.text.lower() for keyword in error_keywords):
                        # Intentar extraer IP para verificar que el proxy funciona
                        try:
                            returned_ip = response.text.strip().strip('"')
                            if self._is_valid_ip_format(returned_ip):
                                result = self._create_result(proxy_ip, True, "OK", response_time, returned_ip, test_url)
                                if verbose:
                                    print(f"   ✅ Válido - {response_time:.2f}s - IP: {returned_ip}")
                                return result
                        except:
                            # Si no podemos extraer IP, pero la respuesta es válida, asumir que funciona
                            result = self._create_result(proxy_ip, True, "OK", response_time, "unknown", test_url)
                            if verbose:
                                print(f"   ✅ Válido - {response_time:.2f}s")
                            return result
                
            except requests.exceptions.ProxyError as e:
                if "authentication" in str(e).lower():
                    result = self._create_result(proxy_ip, False, "Requiere autenticación")
                    if verbose:
                        print(f"   🔒 Requiere autenticación")
                    return result
                continue
                
            except requests.exceptions.ConnectTimeout:
                continue  # Probar siguiente URL
                
            except requests.exceptions.ReadTimeout:
                continue  # Probar siguiente URL
                
            except requests.exceptions.ConnectionError as e:
                if "authentication" in str(e).lower() or "407" in str(e):
                    result = self._create_result(proxy_ip, False, "Requiere autenticación")
                    if verbose:
                        print(f"   🔒 Requiere autenticación")
                    return result
                continue
                
            except Exception as e:
                continue  # Probar siguiente URL
        
        # Si llegamos aquí, falló en todas las URLs
        result = self._create_result(proxy_ip, False, "No responde en ninguna URL de test")
        if verbose:
            print(f"   ❌ No funciona")
        return result
    
    def auto_detect_ports_for_ip(self, ip, verbose=True):
        """
        Auto-detecta el puerto correcto para una IP específica
        Retorna: (puerto_encontrado, response_time) o (None, None)
        """
        if verbose:
            print(f"🔍 Auto-detectando puerto para: {ip}")
        
        for i, puerto in enumerate(PUERTOS_PRIORITARIOS, 1):
            proxy_address = f"{ip}:{puerto}"
            
            try:
                if verbose:
                    print(f"   [{i}/{len(PUERTOS_PRIORITARIOS)}] Probando puerto {puerto}...")
                
                result = self.validate_single_proxy(proxy_address, verbose=False)
                
                if result['valid']:
                    if verbose:
                        print(f"   ✅ Puerto {puerto} VÁLIDO ({result['response_time']:.2f}s)")
                    return puerto, result['response_time']
                else:
                    if verbose and "autenticación" in result['error'].lower():
                        print(f"   🔒 Puerto {puerto}: Requiere autenticación")
                    elif verbose and i <= 3:  # Solo mostrar primeros errores
                        print(f"   ❌ Puerto {puerto}: {result['error']}")
                        
            except Exception as e:
                if verbose and i <= 3:
                    print(f"   ❌ Puerto {puerto}: Error - {str(e)[:30]}...")
                continue
        
        if verbose:
            print(f"   ❌ No se encontró puerto válido para {ip}")
        return None, None
    
    def auto_detect_proxy_ports(self, ip_list, max_workers=8):
        """
        Auto-detecta puertos para una lista de IPs usando threading
        """
        print(f"🔍 Iniciando auto-detección de puertos para {len(ip_list)} IPs...")
        print(f"⚙️  Configuración: {max_workers} threads, {len(PUERTOS_PRIORITARIOS)} puertos prioritarios")
        print(f"🎯 Puertos a probar: {PUERTOS_PRIORITARIOS}")
        print("="*70)
        
        valid_proxies = []
        processed_count = 0
        lock = threading.Lock()
        
        def process_ip(ip):
            nonlocal processed_count
            
            with lock:
                processed_count += 1
                current = processed_count
            
            print(f"[IP {current}/{len(ip_list)}] {ip} - Probando puertos prioritarios...")
            
            puerto, response_time = self.auto_detect_ports_for_ip(ip, verbose=False)
            
            if puerto:
                with lock:
                    valid_proxies.append({
                        'proxy': f"{ip}:{puerto}",
                        'valid': True,
                        'response_time': response_time,
                        'error': None,
                        'returned_ip': 'detected',
                        'test_url': 'auto-detection',
                        'timestamp': datetime.now().isoformat(),
                        'detected_port': puerto
                    })
                print(f"   ✅ Puerto {puerto} VÁLIDO ({response_time:.2f}s)")
                return True
            else:
                print(f"   ❌ Ningún puerto válido encontrado")
                return False
        
        # Ejecutar con ThreadPoolExecutor
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {executor.submit(process_ip, ip): ip for ip in ip_list}
            
            for future in concurrent.futures.as_completed(future_to_ip):
                try:
                    future.result()
                except Exception as e:
                    ip = future_to_ip[future]
                    print(f"   ❌ Error procesando {ip}: {e}")
        
        elapsed_time = time.time() - start_time
        
        # Actualizar listas principales
        self.valid_proxies.extend(valid_proxies)
        
        # Mostrar resumen
        print("\n" + "="*70)
        print("📊 RESUMEN DE AUTO-DETECCIÓN")
        print("="*70)
        print(f"IPs procesadas:     {len(ip_list)}")
        print(f"✅ Proxies válidos:  {len(valid_proxies)} ({len(valid_proxies)/len(ip_list)*100:.1f}%)")
        print(f"❌ IPs sin puerto:   {len(ip_list) - len(valid_proxies)}")
        print(f"⏱️  Tiempo total:     {elapsed_time:.1f}s ({elapsed_time/60:.1f} min)")
        print(f"⚡ Velocidad:        {len(ip_list)/(elapsed_time or 1):.1f} IPs/seg")
        
        if valid_proxies:
            # Estadísticas de puertos
            port_stats = {}
            for proxy_data in valid_proxies:
                port = proxy_data.get('detected_port')
                if port:
                    port_stats[port] = port_stats.get(port, 0) + 1
            
            print(f"📈 Puertos más exitosos:")
            for port, count in sorted(port_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   Puerto {port}: {count} proxies ({count/len(valid_proxies)*100:.1f}%)")
        
        print("="*70)
        
        return len(valid_proxies)
    
    def validate_proxy_list(self, proxy_list, parallel=True, max_workers=MAX_WORKERS):
        """
        Valida una lista de proxies
        """
        print(f"🚀 Iniciando validación de {len(proxy_list)} proxies...")
        print(f"⚙️  Configuración: {'Paralelo' if parallel else 'Secuencial'} - Timeout: {TIMEOUT}s")
        print("="*60)
        
        if parallel and len(proxy_list) > 1:
            # Validación paralela
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_proxy = {
                    executor.submit(self.validate_single_proxy, proxy, False): proxy 
                    for proxy in proxy_list
                }
                
                completed = 0
                for future in concurrent.futures.as_completed(future_to_proxy):
                    result = future.result()
                    completed += 1
                    
                    with self.lock:
                        if result['valid']:
                            self.valid_proxies.append(result)
                            print(f"[{completed}/{len(proxy_list)}] ✅ {result['proxy']} - {result['response_time']:.2f}s")
                        else:
                            self.invalid_proxies.append(result)
                            print(f"[{completed}/{len(proxy_list)}] ❌ {result['proxy']} - {result['error']}")
        else:
            # Validación secuencial
            for i, proxy in enumerate(proxy_list, 1):
                print(f"[{i}/{len(proxy_list)}] ", end="")
                result = self.validate_single_proxy(proxy, verbose=False)
                
                if result['valid']:
                    self.valid_proxies.append(result)
                    print(f"✅ {result['proxy']} - {result['response_time']:.2f}s")
                else:
                    self.invalid_proxies.append(result)
                    print(f"❌ {result['proxy']} - {result['error']}")
    
    def create_updated_proxy_file(self, output_file="proxies.txt"):
        """Crea archivo actualizado con proxies auto-detectados"""
        if not self.valid_proxies:
            print("❌ No hay proxies válidos para actualizar el archivo")
            return False
        
        # Crear backup del original
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"proxies_original_backup_{timestamp}.txt"
        
        try:
            if os.path.exists(output_file):
                import shutil
                shutil.copy2(output_file, backup_file)
                print(f"💾 Backup creado: {backup_file}")
            
            # Ordenar proxies por tiempo de respuesta
            sorted_proxies = sorted(self.valid_proxies, key=lambda x: x['response_time'] or 999)
            
            # Crear archivo actualizado
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Proxies auto-detectados - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Método: Lista prioritaria ({len(PUERTOS_PRIORITARIOS)} puertos comunes)\n")
                f.write(f"# Válidos encontrados: {len(sorted_proxies)} proxies\n")
                f.write(f"# Archivo original respaldado como: {backup_file}\n")
                f.write(f"# \n")
                f.write(f"# Formato: IP:PUERTO (un proxy por línea)\n")
                f.write(f"# Solo proxies verificados y funcionales\n")
                f.write(f"\n")
                
                for proxy_data in sorted_proxies:
                    f.write(f"{proxy_data['proxy']}\n")
            
            print(f"✅ Archivo {output_file} actualizado con {len(sorted_proxies)} proxies válidos")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando archivo: {e}")
            return False
    
    def save_results(self, filename=RESULTS_FILE):
        """Guarda los resultados en un archivo JSON"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_tested': len(self.valid_proxies) + len(self.invalid_proxies),
            'valid_count': len(self.valid_proxies),
            'invalid_count': len(self.invalid_proxies),
            'valid_proxies': sorted(self.valid_proxies, key=lambda x: x['response_time'] or 999),
            'invalid_proxies': self.invalid_proxies,
            'config': {
                'timeout': TIMEOUT,
                'test_urls': self.test_urls,
                'priority_ports': PUERTOS_PRIORITARIOS
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {filename}")
    
    def create_filtered_proxy_file(self, output_file="proxies_valid.txt"):
        """Crea un archivo solo con los proxies válidos"""
        if not self.valid_proxies:
            print("❌ No hay proxies válidos para guardar")
            return
        
        # Ordenar por tiempo de respuesta
        sorted_proxies = sorted(self.valid_proxies, key=lambda x: x['response_time'] or 999)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Proxies válidos - Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total: {len(sorted_proxies)} proxies funcionales\n")
            f.write(f"# Ordenados por velocidad de respuesta\n\n")
            
            for proxy_data in sorted_proxies:
                f.write(f"{proxy_data['proxy']}\n")
        
        print(f"📄 Archivo de proxies válidos creado: {output_file}")
    
    def print_summary(self):
        """Muestra un resumen de los resultados"""
        total = len(self.valid_proxies) + len(self.invalid_proxies)
        
        if total == 0:
            print("\n📊 No hay datos para mostrar resumen")
            return
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE VALIDACIÓN")
        print("="*60)
        print(f"Total testados:    {total}")
        print(f"✅ Válidos:        {len(self.valid_proxies)} ({len(self.valid_proxies)/total*100:.1f}%)")
        print(f"❌ Inválidos:      {len(self.invalid_proxies)} ({len(self.invalid_proxies)/total*100:.1f}%)")
        
        if self.valid_proxies:
            valid_with_time = [p for p in self.valid_proxies if p.get('response_time')]
            if valid_with_time:
                avg_time = sum(p['response_time'] for p in valid_with_time) / len(valid_with_time)
                fastest = min(valid_with_time, key=lambda x: x['response_time'])
                slowest = max(valid_with_time, key=lambda x: x['response_time'])
                
                print(f"\n⚡ Estadísticas de velocidad:")
                print(f"Tiempo promedio:   {avg_time:.2f}s")
                print(f"Más rápido:        {fastest['proxy']} ({fastest['response_time']:.2f}s)")
                print(f"Más lento:         {slowest['proxy']} ({slowest['response_time']:.2f}s)")
            
            # Estadísticas de puertos detectados
            detected_ports = {}
            for proxy_data in self.valid_proxies:
                if 'detected_port' in proxy_data:
                    port = proxy_data['detected_port']
                    detected_ports[port] = detected_ports.get(port, 0) + 1
            
            if detected_ports:
                print(f"\n🎯 Puertos detectados:")
                for port, count in sorted(detected_ports.items(), key=lambda x: x[1], reverse=True):
                    print(f"  Puerto {port}: {count} proxies ({count/len(self.valid_proxies)*100:.1f}%)")
        
        if self.invalid_proxies:
            # Contar tipos de errores
            error_counts = {}
            for proxy in self.invalid_proxies:
                error = proxy['error']
                error_counts[error] = error_counts.get(error, 0) + 1
            
            print(f"\n❌ Tipos de errores:")
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {error}: {count}")
        
        print("="*60)
    
    def _create_result(self, proxy_ip, is_valid, error_msg="", response_time=None, returned_ip=None, test_url=None):
        """Crea un diccionario de resultado estandarizado"""
        return {
            'proxy': proxy_ip,
            'valid': is_valid,
            'response_time': response_time,
            'error': error_msg,
            'returned_ip': returned_ip,
            'test_url': test_url,
            'timestamp': datetime.now().isoformat()
        }
    
    def _is_valid_ip_format(self, ip_str):
        """Verifica si el string parece una dirección IP válida"""
        try:
            parts = ip_str.split('.')
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except:
            return False

def load_proxies_from_file(filename=PROXIES_FILE):
    """Carga proxies desde archivo con manejo de codificaciones y auto-detección"""
    try:
        # Intentar diferentes codificaciones comunes
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        raw_lines = []
        
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as f:
                    raw_lines = [line.strip() for line in f if line.strip()]
                
                print(f"📂 Archivo leído correctamente con codificación {encoding}")
                break
                
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"❌ Error con codificación {encoding}: {e}")
                continue
        
        if not raw_lines:
            print(f"❌ No se pudo leer {filename} con ninguna codificación")
            return [], []
        
        # Separar IPs sin puerto de proxies completos
        ips_without_port = []
        proxies_with_port = []
        
        for line in raw_lines:
            if line.startswith('#'):
                continue
                
            if ':' in line:
                # Ya tiene formato IP:PUERTO
                try:
                    ip, port = line.split(':')
                    port = int(port)
                    if 1 <= port <= 65535:
                        proxies_with_port.append(line)
                    else:
                        print(f"⚠️  Puerto inválido en: {line}")
                except ValueError:
                    print(f"⚠️  Formato inválido: {line}")
            else:
                # Solo IP, necesita auto-detección de puerto
                if line.replace('.', '').replace(' ', '').isdigit() or '.' in line:
                    ips_without_port.append(line)
        
        print(f"📊 Análisis del archivo:")
        print(f"  • Proxies con puerto: {len(proxies_with_port)}")
        print(f"  • IPs sin puerto: {len(ips_without_port)}")
        
        return proxies_with_port, ips_without_port
        
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo {filename}")
        return [], []
    except Exception as e:
        print(f"❌ Error al leer {filename}: {e}")
        return [], []

def main():
    print("="*70)
    print("🔍 VALIDADOR DE PROXIES AVANZADO - ScholarDown")
    print("="*70)
    print("Este script valida proxies y auto-detecta puertos faltantes")
    print("para usar en el scraping de Google Scholar.")
    print("="*70)
    
    # Cargar proxies
    proxies_with_port, ips_without_port = load_proxies_from_file()
    
    if not proxies_with_port and not ips_without_port:
        print("\n❌ No hay proxies para validar.")
        print("💡 Asegúrate de tener un archivo 'proxies.txt' con:")
        print("   • Proxies completos: IP:PUERTO")
        print("   • IPs sin puerto: IP (se auto-detectará el puerto)")
        return
    
    # Inicializar validador
    validator = ProxyValidator()
    
    # Auto-detectar puertos si hay IPs sin puerto
    if ips_without_port:
        print(f"\n🔍 AUTO-DETECCIÓN DE PUERTOS")
        print(f"Se encontraron {len(ips_without_port)} IPs sin puerto especificado.")
        
        auto_detect = input("¿Desea auto-detectar los puertos? (s/n): ").lower().startswith('s')
        
        if auto_detect:
            # Configurar paralelización
            try:
                workers = int(input(f"Threads paralelos (1-20, default 8): ") or 8)
                workers = max(1, min(20, workers))
            except:
                workers = 8
            
            print(f"\n🚀 Iniciando auto-detección con {workers} threads...")
            detected_count = validator.auto_detect_proxy_ports(ips_without_port, workers)
            
            if detected_count > 0:
                print(f"\n✅ {detected_count} proxies detectados exitosamente!")
                
                # Preguntar si actualizar archivo
                update_file = input("¿Actualizar proxies.txt con los puertos detectados? (s/n): ").lower().startswith('s')
                if update_file:
                    validator.create_updated_proxy_file()
                    
                    # Re-cargar archivo actualizado
                    proxies_with_port, _ = load_proxies_from_file()
            else:
                print(f"\n❌ No se detectaron puertos válidos para las IPs sin puerto")
    
    # Validar proxies con puerto
    if proxies_with_port:
        print(f"\n🔍 VALIDACIÓN DE CONECTIVIDAD")
        print(f"Validando {len(proxies_with_port)} proxies con puerto especificado...")
        
        # Configuración de validación
        try:
            parallel = input("¿Validación paralela? (s/n, default: s): ").lower()
            parallel = parallel != 'n'
        except:
            parallel = True
        
        if parallel:
            try:
                workers = int(input(f"Threads paralelos (1-20, default {MAX_WORKERS}): ") or MAX_WORKERS)
                workers = max(1, min(20, workers))
            except:
                workers = MAX_WORKERS
        else:
            workers = 1
        
        # Ejecutar validación
        start_time = time.time()
        validator.validate_proxy_list(proxies_with_port, parallel=parallel, max_workers=workers)
        total_time = time.time() - start_time
        
        # Mostrar resultados
        validator.print_summary()
        print(f"\n⏱️  Tiempo total: {total_time:.1f}s")
        
        # Guardar resultados
        validator.save_results()
        
        if validator.valid_proxies:
            # Crear archivo final con todos los proxies válidos
            create_final = input(f"\n💾 ¿Crear archivo final con todos los proxies válidos? (s/n): ").lower().startswith('s')
            if create_final:
                validator.create_filtered_proxy_file()
    
    # Recomendaciones finales
    total_valid = len(validator.valid_proxies)
    print(f"\n💡 Recomendaciones:")
    if total_valid >= 20:
        print(f"   ✅ Excelente cantidad de proxies válidos ({total_valid})")
    elif total_valid >= 10:
        print(f"   ✅ Buena cantidad de proxies válidos ({total_valid})")
    elif total_valid >= 5:
        print(f"   ⚠️  Pocos proxies válidos ({total_valid}). Considera conseguir más.")
    else:
        print(f"   ❌ Muy pocos proxies válidos ({total_valid}). Necesitas más proxies de calidad.")
    
    if validator.valid_proxies:
        valid_with_time = [p for p in validator.valid_proxies if p.get('response_time')]
        if valid_with_time:
            avg_time = sum(p['response_time'] for p in valid_with_time) / len(valid_with_time)
            if avg_time < 3:
                print(f"   ⚡ Velocidad excelente (promedio: {avg_time:.2f}s)")
            elif avg_time < 6:
                print(f"   🚀 Velocidad buena (promedio: {avg_time:.2f}s)")
            else:
                print(f"   🐌 Velocidad lenta (promedio: {avg_time:.2f}s). Considera proxies más rápidos.")
    
    print(f"\n🎯 Los proxies válidos están listos para usar con ScholarDown!")

if __name__ == "__main__":
    main()