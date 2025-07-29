#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Scholar Links Extractor ADVANCED
Extracción mejorada con anti-detección, auto-detección de proxies y fingerprinting inteligente
"""

import os
import time
import subprocess
import requests
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import random
import hashlib
import json
import concurrent.futures
import threading

# --- Configuración TOR ---
TOR_EXE = r"C:\Tor Browser\Browser\TorBrowser\Tor\tor.exe"
TOR_CONTROL_PORT = 9051
TOR_SOCKS_PORT = 9050
CONTROL_PASSWORD = ""  # sin contraseña
TORRC_FILE = os.path.join(os.getcwd(), "torrc_temp.txt")
PROXIES_FILE = "proxies.txt"

# Variables globales para manejo de proxies y sesiones
proxy_list = []
validated_proxies = []
failed_proxies = []
current_proxy_index = 0
using_proxy = False
tor_blocked = False
session_cookies = {}

# Lista de puertos prioritarios para auto-detección
PUERTOS_PRIORITARIOS = [
    80, 8080, 3128, 8000, 8888, 1080, 3129, 8081, 
    9000, 9090, 8123, 8118, 3127, 8001, 8008
]

class BrowserSimulator:
    """Simulador de navegador simplificado para Part1"""
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ]
        
        self.languages = ['en-US,en;q=0.9', 'en-GB,en;q=0.9', 'es-ES,es;q=0.8,en;q=0.7']
        self.current_profile = self.generate_profile()
    
    def generate_profile(self):
        """Genera un perfil de navegador coherente"""
        user_agent = random.choice(self.user_agents)
        browser_type = self.detect_browser_type(user_agent)
        
        return {
            'user_agent': user_agent,
            'browser_type': browser_type,
            'language': random.choice(self.languages),
            'do_not_track': random.choice(['1', '0']),
            'canvas_fingerprint': self.generate_canvas_fingerprint(),
        }
    
    def detect_browser_type(self, user_agent):
        if 'Chrome' in user_agent and 'Safari' in user_agent:
            return 'Chrome'
        elif 'Firefox' in user_agent:
            return 'Firefox'
        elif 'Safari' in user_agent and 'Chrome' not in user_agent:
            return 'Safari'
        return 'Chrome'
    
    def generate_canvas_fingerprint(self):
        """Genera un canvas fingerprint único"""
        base_data = f"{random.randint(1000000, 9999999)}{time.time()}"
        return hashlib.md5(base_data.encode()).hexdigest()[:16]
    
    def get_headers(self, referer=None):
        """Genera headers coherentes y realistas"""
        profile = self.current_profile
        
        headers = {
            'User-Agent': profile['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': profile['language'],
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': profile['do_not_track'],
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if profile['browser_type'] == 'Chrome':
            headers.update({
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none' if not referer else 'same-origin',
                'Sec-CH-UA': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                'Sec-CH-UA-Mobile': '?0',
                'Sec-CH-UA-Platform': '"Windows"',
            })
        
        if referer:
            headers['Referer'] = referer
        
        return headers
    
    def rotate_profile(self):
        """Rota el perfil del navegador"""
        if random.random() < 0.15:  # 15% probabilidad
            print("   [FINGERPRINT] Rotando perfil de navegador...")
            self.current_profile = self.generate_profile()
    
    def simulate_human_pause(self):
        """Simula pausas humanas variables"""
        # Pausa base entre requests
        base_delay = random.uniform(2, 6)
        
        # Ocasionalmente pausas más largas (simular lectura)
        if random.random() < 0.08:  # 8% probabilidad
            base_delay = random.uniform(5, 12)
            print(f"   [HUMAN] Pausa de lectura: {base_delay:.1f}s")
        
        time.sleep(base_delay)

class SessionManager:
    """Gestión simplificada de sesiones para Part1"""
    def __init__(self):
        self.cookies_store = {}
    
    def get_realistic_cookies(self, domain):
        """Genera cookies básicas para el dominio"""
        if domain not in self.cookies_store:
            self.cookies_store[domain] = {
                'GSP': f'ID={random.randint(100000, 999999)}:T={int(time.time())}',
                'CONSENT': f'YES+cb.{datetime.now().year}{random.randint(10,12)}.es+V{random.randint(8,14)}',
                'NID': ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=32)),
            }
        return self.cookies_store[domain]

# Funciones de validación de proxies (versión simplificada)
def validate_proxy(proxy_ip, timeout=8):
    """Validación rápida de proxy para Part1"""
    test_urls = ["http://httpbin.org/ip", "http://icanhazip.com/"]
    
    for test_url in test_urls:
        try:
            start_time = time.time()
            session = requests.Session()
            session.proxies = {
                'http': f'http://{proxy_ip}:80',
                'https': f'http://{proxy_ip}:80'
            }
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            response = session.get(test_url, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and len(response.text.strip()) > 0:
                if not any(keyword in response.text.lower() for keyword in 
                          ['login', 'password', 'authentication', 'unauthorized']):
                    return True, response_time, None
                    
        except requests.exceptions.ProxyError as e:
            if "authentication" in str(e).lower():
                return False, None, "Requiere autenticación"
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
            continue
        except Exception:
            continue
    
    return False, None, "No responde"

def auto_detect_proxy_ports(ip_list, max_workers=6):
    """Auto-detección rápida de puertos para Part1"""
    print(f"[INFO] Auto-detectando puertos para {len(ip_list)} IPs...")
    
    valid_proxies = []
    processed_count = 0
    lock = threading.Lock()
    
    def test_ip_ports(ip):
        nonlocal processed_count
        
        with lock:
            processed_count += 1
            current = processed_count
        
        print(f"[{current}/{len(ip_list)}] Probando {ip}...")
        
        # Probar solo los 8 puertos más comunes para Part1 (más rápido)
        priority_ports = [80, 8080, 3128, 8000, 8888, 1080, 3129, 8081]
        
        for puerto in priority_ports:
            proxy_address = f"{ip}:{puerto}"
            is_valid, response_time, error = validate_proxy(proxy_address)
            
            if is_valid:
                with lock:
                    valid_proxies.append((ip, puerto, response_time))
                print(f"   ✅ Puerto {puerto} válido ({response_time:.2f}s)")
                return True
        
        print(f"   ❌ Sin puerto válido")
        return False
    
    # Ejecutar con ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(test_ip_ports, ip_list))
    
    print(f"[INFO] Auto-detección completada: {len(valid_proxies)}/{len(ip_list)} válidos")
    return valid_proxies

def load_and_setup_proxies():
    """Carga y configura proxies con auto-detección"""
    global validated_proxies, failed_proxies
    
    try:
        # Intentar leer archivo con diferentes codificaciones
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        raw_lines = []
        
        for encoding in encodings:
            try:
                with open(PROXIES_FILE, "r", encoding=encoding) as f:
                    raw_lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                print(f"[INFO] Archivo leído con codificación {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if not raw_lines:
            print(f"[WARNING] No se pudo leer {PROXIES_FILE}")
            return False
        
        # Separar IPs de proxies completos
        ips_without_port = []
        proxies_with_port = []
        
        for line in raw_lines:
            if ':' in line:
                try:
                    ip, port = line.split(':')
                    port = int(port)
                    if 1 <= port <= 65535:
                        proxies_with_port.append(line)
                except ValueError:
                    pass
            else:
                if '.' in line:
                    ips_without_port.append(line)
        
        print(f"[INFO] Encontrados: {len(proxies_with_port)} proxies completos, {len(ips_without_port)} IPs sin puerto")
        
        # Auto-detectar puertos si es necesario
        all_valid_proxies = []
        
        if ips_without_port:
            print(f"[INFO] Auto-detectando puertos...")
            detected_proxies = auto_detect_proxy_ports(ips_without_port)
            
            # Crear backup y actualizar archivo si se detectaron proxies
            if detected_proxies:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = f"proxies_backup_part1_{timestamp}.txt"
                
                try:
                    import shutil
                    shutil.copy2(PROXIES_FILE, backup_file)
                    
                    # Actualizar archivo con proxies detectados
                    with open(PROXIES_FILE, 'w', encoding='utf-8') as f:
                        f.write(f"# Proxies actualizados por Part1 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"# Auto-detectados: {len(detected_proxies)} proxies\n")
                        f.write(f"# Backup original: {backup_file}\n\n")
                        
                        # Escribir proxies detectados
                        for ip, port, _ in detected_proxies:
                            f.write(f"{ip}:{port}\n")
                        
                        # Añadir proxies que ya tenían puerto
                        for proxy in proxies_with_port:
                            f.write(f"{proxy}\n")
                    
                    print(f"[INFO] Archivo actualizado con {len(detected_proxies)} proxies detectados")
                    
                except Exception as e:
                    print(f"[WARNING] Error actualizando archivo: {e}")
        
        # Validar proxies finales (validación rápida)
        final_proxies = proxies_with_port + [f"{ip}:{port}" for ip, port, _ in detected_proxies] if 'detected_proxies' in locals() else proxies_with_port
        
        if final_proxies:
            print(f"[INFO] Validando {len(final_proxies)} proxies...")
            
            validated_proxies = []
            for proxy in final_proxies[:20]:  # Limitar a 20 para Part1 (más rápido)
                is_valid, response_time, error = validate_proxy(proxy)
                if is_valid:
                    validated_proxies.append({
                        'ip': proxy,
                        'response_time': response_time,
                        'success_count': 0,
                        'fail_count': 0
                    })
            
            print(f"[INFO] {len(validated_proxies)} proxies válidos listos")
            return len(validated_proxies) > 0
        
        return False
        
    except FileNotFoundError:
        print(f"[WARNING] No se encontró {PROXIES_FILE}")
        return False
    except Exception as e:
        print(f"[WARNING] Error configurando proxies: {e}")
        return False

def get_next_proxy():
    """Obtiene el siguiente proxy válido"""
    global current_proxy_index
    if not validated_proxies:
        return None
    
    proxy_data = validated_proxies[current_proxy_index]
    current_proxy_index = (current_proxy_index + 1) % len(validated_proxies)
    return proxy_data['ip']

def setup_tor_session(browser_sim):
    """Configura sesión TOR con headers avanzados"""
    session = requests.Session()
    session.proxies = {
        'http': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}',
        'https': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}'
    }
    # Headers se configurarán dinámicamente en cada request
    return session

def setup_proxy_session(proxy_ip, browser_sim):
    """Configura sesión proxy con headers avanzados"""
    session = requests.Session()
    session.proxies = {
        'http': f'http://{proxy_ip}',
        'https': f'http://{proxy_ip}'
    }
    # Headers se configurarán dinámicamente en cada request
    return session

def switch_to_proxy(browser_sim):
    """Cambia a usar proxies HTTP/HTTPS"""
    global using_proxy, session
    proxy_ip = get_next_proxy()
    if proxy_ip:
        print(f"[INFO] Cambiando a proxy: {proxy_ip}")
        session = setup_proxy_session(proxy_ip, browser_sim)
        using_proxy = True
        return True
    else:
        print("[ERROR] No hay proxies válidos disponibles")
        return False

def switch_proxy(browser_sim):
    """Cambia al siguiente proxy"""
    global session
    proxy_ip = get_next_proxy()
    if proxy_ip:
        print(f"[INFO] Cambiando al proxy: {proxy_ip}")
        session = setup_proxy_session(proxy_ip, browser_sim)
        return True
    else:
        print("[ERROR] No hay más proxies válidos")
        return False

# Crear torrc temporal
with open(TORRC_FILE, "w") as f:
    f.write(f"SocksPort {TOR_SOCKS_PORT}\n")
    f.write(f"ControlPort {TOR_CONTROL_PORT}\n")
    f.write("CookieAuthentication 0\n")

def start_tor():
    print("[INFO] Iniciando servicio TOR...")
    tor_process = subprocess.Popen([TOR_EXE, "-f", TORRC_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(8)  # Menos tiempo de espera para Part1
    print("[INFO] TOR iniciado en puertos 9050/9051")
    return tor_process

def renew_tor_ip():
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate(password=CONTROL_PASSWORD)
            controller.signal(Signal.NEWNYM)
        print("[INFO] IP renovada con TOR")
        time.sleep(3)  # Menos tiempo de espera
    except Exception as e:
        print(f"[ERROR] No se pudo renovar la IP: {e}")

def is_blocked(html):
    """Detecta bloqueos de Google Scholar"""
    markers = [
        "id=\"gs_captcha_ccl\"",
        "Please show you're not a robot", 
        "detected unusual traffic",
        "captcha",
        "Unusual traffic"
    ]
    return any(marker.lower() in html.lower() for marker in markers)

def get_profile_links(profile_url, browser_sim, session_mgr):
    """Extracción mejorada con anti-detección"""
    global using_proxy, tor_blocked, session
    
    all_links = []
    start = 0
    max_attempts = 50
    attempts = 0
    max_retries_per_page = 8
    retry_count = 0

    parsed_url = urlparse(profile_url)
    query_params = parse_qs(parsed_url.query)

    if "user" not in query_params:
        print("[ERROR] La URL no contiene el parámetro 'user'.")
        return []

    user_id = query_params["user"][0]
    domain = parsed_url.netloc

    # Configurar cookies iniciales
    cookies = session_mgr.get_realistic_cookies(domain)
    for name, value in cookies.items():
        session.cookies.set(name, value, domain=domain)

    while attempts < max_attempts:
        params = {
            "user": user_id,
            "hl": "en", 
            "view_op": "list_works",
            "cstart": start,
            "pagesize": 100
        }
        url = f"https://{domain}/citations?" + urlencode(params)

        connection_type = "PROXY" if using_proxy else "TOR"
        print(f"[INFO] [{connection_type}] Página {attempts+1}: {start}-{start+99}")

        # Rotar perfil ocasionalmente
        browser_sim.rotate_profile()
        
        # Obtener headers coherentes
        headers = browser_sim.get_headers(referer=f"https://{domain}/")
        
        try:
            # Simular comportamiento humano antes del request
            if attempts > 0:  # No en la primera página
                browser_sim.simulate_human_pause()
            
            r = session.get(url, headers=headers, timeout=25)
            
        except Exception as e:
            print(f"[ERROR] Excepción durante petición: {e}")
            retry_count += 1
            
            if retry_count >= max_retries_per_page:
                print("[ERROR] Máximo número de reintentos alcanzado. Abortando.")
                break
                
            if not using_proxy and not tor_blocked:
                renew_tor_ip()
            elif using_proxy:
                if not switch_proxy(browser_sim):
                    print("[ERROR] No se pudo cambiar de proxy. Abortando.")
                    break
            elif not using_proxy and tor_blocked:
                if not switch_to_proxy(browser_sim):
                    print("[ERROR] No se pudo activar sistema de proxies. Abortando.")
                    break
            continue

        if r.status_code != 200:
            print(f"[ERROR] Código HTTP: {r.status_code}")
            retry_count += 1
            
            if retry_count >= max_retries_per_page:
                print("[ERROR] Máximo número de reintentos alcanzado. Abortando.")
                break
                
            if not using_proxy and not tor_blocked:
                renew_tor_ip()
            elif using_proxy:
                if not switch_proxy(browser_sim):
                    print("[ERROR] No se pudo cambiar de proxy. Abortando.")
                    break
            elif not using_proxy and tor_blocked:
                if not switch_to_proxy(browser_sim):
                    print("[ERROR] No se pudo activar sistema de proxies. Abortando.")
                    break
            continue

        if is_blocked(r.text):
            print("[BLOQUEO] Bloqueo detectado.")
            retry_count += 1
            
            if retry_count >= max_retries_per_page:
                print("[ERROR] Máximo número de reintentos alcanzado. Abortando.")
                break
            
            if not using_proxy:
                print("[INFO] Cambiando de TOR a sistema de proxies...")
                tor_blocked = True
                if not switch_to_proxy(browser_sim):
                    print("[ERROR] No se pudo activar sistema de proxies. Abortando.")
                    break
            else:
                if not switch_proxy(browser_sim):
                    print("[ERROR] No se pudo cambiar de proxy. Abortando.")
                    break
            
            time.sleep(random.uniform(5, 10))
            continue

        # Reset retry counter on successful request
        retry_count = 0

        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("tr.gsc_a_tr")

        if not rows:
            print("[INFO] No hay más resultados. Fin de la paginación.")
            break

        prev_count = len(all_links)
        for row in rows:
            link_tag = row.select_one("a.gsc_a_at")
            if link_tag and link_tag.get("href"):
                full_link = f"https://{domain}" + link_tag["href"]
                if full_link not in all_links:
                    all_links.append(full_link)

        print(f"[INFO] Acumulados: {len(all_links)} enlaces")

        if len(all_links) == prev_count:
            print("[INFO] Sin incremento en enlaces. Terminando paginación.")
            break

        start += 100
        attempts += 1

    return all_links

def save_links(links):
    """Guarda enlaces con información mejorada"""
    filename = os.path.join(os.getcwd(), "papers.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# GOOGLE SCHOLAR LINKS - ADVANCED EXTRACTION\n")
        f.write(f"# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Total: {len(links)} enlaces\n")
        f.write(f"# Sistema: Anti-detección con fingerprinting avanzado\n")
        f.write(f"# Proxies: Auto-detección y validación automática\n\n")
        for i, link in enumerate(links, 1):
            f.write(f"{i:03d}: {link}\n")
    print(f"[INFO] Archivo generado: {filename}")

# Inicializar componentes
browser_sim = BrowserSimulator()
session_mgr = SessionManager()
session = setup_tor_session(browser_sim)

if __name__ == "__main__":
    print("="*70)
    print("🎓 GOOGLE SCHOLAR LINKS EXTRACTOR - ADVANCED")
    print("="*70)
    print("✨ Características mejoradas:")
    print("  • Auto-detección de puertos para proxies")
    print("  • Headers coherentes y fingerprinting inteligente")
    print("  • Simulación de comportamiento humano")
    print("  • Rotación automática de profiles")
    print("  • Gestión avanzada de cookies")
    print("="*70)
    
    # Configurar proxies con auto-detección
    proxies_available = load_and_setup_proxies()
    if not proxies_available:
        print("[WARNING] Funcionando solo con TOR (sin proxies de respaldo)")
    
    profile_url = input("\nURL del perfil de Google Scholar: ").strip()
    if "scholar.google" not in profile_url:
        print("[ERROR] URL no válida.")
        exit(1)

    print(f"\n[INFO] Perfil de navegador: {browser_sim.current_profile['browser_type']}")
    print(f"[INFO] Canvas fingerprint: {browser_sim.current_profile['canvas_fingerprint']}")

    tor_process = start_tor()
    try:
        links = get_profile_links(profile_url, browser_sim, session_mgr)
        save_links(links)
        print(f"\n🎉 Proceso completado exitosamente!")
        print(f"📊 Total enlaces extraídos: {len(links)}")
        print(f"🔒 Nivel de protección: Avanzado")
    finally:
        print("\n[INFO] Cerrando TOR...")
        tor_process.terminate()
        
        # Limpiar archivos temporales
        try:
            os.remove(TORRC_FILE)
            print("[INFO] Archivos temporales eliminados")
        except:
            pass