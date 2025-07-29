import os
import subprocess
import time
import random
import json
import hashlib
import base64
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
from urllib.parse import urlparse, urljoin

# Archivos
INPUT_FILE = "papers.txt"
OUTPUT_FILE = "papers2.txt"
PROGRESS_FILE = "progress.json"
PROXIES_FILE = "proxies.txt"

# Configuración TOR
TOR_EXE = r"C:\Tor Browser\Browser\TorBrowser\Tor\tor.exe"
TOR_CONTROL_PORT = 9051
TOR_SOCKS_PORT = 9050
CONTROL_PASSWORD = ""
ROTATE_EVERY = 15
MAX_RETRIES = 5

# Variables globales para manejo de proxies y sesiones
proxy_list = []
validated_proxies = []
failed_proxies = []
current_proxy_index = 0
using_proxy = False
tor_blocked = False
session_cookies = {}
canvas_fingerprint = None
webgl_fingerprint = None

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

class AdvancedBrowserSimulator:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ]
        
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
            (1280, 720), (1600, 900), (2560, 1440), (1920, 1200)
        ]
        
        self.languages = {
            'Chrome': ['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'es-ES,es;q=0.8,en;q=0.7'],
            'Firefox': ['en-US,en;q=0.5', 'en-GB,en;q=0.5', 'es-ES,es;q=0.8,en;q=0.6'],
            'Safari': ['en-US', 'en-GB', 'es-ES']
        }
        
        self.current_profile = self.generate_browser_profile()
    
    def generate_browser_profile(self):
        """Genera un perfil de navegador coherente"""
        user_agent = random.choice(self.user_agents)
        browser_type = self.detect_browser_type(user_agent)
        screen_res = random.choice(self.screen_resolutions)
        
        profile = {
            'user_agent': user_agent,
            'browser_type': browser_type,
            'screen_resolution': screen_res,
            'language': random.choice(self.languages.get(browser_type, self.languages['Chrome'])),
            'timezone': random.choice(['America/New_York', 'Europe/London', 'Europe/Madrid', 'America/Los_Angeles']),
            'canvas_fingerprint': self.generate_canvas_fingerprint(),
            'webgl_fingerprint': self.generate_webgl_fingerprint(),
            'platform': self.extract_platform(user_agent),
            'do_not_track': random.choice(['1', '0']),
        }
        
        return profile
    
    def detect_browser_type(self, user_agent):
        if 'Chrome' in user_agent and 'Safari' in user_agent:
            return 'Chrome'
        elif 'Firefox' in user_agent:
            return 'Firefox'
        elif 'Safari' in user_agent and 'Chrome' not in user_agent:
            return 'Safari'
        return 'Chrome'
    
    def extract_platform(self, user_agent):
        if 'Windows NT 10.0' in user_agent:
            return 'Win32'
        elif 'Macintosh' in user_agent:
            return 'MacIntel'
        elif 'Linux' in user_agent:
            return 'Linux x86_64'
        return 'Win32'
    
    def generate_canvas_fingerprint(self):
        """Simula un canvas fingerprint único pero realista"""
        base_data = f"{random.randint(1000000, 9999999)}{time.time()}"
        return hashlib.md5(base_data.encode()).hexdigest()[:16]
    
    def generate_webgl_fingerprint(self):
        """Simula un WebGL fingerprint"""
        gpu_vendors = ['NVIDIA Corporation', 'AMD', 'Intel Inc.', 'Apple']
        gpu_models = {
            'NVIDIA Corporation': ['GeForce RTX 3060', 'GeForce GTX 1660', 'GeForce RTX 4070'],
            'AMD': ['Radeon RX 6600', 'Radeon RX 5700 XT', 'Radeon RX 7800 XT'],
            'Intel Inc.': ['Intel Iris Xe Graphics', 'Intel UHD Graphics 630'],
            'Apple': ['Apple M1', 'Apple M2', 'Apple M1 Pro']
        }
        
        vendor = random.choice(gpu_vendors)
        model = random.choice(gpu_models[vendor])
        
        return {
            'vendor': vendor,
            'renderer': model,
            'version': f"OpenGL ES 3.0 ({model})"
        }
    
    def get_coherent_headers(self, url=None, referer=None):
        """Genera headers coherentes con el perfil del navegador"""
        profile = self.current_profile
        
        # Headers base ordenados de forma realista
        base_headers = [
            ('User-Agent', profile['user_agent']),
            ('Accept', self.get_accept_header(profile['browser_type'])),
            ('Accept-Language', profile['language']),
            ('Accept-Encoding', 'gzip, deflate, br'),
            ('DNT', profile['do_not_track']),
            ('Connection', 'keep-alive'),
            ('Upgrade-Insecure-Requests', '1'),
        ]
        
        # Headers específicos del navegador
        if profile['browser_type'] == 'Chrome':
            base_headers.extend([
                ('Sec-Fetch-Dest', 'document'),
                ('Sec-Fetch-Mode', 'navigate'),
                ('Sec-Fetch-Site', 'none' if not referer else 'same-origin'),
                ('Sec-CH-UA', self.get_sec_ch_ua(profile['user_agent'])),
                ('Sec-CH-UA-Mobile', '?0'),
                ('Sec-CH-UA-Platform', f'"{self.get_platform_name(profile["platform"])}"'),
            ])
        
        # Agregar referer si existe
        if referer:
            base_headers.insert(-2, ('Referer', referer))
        
        # Cache control ocasional
        if random.random() < 0.3:
            base_headers.append(('Cache-Control', 'no-cache'))
            base_headers.append(('Pragma', 'no-cache'))
        
        # Randomizar ligeramente el orden manteniendo coherencia
        headers = dict(base_headers)
        
        return headers
    
    def get_accept_header(self, browser_type):
        accept_headers = {
            'Chrome': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Firefox': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Safari': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        return accept_headers.get(browser_type, accept_headers['Chrome'])
    
    def get_sec_ch_ua(self, user_agent):
        if 'Chrome/119' in user_agent:
            return '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"'
        elif 'Chrome/118' in user_agent:
            return '"Google Chrome";v="118", "Chromium";v="118", "Not=A?Brand";v="99"'
        return '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"'
    
    def get_platform_name(self, platform):
        platform_names = {
            'Win32': 'Windows',
            'MacIntel': 'macOS',
            'Linux x86_64': 'Linux'
        }
        return platform_names.get(platform, 'Windows')
    
    def simulate_human_behavior(self, session, url):
        """Simula comportamiento humano antes de la request principal"""
        
        # 1. Ocasionalmente simular navegación previa
        if random.random() < 0.15:  # 15% de probabilidad
            print("   [HUMAN] Simulando navegación previa...")
            
            # Visitar página principal de Scholar ocasionalmente
            if random.random() < 0.5:
                try:
                    scholar_main = "https://scholar.google.es/"
                    pre_headers = self.get_coherent_headers(scholar_main)
                    session.get(scholar_main, headers=pre_headers, timeout=10)
                    time.sleep(random.uniform(1, 3))
                except:
                    pass
        
        # 2. Simular errores humanos ocasionales
        if random.random() < 0.08:  # 8% de probabilidad
            print("   [HUMAN] Simulando error humano (URL incorrecta)...")
            try:
                # Simular typo en URL o click erróneo
                wrong_url = url.replace('citations', 'citationz')  # typo simulado
                error_headers = self.get_coherent_headers(wrong_url)
                session.get(wrong_url, headers=error_headers, timeout=5)
                time.sleep(random.uniform(0.5, 1.5))
            except:
                pass
        
        # 3. Pausa de "lectura" variable
        reading_time = random.uniform(0.5, 2.0)
        if random.random() < 0.1:  # 10% de probabilidad de pausa larga
            reading_time = random.uniform(3, 8)
            print(f"   [HUMAN] Pausa de lectura larga: {reading_time:.1f}s")
        
        time.sleep(reading_time)
    
    def rotate_profile(self):
        """Rota el perfil del navegador periódicamente"""
        if random.random() < 0.1:  # 10% de probabilidad
            print("   [FINGERPRINT] Rotando perfil de navegador...")
            self.current_profile = self.generate_browser_profile()

class SessionManager:
    def __init__(self):
        self.cookies_store = {}
        self.session_data = {}
    
    def get_realistic_cookies(self, domain):
        """Genera cookies realistas para el dominio"""
        if domain not in self.cookies_store:
            self.cookies_store[domain] = {
                'GSP': f'ID={random.randint(100000, 999999)}:T={int(time.time())}:S={random.choice(["ALNI", "ANID", "HSID"])}',
                'CONSENT': f'YES+cb.{datetime.now().year}{random.randint(10,12)}.es+V{random.randint(8,14)}+BX+{random.randint(100,999)}',
                '_ga': f'GA1.3.{random.randint(1000000000, 9999999999)}.{int(time.time())}',
                'NID': ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=64)),
            }
            
            # Ocasionalmente agregar cookies adicionales
            if random.random() < 0.3:
                self.cookies_store[domain]['SID'] = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=32))
            
        return self.cookies_store[domain]
    
    def update_session_cookies(self, session, response):
        """Actualiza cookies de sesión basadas en la respuesta"""
        domain = urlparse(response.url).netloc
        
        # Simular Set-Cookie processing
        for cookie in response.cookies:
            if domain not in self.cookies_store:
                self.cookies_store[domain] = {}
            self.cookies_store[domain][cookie.name] = cookie.value

