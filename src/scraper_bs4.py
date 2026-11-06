"""Scraper de portátiles con BeautifulSoup.

Extrae título, descripción, precio, calificación, número de opiniones y enlace
de los portátiles del sitio de pruebas webscraper.io (Computers > Laptops).
Es la versión modular del código de la Evidencia de Aprendizaje 1.
"""
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SITIO = "https://webscraper.io"
URL_LISTADO = SITIO + "/test-sites/e-commerce/static/computers/laptops"
PAGINAS = 20  # el listado tiene 20 páginas de 6 portátiles (117 en total)
PAUSA = 1  # segundos entre solicitudes
HEADERS = {
    "User-Agent": "Mozilla/5.0 (proyecto academico)",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
}


def url_pagina(p):
    """Devuelve la URL de la página p del listado."""
    return URL_LISTADO if p == 1 else f"{URL_LISTADO}?page={p}"


def a_precio(texto):
    """'$1178.99' -> 1178.99"""
    t = re.sub(r"[^\d.]", "", texto or "")
    return float(t) if t else None


def a_entero(texto):
    """'12 reviews' -> 12"""
    m = re.search(r"\d+", texto or "")
    return int(m.group()) if m else None


def derivar_specs(desc):
    """'15.6", AMD E2-3800 1.3GHz, 4GB, 500GB, Windows 8.1' -> (15.6, 4)"""
    pulg = re.search(r'(\d+(?:\.\d+)?)"', desc or "")
    partes = [p.strip() for p in (desc or "").split(",")]
    ram = None
    for p in partes[1:]:
        m = re.fullmatch(r"(\d+)\s*GB", p)
        if m:
            ram = int(m.group(1))  # primer valor en GB después del procesador = RAM
            break
    return (float(pulg.group(1)) if pulg else None), ram


def obtener_html(url, headers=HEADERS):
    """Descarga el HTML de una URL y lanza un error si el sitio no responde 200."""
    respuesta = requests.get(url, headers=headers, timeout=20)
    respuesta.raise_for_status()
    return respuesta.text


def parsear_listado(html, herramienta="BeautifulSoup"):
    """Convierte el HTML de una página del listado en una lista de diccionarios."""
    soup = BeautifulSoup(html, "html.parser")
    filas = []
    for t in soup.select("div.thumbnail"):
        a = t.select_one("a.title")
        precio = t.select_one(".price")
        desc = t.select_one("p.description")
        rev = t.select_one(".review-count")
        est = t.select_one("p[data-rating]")
        descripcion = desc.get_text(strip=True) if desc else None
        pulgadas, ram = derivar_specs(descripcion)
        if est and est.has_attr("data-rating"):
            rating = int(est["data-rating"])
        else:
            rating = len(t.select("span.ws-icon-star")) or None
        filas.append(
            {
                "titulo": (a.get("title") or a.get_text(strip=True)) if a else None,
                "descripcion": descripcion,
                "precio_usd": a_precio(precio.get_text()) if precio else None,
                "rating": rating,
                "opiniones": a_entero(rev.get_text()) if rev else None,
                "pulgadas": pulgadas,
                "ram_gb": ram,
                "url": urljoin(SITIO, a["href"]) if a and a.has_attr("href") else None,
                "herramienta": herramienta,
            }
        )
    return filas


def scrapear_listado(paginas=PAGINAS, pausa=PAUSA):
    """Recorre las páginas del listado y devuelve todos los portátiles."""
    resultados = []
    for p in range(1, paginas + 1):
        html = obtener_html(url_pagina(p))
        resultados += parsear_listado(html)
        print(f"Página {p}: {len(resultados)} portátiles acumulados")
        time.sleep(pausa)
    return resultados


if __name__ == "__main__":
    import pandas as pd

    df = pd.DataFrame(scrapear_listado())
    df.to_csv("data/portatiles_bs4.csv", index=False, encoding="utf-8-sig")
    print(df.shape)
