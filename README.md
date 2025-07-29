# 🎓 ScholarDown Advanced

**Sistema avanzado de extracción masiva de papers académicos desde Google Scholar con técnicas anti-detección de última generación.**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

---

## 📋 Descripción

ScholarDown Advanced es una herramienta de investigación académica que permite la extracción automatizada y masiva de papers desde perfiles de Google Scholar. El sistema implementa técnicas avanzadas de anti-detección, auto-configuración de proxies y simulación de comportamiento humano para evitar bloqueos y garantizar extracciones exitosas a gran escala.

### 🎯 Características Principales

- **🤖 Anti-Detección Avanzada**: Simulación de comportamiento humano, rotación de fingerprints, headers inteligentes
- **🔧 Auto-Configuración**: Detección automática de puertos para proxies, validación de conectividad
- **🛡️ Elusión de Bloqueos**: Sistema inteligente de rotación TOR/Proxies con recuperación automática
- **💾 Recuperación de Sesión**: Escritura incremental con capacidad de reanudación tras interrupciones
- **📊 Monitoreo Completo**: Estadísticas detalladas, progreso en tiempo real, logs informativos
- **🔄 Procesamiento Paralelo**: Validación y detección multi-thread para máxima eficiencia

---

## 🚀 Instalación

### Requisitos del Sistema