def validate_proxy(proxy_ip, timeout=10):
    """
    Valida si un proxy funciona correctamente
    Retorna: (is_valid, response_time, error_message)
    """
    test_urls = [
        "http://httpbin.org/ip",  # Servicio simple para test
        "http://icanhazip.com/",  # Backup
        "https://api.ipify.org/"  # HTTPS test
    ]
    
    print(f"   [VALIDANDO] Probando proxy: {proxy_ip}")
    
    for test_url in test_urls:
        try:
            start_time = time.time()
            
            # Configurar sesión con el proxy
            test_session = requests.Session()
            test_session.proxies = {
                'http': f'http://{proxy_ip}:80',
                'https': f'http://{proxy_ip}:80'
            }
            test_session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            # Realizar test request
            response = test_session.get(test_url, timeout=timeout)
            response_time = time.time() - start_time
            
            # Verificar respuesta válida
            if response.status_code == 200 and len(response.text.strip()) > 0:
                # Verificar que no sea una página de error/auth
                if not any(keyword in response.text.lower() for keyword in 
                          ['login', 'password', 'authentication', 'unauthorized', 'forbidden', 'error']):
                    print(f"   [✓] Proxy válido - Tiempo: {response_time:.2f}s")
                    return True, response_time, None
            
        except requests.exceptions.ProxyError as e:
            error_msg = f"Error de proxy: {str(e)}"
            if "authentication" in str(e).lower() or "password" in str(e).lower():
                print(f"   [✗] Proxy requiere autenticación")
                return False, None, "Requiere autenticación"
        except requests.exceptions.ConnectTimeout:
            print(f"   [✗] Proxy timeout de conexión")
            return False, None, "Timeout de conexión"
        except requests.exceptions.ReadTimeout:
            print(f"   [✗] Proxy timeout de lectura")
            return False, None, "Timeout de lectura"
        except requests.exceptions.ConnectionError as e:
            if "authentication" in str(e).lower():
                print(f"   [✗] Proxy requiere autenticación")
                return False, None, "Requiere autenticación"
            else:
                print(f"   [✗] Error de conexión")
                return False, None, f"Error de conexión: {str(e)[:50]}"
        except Exception as e:
            print(f"   [✗] Error inesperado: {str(e)[:50]}")
            continue
    
    return False, None, "Falló en todas las URLs de test"

