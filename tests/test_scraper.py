"""Pruebas del scraper de portátiles.

Usan un HTML de ejemplo, así que no necesitan conexión a internet.
"""
from scraper_bs4 import (
    a_entero,
    a_precio,
    derivar_specs,
    parsear_listado,
    url_pagina,
    URL_LISTADO,
)

HTML_EJEMPLO = """
<div class="thumbnail">
  <h4 class="price">$416.99</h4>
  <a class="title" href="/test-sites/e-commerce/static/product/1" title="Asus VivoBook">Asus...</a>
  <p class="description">Asus VivoBook, 15.6", Core i3, 4GB, 500GB, Windows 8.1</p>
  <div class="ratings">
    <p class="review-count">7 reviews</p>
    <p data-rating="3"></p>
  </div>
</div>
<div class="thumbnail">
  <h4 class="price">$1178.99</h4>
  <a class="title" href="/test-sites/e-commerce/static/product/2" title="Dell Latitude">Dell...</a>
  <p class="description">Dell Latitude, 14", Core i5, 8GB, 256GB, Windows 10</p>
  <div class="ratings">
    <p class="review-count">12 reviews</p>
    <p data-rating="4"></p>
  </div>
</div>
"""


def test_a_precio_convierte_texto_a_numero():
    assert a_precio("$1178.99") == 1178.99


def test_a_precio_sin_texto_devuelve_none():
    assert a_precio("") is None
    assert a_precio(None) is None


def test_a_entero_extrae_el_numero():
    assert a_entero("12 reviews") == 12
    assert a_entero("sin opiniones") is None


def test_derivar_specs_extrae_pulgadas_y_ram():
    desc = '15.6", AMD E2-3800 1.3GHz, 4GB, 500GB, Windows 8.1'
    assert derivar_specs(desc) == (15.6, 4)


def test_url_pagina():
    assert url_pagina(1) == URL_LISTADO
    assert url_pagina(3) == URL_LISTADO + "?page=3"


def test_parsear_listado_devuelve_un_registro_por_portatil():
    filas = parsear_listado(HTML_EJEMPLO)
    assert len(filas) == 2


def test_parsear_listado_extrae_los_campos_correctos():
    primera = parsear_listado(HTML_EJEMPLO)[0]
    assert primera["titulo"] == "Asus VivoBook"
    assert primera["precio_usd"] == 416.99
    assert primera["rating"] == 3
    assert primera["opiniones"] == 7
    assert primera["pulgadas"] == 15.6
    assert primera["ram_gb"] == 4
    assert primera["url"].startswith("https://webscraper.io/")


def test_parsear_listado_sin_productos_devuelve_lista_vacia():
    assert parsear_listado("<html><body></body></html>") == []


def test_los_precios_son_numericos_y_los_titulos_no_estan_vacios():
    for fila in parsear_listado(HTML_EJEMPLO):
        assert isinstance(fila["precio_usd"], float)
        assert fila["titulo"]
