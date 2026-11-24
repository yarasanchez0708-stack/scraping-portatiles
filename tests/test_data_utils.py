import math
import pandas as pd
import pytest
from src.data_utils import (
    normalizar_columnas, limpiar_precio, cargar_datos,
    filtrar_por_precio, buscar_por_texto,
)


@pytest.fixture
def df_ejemplo():
    return pd.DataFrame({
        "titulo": ["Lenovo ThinkPad", "Asus VivoBook", "Dell Inspiron"],
        "precio": [399.0, 745.5, 1139.54],
    })


def test_limpiar_precio_con_simbolo_y_coma():
    assert limpiar_precio("$1,139.54") == 1139.54


def test_limpiar_precio_numerico():
    assert limpiar_precio(399) == 399.0


def test_limpiar_precio_invalido_devuelve_nan():
    assert math.isnan(limpiar_precio("sin precio"))


def test_normalizar_columnas_ingles():
    df = pd.DataFrame({"Title": ["x"], "Price": [1]})
    assert {"titulo", "precio"} <= set(normalizar_columnas(df).columns)


def test_filtrar_por_precio(df_ejemplo):
    resultado = filtrar_por_precio(df_ejemplo, 400, 800)
    assert list(resultado["titulo"]) == ["Asus VivoBook"]


def test_buscar_por_texto_ignora_mayusculas(df_ejemplo):
    assert len(buscar_por_texto(df_ejemplo, "lenovo")) == 1


def test_buscar_texto_vacio_devuelve_todo(df_ejemplo):
    assert len(buscar_por_texto(df_ejemplo, "")) == 3


def test_cargar_datos_desde_csv(tmp_path):
    ruta = tmp_path / "datos.csv"
    pd.DataFrame({"title": ["A", "B"], "price": ["$10.5", "sin dato"]}).to_csv(ruta, index=False)
    df = cargar_datos(str(ruta))
    assert len(df) == 1 and df.loc[0, "precio"] == 10.5


def test_cargar_datos_sin_columna_precio(tmp_path):
    ruta = tmp_path / "malo.csv"
    pd.DataFrame({"titulo": ["A"]}).to_csv(ruta, index=False)
    with pytest.raises(ValueError):
        cargar_datos(str(ruta))


def test_cargar_datos_quita_duplicados_por_url(tmp_path):
    """El CSV consolidado repite productos (BeautifulSoup, Selenium, Scrapy)."""
    ruta = tmp_path / "consolidado.csv"
    pd.DataFrame({
        "titulo": ["A", "A", "B"],
        "precio_usd": [10.0, 10.0, 20.0],
        "url": ["u1", "u1", "u2"],
        "herramienta": ["BeautifulSoup", "Scrapy", "Scrapy"],
    }).to_csv(ruta, index=False, encoding="utf-8-sig")
    df = cargar_datos(str(ruta))
    assert len(df) == 2