def auto_detect_proxy_ports(ip_list, max_workers=8):
    """
    Auto-detecta puertos para una lista de IPs usando threading
    Retorna: lista de tuplas (ip, puerto) para proxies válidos
    """
    import concurrent.futures
    import threading
    
    print(f"🔍 Iniciando auto-detección de puertos para {len(ip_list)} IPs...")
    print(f"⚙️  Configuración: {max_workers} threads, {len(PUERTOS_PRIORITARIOS)} puertos prioritarios")
    print(f"🎯 Puertos a probar: {PUERTOS_PRIORITARIOS}")
    print("="*70)
    
    valid_proxies = []
    processed_count = 0
    lock = threading.Lock()
    
    def test_ip_ports(ip):
        """Prueba todos los puertos prioritarios para una IP específica"""
        nonlocal processed_count
        
        with lock:
            processed_count += 1
            current = processed_count
        
        print(f"[IP {current}/{len(ip_list)}] {ip} - Probando puertos prioritarios...")
        
        # Probar cada puerto hasta encontrar uno válido
        for i, puerto in enumerate(PUERTOS_PRIORITARIOS, 1):
            proxy_address = f"{ip}:{puerto}"
            
            try:
                is_valid, response_time, error = validate_proxy(proxy_address, timeout=5)
                
                if is_valid:
                    with lock:
                        valid_proxies.append((ip, puerto, response_time))
                    print(f"   ✅ Puerto {puerto} VÁLIDO ({response_time:.2f}s) - Guardando...")
                    return True  # Stop-on-first-success
                else:
                    # Solo mostrar errores importantes, no todos los timeouts
                    if "autenticación" in str(error).lower():
                        print(f"   🔒 Puerto {puerto}: Requiere autenticación")
                    elif i <= 3:  # Solo mostrar primeros 3 fallos para no saturar
                        print(f"   ⏭️  Puerto {puerto}: {error}")
                        
            except Exception as e:
                if i <= 3:  # Solo mostrar primeros errores
                    print(f"   ❌ Puerto {puerto}: Error - {str(e)[:30]}...")
                continue
        
        print(f"   ❌ Ningún puerto válido encontrado para {ip}")
        return False
    
    # Ejecutar con ThreadPoolExecutor
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Enviar todas las tareas
        future_to_ip = {executor.submit(test_ip_ports, ip): ip for ip in ip_list}
        
        # Procesar resultados conforme se completan
        for future in concurrent.futures.as_completed(future_to_ip):
            try:
                future.result()  # Esto manejará cualquier excepción
            except Exception as e:
                ip = future_to_ip[future]
                print(f"   ❌ Error procesando {ip}: {e}")
    
    elapsed_time = time.time() - start_time
    
    # Mostrar resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE AUTO-DETECCIÓN")
    print("="*70)
    print(f"IPs procesadas:     {len(ip_list)}")
    print(f"✅ Proxies válidos:  {len(valid_proxies)} ({len(valid_proxies)/len(ip_list)*100:.1f}%)")
    print(f"❌ IPs sin puerto:   {len(ip_list) - len(valid_proxies)}")
    print(f"⏱️  Tiempo total:     {elapsed_time:.1f}s ({elapsed_time/60:.1f} min)")
    print(f"⚡ Velocidad:        {len(ip_list)/elapsed_time:.1f} IPs/seg")
    
    if valid_proxies:
        # Ordenar por tiempo de respuesta
        valid_proxies.sort(key=lambda x: x[2])
        fastest = valid_proxies[0]
        print(f"🚀 Proxy más rápido: {fastest[0]}:{fastest[1]} ({fastest[2]:.2f}s)")
        
        # Estadísticas de puertos
        port_stats = {}
        for _, port, _ in valid_proxies:
            port_stats[port] = port_stats.get(port, 0) + 1
        
        print(f"📈 Puertos más exitosos:")
        for port, count in sorted(port_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   Puerto {port}: {count} proxies ({count/len(valid_proxies)*100:.1f}%)")
    
    print("="*70)
    
    return valid_proxies

def create_backup_and_update_file(original_file, valid_proxies):
    """
    Crea backup del archivo original y actualiza con proxies válidos
    """
    from datetime import datetime
    
    # Crear nombre de backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"proxies_original_backup_{timestamp}.txt"
    
    try:
        # Crear backup del archivo original
        if os.path.exists(original_file):
            import shutil
            shutil.copy2(original_file, backup_file)
            print(f"💾 Backup creado: {backup_file}")
        
        # Crear archivo actualizado con proxies válidos
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(f"# Proxies auto-detectados - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Método: Lista prioritaria ({len(PUERTOS_PRIORITARIOS)} puertos comunes)\n")
            f.write(f"# Escaneados: {len(valid_proxies)} IPs | Válidos: {len([p for p in valid_proxies if len(p) >= 3])} | Tasa éxito: {len([p for p in valid_proxies if len(p) >= 3])/len(valid_proxies)*100:.1f}%\n")
            f.write(f"# Archivo original respaldado como: {backup_file}\n")
            f.write(f"# \n")
            f.write(f"# Formato: IP:PUERTO (un proxy por línea)\n")
            f.write(f"# Solo proxies verificados y funcionales\n")
            f.write(f"\n")
            
            # Escribir proxies válidos ordenados por velocidad
            sorted_proxies = sorted(valid_proxies, key=lambda x: x[2] if len(x) >= 3 else 999)
            for ip, port, response_time in sorted_proxies:
                f.write(f"{ip}:{port}\n")
        
        print(f"✅ Archivo {original_file} actualizado con {len(valid_proxies)} proxies válidos")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando archivo: {e}")
        return False

def load_and_validate_proxies():
    """Carga y valida la lista de proxies desde el archivo con auto-detección de puertos"""
    global proxy_list, validated_proxies, failed_proxies
    
    try:
        # Intentar diferentes codificaciones
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        raw_lines = []
        successful_encoding = None
        
        for encoding in encodings:
            try:
                with open(PROXIES_FILE, "r", encoding=encoding) as f:
                    raw_lines = [line.strip() for line in f if line.strip()]
                print(f"[INFO] Archivo leído correctamente con codificación {encoding}")
                successful_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"[WARNING] Error con codificación {encoding}: {e}")
                continue
        
        if not raw_lines:
            print(f"[ERROR] No se pudo leer el archivo {PROXIES_FILE} o está vacío")
            return False
        
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
                        print(f"[WARNING] Puerto inválido en: {line}")
                except ValueError:
                    print(f"[WARNING] Formato inválido: {line}")
            else:
                # Solo IP, necesita auto-detección de puerto
                if line.replace('.', '').replace(' ', '').isdigit() or '.' in line:
                    ips_without_port.append(line)
        
        print(f"[INFO] Análisis inicial:")
        print(f"  • Proxies con puerto: {len(proxies_with_port)}")
        print(f"  • IPs sin puerto: {len(ips_without_port)}")
        
        # Auto-detectar puertos para IPs sin puerto
        if ips_without_port:
            print(f"\n[INFO] Iniciando auto-detección de puertos para {len(ips_without_port)} IPs...")
            
            valid_auto_detected = auto_detect_proxy_ports(ips_without_port)
            
            if valid_auto_detected:
                # Actualizar archivo con proxies auto-detectados
                all_valid_proxies = valid_auto_detected.copy()
                
                # Añadir proxies que ya tenían puerto (validarlos después)
                for proxy in proxies_with_port:
                    ip, port = proxy.split(':')
                    all_valid_proxies.append((ip, int(port), 0))  # 0 como placeholder de tiempo
                
                # Crear backup y actualizar archivo
                create_backup_and_update_file(PROXIES_FILE, all_valid_proxies)
                
                # Re-cargar archivo actualizado
                with open(PROXIES_FILE, "r", encoding='utf-8') as f:
                    updated_lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                proxies_with_port = updated_lines
                print(f"[INFO] Archivo actualizado. Ahora validando {len(proxies_with_port)} proxies...")
            else:
                print(f"[WARNING] No se encontraron puertos válidos para las IPs sin puerto")
        
        # Validar todos los proxies (con puerto)
        if not proxies_with_port:
            print(f"[ERROR] No hay proxies con formato IP:PUERTO para validar")
            return False
        
        print(f"\n[INFO] Validando conectividad de {len(proxies_with_port)} proxies...")
        validated_proxies = []
        failed_proxies = []
        
        for i, proxy_ip in enumerate(proxies_with_port, 1):
            print(f"[{i}/{len(proxies_with_port)}] Validando conectividad: {proxy_ip}")
            
            # Validar conectividad del proxy
            is_valid, response_time, error = validate_proxy(proxy_ip)
            
            if is_valid:
                validated_proxies.append({
                    'ip': proxy_ip,
                    'response_time': response_time,
                    'last_used': None,
                    'success_count': 0,
                    'fail_count': 0
                })
                print(f"   ✅ Conectividad OK ({response_time:.2f}s)")
            else:
                failed_proxies.append((proxy_ip, error))
                print(f"   ❌ {error}")
            
            # Pequeña pausa entre validaciones
            time.sleep(0.3)
        
        # Mostrar resumen final
        print(f"\n[RESUMEN FINAL]")
        print(f"✓ Proxies conectados: {len(validated_proxies)}")
        print(f"✗ Proxies fallidos: {len(failed_proxies)}")
        
        if failed_proxies and len(failed_proxies) <= 10:
            print(f"\nProxies fallidos:")
            for proxy, reason in failed_proxies:
                print(f"  • {proxy}: {reason}")
        elif len(failed_proxies) > 10:
            print(f"\nPrimeros 5 proxies fallidos:")
            for proxy, reason in failed_proxies[:5]:
                print(f"  • {proxy}: {reason}")
            print(f"  ... y {len(failed_proxies) - 5} más")
        
        if len(validated_proxies) == 0:
            print(f"[ERROR] No se encontraron proxies funcionales")
            return False
        
        # Ordenar por tiempo de respuesta (más rápidos primero)
        validated_proxies.sort(key=lambda x: x['response_time'])
        print(f"[INFO] Proxies ordenados por velocidad (mejor: {validated_proxies[0]['response_time']:.2f}s)")
        
        return True
        
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo {PROXIES_FILE}")
        return False
    except Exception as e:
        print(f"[ERROR] Error al procesar proxies: {e}")
        print(f"[INFO] Intentando crear archivo proxies.txt con formato correcto...")
        
        # Crear archivo de ejemplo con codificación UTF-8
        try:
            with open(PROXIES_FILE, "w", encoding="utf-8") as f:
                f.write("# Archivo de proxies - Codificación UTF-8\n")
                f.write("# Formato soportado:\n")
                f.write("#   IP:PUERTO  (ej: 192.168.1.100:8080) - Listo para usar\n")
                f.write("#   IP         (ej: 192.168.1.100) - Auto-detectará puerto\n")
                f.write("# Elimina estos comentarios y agrega tus proxies reales\n")
                f.write("\n")
                f.write("# Ejemplos:\n")
                f.write("# 123.456.789.100:8080\n")
                f.write("# 98.765.432.100:3128\n")
                f.write("# 111.222.333.444     # <- Auto-detectará puerto\n")
            print(f"[INFO] Archivo {PROXIES_FILE} recreado con formato mejorado")
        except Exception as create_error:
            print(f"[ERROR] No se pudo recrear el archivo: {create_error}")
        
        return False

