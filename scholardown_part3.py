import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Archivo con enlaces
INPUT_FILE = "papers2.txt"
# Carpeta de destino
OUTPUT_DIR = "pdf"

# Crear la carpeta de destino si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

def is_pdf(content_type: str) -> bool:
    """Verifica si el contenido es PDF según el header."""
    return "application/pdf" in content_type.lower()

def download_file(url: str, dest_folder: str):
    """Descarga un archivo desde una URL y lo guarda en la carpeta especificada."""
    try:
        # Obtener respuesta inicial
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        
        # Comprobar si es PDF por Content-Type
        if is_pdf(response.headers.get("Content-Type", "")):
            filename = url.split("/")[-1].split("?")[0]
            if not filename.endswith(".pdf"):
                filename += ".pdf"
            filepath = os.path.join(dest_folder, filename)
            
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ Descargado: {filename}")
            return True
        else:
            print(f"🔍 No es PDF directo, buscando en página: {url}")
            return False
    except Exception as e:
        print(f"❌ Error descargando {url}: {e}")
        return False

def find_pdf_in_page(url: str):
    """Busca enlaces a PDF en una página HTML."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        pdf_links = []
        
        # Buscar enlaces que terminen en .pdf o tengan 'download'
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if ".pdf" in href.lower() or "download" in href.lower():
                full_url = urljoin(url, href)
                pdf_links.append(full_url)
        
        return pdf_links
    except Exception as e:
        print(f"❌ Error analizando la página {url}: {e}")
        return []

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    for url in urls:
        if not download_file(url, OUTPUT_DIR):
            pdf_candidates = find_pdf_in_page(url)
            for pdf_url in pdf_candidates:
                if download_file(pdf_url, OUTPUT_DIR):
                    break  # Si se descarga un PDF, no seguimos buscando más en esa página

if __name__ == "__main__":
    main()