- **Python 3.7+**
- **TOR Browser** (recomendado) - [Descargar](https://www.torproject.org/)
- **Proxies HTTP** (opcional pero recomendado)

### Dependencias Python

```bash
pip install requests beautifulsoup4 stem chardet
```

### Configuración TOR (Opcional)

1. Instalar TOR Browser en: `C:\Tor Browser\` (Windows)
2. El sistema detectará automáticamente la instalación

---

## 📁 Estructura del Proyecto

```
scholardown/
├── scholardown.py                   # 🎮 Script principal orquestador
├── scholardown_part1.py             # 📡 Extracción de enlaces (avanzado)
├── scholardown_part2.py             # 🔍 Búsqueda de descargas (avanzado)  
├── scholardown_part3.py             # 📥 Descarga de PDFs
├── proxy_validator.py               # 🔧 Validador de proxies con auto-detección
├── fix_proxies_encoding.py          # 🛠️ Corrector de codificación
├── demo_autodetect.py               # 🎬 Demo de funcionalidades
├── proxies.txt                      # 📋 Configuración de proxies
└── README.md                        # 📖 Este archivo
```

---

## 🎮 Uso Rápido

### Método 1: Ejecución Completa (Recomendado)

```bash
python scholardown.py
```

### Método 2: Validación Previa de Proxies

```bash
python proxy_validator.py          # Validar y auto-detectar proxies
python scholardown.py              # Ejecutar proceso completo
```

### Método 3: Ejecución Manual por Pasos

```bash
python scholardown_part1_advanced.py    # Extraer enlaces del perfil
python scholardown_part2_advanced.py    # Buscar enlaces de descarga  
python scholardown_part3.py             # Descargar PDFs
```

---

## ⚙️ Configuración de Proxies

### 🔧 Auto-Detección de Puertos (Nueva Característica)

El sistema puede trabajar con dos formatos de proxy:

```bash
# Formato 1: Proxy completo (tradicional)
192.168.1.100:8080
203.142.69.67:3128

# Formato 2: Solo IP (auto-detección automática) 
192.168.1.100
203.142.69.67
```

### 📝 Configuración del Archivo proxies.txt

```bash
# Ejemplo de archivo proxies.txt con formato mixto
# Proxies completos
192.168.1.100:8080
10.0.0.50:3128

# IPs sin puerto (se auto-detectará)
203.142.69.67
89.163.221.14
193.108.116.242
```

### 🎯 Puertos Detectados Automáticamente

El sistema prueba automáticamente estos puertos prioritarios:
- **HTTP Estándar**: 80, 8080, 8000, 8001, 8008
- **Squid Proxies**: 3128, 3129, 3127
- **Proxies Alternativos**: 8888, 8081, 8123, 8118
- **Corporativos**: 9000, 9090, 1080

---

## 🛡️ Técnicas Anti-Detección Implementadas

### Nivel 1: Headers y Sesiones
- ✅ Rotación inteligente de User-Agents
- ✅ Headers completos y coherentes (Accept, DNT, Referer, Sec-CH-UA)
- ✅ Orden aleatorio de headers por navegador
- ✅ Gestión realista de cookies de sesión

### Nivel 2: Fingerprinting Avanzado  
- ✅ Canvas fingerprinting con variaciones realistas
- ✅ WebGL fingerprinting con simulación de GPUs
- ✅ Diversidad de resoluciones de pantalla
- ✅ Coherencia geográfica (timezone/idioma)

### Nivel 3: Comportamiento Humano
- ✅ Patrones de timing naturales y variables
- ✅ Simulación de movimientos de ratón
- ✅ Patrones de navegación con errores humanos
- ✅ Pausas de lectura realistas

### Nivel 4: Gestión de Red
- ✅ Rotación automática TOR ↔ Proxies
- ✅ Validación en tiempo real de conectividad
- ✅ Recuperación inteligente ante bloqueos
- ✅ Distribución de carga entre conexiones

---

## 📊 Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `papers.txt` | Enlaces de papers extraídos del perfil |
| `papers2.txt` | Enlaces de descarga encontrados |
| `pdf/` | Carpeta con archivos PDF descargados |
| `proxy_validation_results.json` | Resultados detallados de validación |
| `proxies_valid.txt` | Lista filtrada de proxies funcionales |
| `proxies_original_backup_*.txt` | Backup automático de configuración |
| `progress.json` | Estado de progreso para reanudación |

---

## 🔧 Herramientas Auxiliares

### Validador de Proxies

```bash
python proxy_validator.py
```

**Características:**
- Auto-detección paralela de puertos
- Validación de conectividad en tiempo real
- Estadísticas detalladas de rendimiento
- Filtrado automático de proxies funcionales

### Corrector de Codificación

```bash
python fix_proxies_encoding.py
```

**Soluciona:**
- Problemas de codificación UTF-8/Latin-1
- Formatos de archivo inconsistentes
- Detección automática de caracteres especiales

### Demo Interactivo

```bash
python demo_autodetect.py
```

**Muestra:**
- Proceso de auto-detección paso a paso
- Comparación antes/después
- Ejemplos de configuración

---

## 📈 Casos de Uso

### Investigación Académica
- Extracción masiva de bibliografías
- Análisis de producción científica
- Construcción de bases de datos académicas
- Estudios bibliométricos

### Gestión de Información
- Per
### Gestión de Información
- Recopilación automatizada de literatura
- Monitoreo de publicaciones por autor
- Backup de colecciones académicas
- Análisis de tendencias de investigación

---

## ⚠️ Consideraciones Éticas y Legales

### 📋 Buenas Prácticas
- **Respetar robots.txt** de los sitios web
- **No sobrecargar servidores** con requests excesivos
- **Usar para investigación legítima** y educativa
- **Cumplir términos de servicio** de Google Scholar
- **Considerar APIs oficiales** cuando estén disponibles

### 🚦 Límites Recomendados
- Máximo 1000 papers por sesión
- Intervalos mínimos de 2-5 segundos entre requests
- Uso responsable de recursos de red
- Respeto por la infraestructura académica

---

## 🛠️ Solución de Problemas

### Problemas Comunes

#### Error: "TOR no encontrado"
```bash
# Verificar instalación de TOR Browser
# Ruta esperada: C:\Tor Browser\Browser\TorBrowser\Tor\tor.exe
```

#### Error: "No hay proxies válidos disponibles"
```bash
python proxy_validator.py           # Validar proxies
python fix_proxies_encoding.py     # Corregir codificación
```

#### Progreso Interrumpido
El sistema pregunta automáticamente si continuar desde donde se quedó.

#### Bloqueos Persistentes
1. Validar calidad de proxies: `python proxy_validator.py`
2. Aumentar delays entre requests
3. Verificar funcionamiento de TOR
4. Usar proxies premium de mayor calidad

### Optimización de Rendimiento

#### Para Mayor Éxito
- Usar proxies premium verificados
- Combinar TOR + proxies de calidad
- Ejecutar en horarios de menor carga
- Procesar en lotes pequeños (200-500 papers)

#### Para Mayor Velocidad  
- Validar proxies previamente
- Usar solo proxies más rápidos (<3s respuesta)
- Optimizar configuración de threads
- Ejecutar desde servidor con buena conectividad

---

## 🤝 Contribución

### Reportar Problemas
- Usar [GitHub Issues](../../issues) para reportar bugs
- Incluir logs detallados y configuración usada
- Especificar sistema operativo y versión Python

### Mejoras Sugeridas
- Fork del repositorio
- Crear rama para nueva funcionalidad
- Enviar Pull Request con descripción detallada
- Incluir tests y documentación

---

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 👨‍🎓 Autor y Colaboración

**Desarrollado por:**  
**Prof. Manuel Blázquez Ochando**  
📧 manublaz@ucm.es  
🏛️ Dpto. Biblioteconomía y Documentación  
🎓 Facultad de Ciencias de la Documentación  
🏫 Universidad Complutense de Madrid  
🔗 [ORCID: 0000-0002-4108-7531](https://orcid.org/0000-0002-4108-7531)

**Desarrollado con la colaboración y asistencia de:**  
**Claude (Anthropic)**  
🤖 Asistente de IA especializado en desarrollo de software  
💡 Contribuciones en arquitectura, anti-detección y optimización  

---

## 🙏 Agradecimientos

- **Comunidad académica** por el feedback y casos de uso
- **Desarrolladores de bibliotecas** utilizadas (requests, BeautifulSoup, stem)
- **Proyecto TOR** por proporcionar herramientas de privacidad
- **Google Scholar** por facilitar el acceso a literatura académica
- **Anthropic** por el desarrollo de herramientas de IA colaborativas

---

## 📞 Soporte

### Contacto Académico
- **Email**: manublaz@ucm.es
- **ORCID**: [0000-0002-4108-7531](https://orcid.org/0000-0002-4108-7531)
- **Institución**: Universidad Complutense de Madrid

### Recursos Técnicos
- **Documentación**: Ver archivos incluidos en el proyecto
- **Ejemplos**: Ejecutar `python demo_autodetect.py`
- **Issues**: [GitHub Issues](../../issues)

### Citas y Referencias
Si utilizas ScholarDown Advanced en tu investigación, por favor cita:

```
Blázquez Ochando, M. (2025). ScholarDown Advanced: Sistema de extracción 
masiva de literatura académica con técnicas anti-detección. 
GitHub. https://github.com/[usuario]/scholardown-advanced
```

---