def get_next_proxy():
    """Obtiene el siguiente proxy válido de la lista"""
    global current_proxy_index
    if not validated_proxies:
        return None
    
    proxy_data = validated_proxies[current_proxy_index]
    current_proxy_index = (current_proxy_index + 1) % len(validated_proxies)
    
    # Actualizar estadísticas de uso
    proxy_data['last_used'] = time.time()
    
    return proxy_data['ip']

def mark_proxy_failed(proxy_ip):
    """Marca un proxy como fallido y lo mueve al final de la lista"""
    global validated_proxies
    
    for i, proxy_data in enumerate(validated_proxies):
        if proxy_data['ip'] == proxy_ip:
            proxy_data['fail_count'] += 1
            print(f"   [WARNING] Proxy {proxy_ip} falló ({proxy_data['fail_count']} veces)")
            
            # Si falla demasiadas veces, moverlo al final
            if proxy_data['fail_count'] >= 3:
                print(f"   [INFO] Moviendo proxy problemático al final de la lista")
                failed_proxy = validated_proxies.pop(i)
                validated_proxies.append(failed_proxy)
            break

def mark_proxy_success(proxy_ip):
    """Marca un proxy como exitoso"""
    for proxy_data in validated_proxies:
        if proxy_data['ip'] == proxy_ip:
            proxy_data['success_count'] += 1
            # Reset fail count en caso de éxito
            if proxy_data['fail_count'] > 0:
                proxy_data['fail_count'] = max(0, proxy_data['fail_count'] - 1)
            break

def setup_tor_session():
    """Configura la sesión para usar TOR"""
    session = requests.Session()
    session.proxies = {
        'http': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}',
        'https': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}'
    }
    return session

def setup_proxy_session(proxy_ip):
    """Configura la sesión para usar un proxy HTTP/HTTPS"""
    session = requests.Session()
    session.proxies = {
        'http': f'http://{proxy_ip}:80',
        'https': f'http://{proxy_ip}:80'
    }
    return session

def switch_to_proxy():
    """Cambia a usar proxies HTTP/HTTPS"""
    global using_proxy, session
    proxy_ip = get_next_proxy()
    if proxy_ip:
        print(f"[INFO] Cambiando a proxy: {proxy_ip}")
        session = setup_proxy_session(proxy_ip)
        using_proxy = True
        return True
    else:
        print("[ERROR] No hay proxies válidos disponibles")
        return False

def switch_proxy():
    """Cambia al siguiente proxy en la lista"""
    global session
    
    # Marcar el proxy actual como problemático si existe
    if using_proxy and hasattr(session, 'proxies'):
        current_proxy = None
        for proxy_url in session.proxies.values():
            if 'http://' in proxy_url:
                current_proxy = proxy_url.replace('http://', '').replace(':80', '')
                break
        if current_proxy:
            mark_proxy_failed(current_proxy)
    
    proxy_ip = get_next_proxy()
    if proxy_ip:
        print(f"[INFO] Cambiando al proxy: {proxy_ip}")
        session = setup_proxy_session(proxy_ip)
        return True
    else:
        print("[ERROR] No hay más proxies válidos disponibles")
        return False

# Crear torrc temporal
TORRC_FILE = os.path.join(os.getcwd(), "torrc_temp.txt")
with open(TORRC_FILE, "w") as f:
    f.write(f"SocksPort {TOR_SOCKS_PORT}\n")
    f.write(f"ControlPort {TOR_CONTROL_PORT}\n")
    f.write("CookieAuthentication 0\n")

def start_tor():
    print("[INFO] Iniciando TOR...")
    tor_process = subprocess.Popen([TOR_EXE, "-f", TORRC_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(10)
    print("[INFO] TOR activo en puertos 9050/9051")
    return tor_process

def renew_tor_ip():
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate(password=CONTROL_PASSWORD)
            controller.signal(Signal.NEWNYM)
        print("[INFO] IP renovada con TOR")
    except Exception as e:
        print(f"[ERROR] No se pudo renovar la IP: {e}")

def save_progress(processed_count, total_count, results):
    """Guarda el progreso actual"""
    progress_data = {
        'processed': processed_count,
        'total': total_count,
        'timestamp': datetime.now().isoformat(),
        'results_count': len(results)
    }
    
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, indent=2)

def load_progress():
    """Carga el progreso anterior si existe"""
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def append_result(link):
    """Añade un resultado inmediatamente al archivo de salida"""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def extract_links_from_scholar(url, browser_sim, session_mgr):
    global using_proxy, tor_blocked, session
    
    for attempt in range(MAX_RETRIES):
        try:
            connection_type = "PROXY" if using_proxy else "TOR"
            print(f"   [{connection_type}] Intento {attempt + 1}/{MAX_RETRIES}")
            
            # Simular comportamiento humano antes de la request
            browser_sim.simulate_human_behavior(session, url)
            
            # Obtener headers coherentes
            headers = browser_sim.get_coherent_headers(url, referer="https://scholar.google.es/")
            
            # Configurar cookies realistas
            domain = urlparse(url).netloc
            cookies = session_mgr.get_realistic_cookies(domain)
            
            # Actualizar cookies en la sesión
            for name, value in cookies.items():
                session.cookies.set(name, value, domain=domain)
            
            # Realizar request
            response = session.get(url, headers=headers, timeout=25)
            
            # Actualizar cookies de sesión
            session_mgr.update_session_cookies(session, response)
            
            # Marcar proxy como exitoso si se usó
            if using_proxy and hasattr(session, 'proxies'):
                current_proxy = None
                for proxy_url in session.proxies.values():
                    if 'http://' in proxy_url:
                        current_proxy = proxy_url.replace('http://', '').replace(':80', '')
                        break
                if current_proxy:
                    mark_proxy_success(current_proxy)
            
            if response.status_code == 429:
                print(f"[BLOQUEO] 429 detectado.")
                handle_block(browser_sim)
                continue

            if "captcha" in response.text.lower() or "unusual traffic" in response.text.lower():
                print("[BLOQUEO] Captcha/bloqueo detectado.")
                handle_block(browser_sim)
                continue

            if response.status_code != 200:
                print(f"[ERROR] {url} - Código: {response.status_code}")
                time.sleep(random.uniform(3, 8))
                continue

            # Parsear respuesta
            soup = BeautifulSoup(response.text, "html.parser")
            title_wrapper = soup.find("div", id="gsc_oci_title_wrapper")

            if title_wrapper:
                # Buscar enlace PDF directo
                for a_tag in title_wrapper.find_all("a", href=True):
                    href = a_tag["href"]
                    text = a_tag.get_text(strip=True)
                    if "[PDF]" in text or href.lower().endswith(".pdf"):
                        return href
                    elif "Full View" in text or "view" in href:
                        editorial_link = href

                return editorial_link if 'editorial_link' in locals() else None

            return None

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Excepción en intento {attempt+1}/{MAX_RETRIES}: {e}")
            if attempt < MAX_RETRIES - 1:
                # Rotar perfil en caso de error
                browser_sim.rotate_profile()
                time.sleep(random.uniform(5, 10))
            continue

    print("[ERROR] Todos los intentos fallaron")
    return None

def handle_block(browser_sim):
    """Maneja los bloqueos cambiando de TOR a proxies o entre proxies"""
    global using_proxy, tor_blocked
    
    # Rotar perfil de navegador en caso de bloqueo
    browser_sim.rotate_profile()
    print("   [FINGERPRINT] Perfil rotado debido a bloqueo")
    
    if not using_proxy and not tor_blocked:
        print("[INFO] Primer bloqueo detectado. Cambiando de TOR a sistema de proxies...")
        tor_blocked = True
        if switch_to_proxy():
            time.sleep(random.uniform(8, 15))
        else:
            print("[ERROR] No se pudo activar sistema de proxies. Intentando renovar TOR...")
            renew_tor_ip()
            time.sleep(15)
    elif using_proxy:
        if not switch_proxy():
            print("[ERROR] No hay más proxies. Volviendo a TOR...")
            using_proxy = False
            tor_blocked = False
            global session
            session = setup_tor_session()
            renew_tor_ip()
        time.sleep(random.uniform(8, 15))
    else:
        renew_tor_ip()
        time.sleep(15)

# Inicializar sesión con TOR
session = setup_tor_session()

def main():
    global session
    
    # Cargar y validar proxies
    if not load_and_validate_proxies():
        print("[WARNING] Funcionando solo con TOR (sin proxies de respaldo)")
    
    # Inicializar simuladores
    browser_sim = AdvancedBrowserSimulator()
    session_mgr = SessionManager()
    
    print(f"[INFO] Perfil inicial: {browser_sim.current_profile['browser_type']} - {browser_sim.current_profile['screen_resolution']}")
    
    tor_process = start_tor()
    
    # Cargar URLs
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = []
        for line in f:
            line = line.strip()
            if ": http" in line:
                parts = line.split(": ", 1)
                if len(parts) == 2 and parts[1].startswith("http"):
                    urls.append(parts[1])

    print(f"[INFO] Total: {len(urls)} URLs a procesar")
    
    # Verificar progreso anterior
    progress = load_progress()
    start_index = 0
    result_links = []
    
    if progress:
        start_index = progress['processed']
        print(f"[INFO] Reanudando desde URL {start_index + 1}")
        
        # Cargar resultados existentes
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                result_links = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            pass
    else:
        # Crear archivo de salida vacío
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("")  # Archivo vacío para empezar

    for idx in range(start_index, len(urls)):
        url = urls[idx]
        connection_type = "PROXY" if using_proxy else "TOR"
        print(f"[{idx+1}/{len(urls)}] [{connection_type}] {url}")
        
        link = extract_links_from_scholar(url, browser_sim, session_mgr)
        if link:
            result_links.append(link)
            append_result(link)  # Guardar inmediatamente
            print(f"   -> {link}")
        else:
            print("   -> No se encontró enlace")

        # Guardar progreso
        save_progress(idx + 1, len(urls), result_links)

        # Rotación periódica solo si estamos usando TOR y no está bloqueado
        if (idx + 1) % ROTATE_EVERY == 0 and not using_proxy and not tor_blocked:
            print("[INFO] Rotación periódica de IP con TOR")
            renew_tor_ip()
            time.sleep(random.uniform(8, 12))

        # Rotar perfil ocasionalmente
        if (idx + 1) % 25 == 0:
            browser_sim.rotate_profile()
            print(f"[FINGERPRINT] Nuevo perfil: {browser_sim.current_profile['browser_type']} - {browser_sim.current_profile['screen_resolution']}")

        # Pausa entre requests con comportamiento más humano
        base_delay = random.uniform(1, 5)
        
        # Pausas ocasionales más largas
        if random.random() < 0.1:  # 10% de probabilidad
            base_delay = random.uniform(5, 12)
            print(f"   [HUMAN] Pausa larga: {base_delay:.1f}s")
        
        time.sleep(base_delay)

    print(f"[INFO] Proceso completado. {len(result_links)} enlaces guardados en {OUTPUT_FILE}")
    
    # Limpiar archivos temporales
    tor_process.terminate()
    
    try:
        os.remove(TORRC_FILE)
        os.remove(PROGRESS_FILE)
        print("[INFO] Archivos temporales eliminados")
    except:
        pass

if __name__ == "__main__":
    main()