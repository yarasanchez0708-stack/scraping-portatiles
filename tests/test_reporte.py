"""Pruebas del generador de reporte (con datos de ejemplo, sin internet)."""
import pandas as pd

from generar_reporte import construir_reporte, limpiar


def datos_ejemplo():
    return pd.DataFrame(
        {
            "titulo": ["A", "B", "C", "A"],
            "precio_usd": [400.0, 800.0, 1200.0, 400.0],
            "ram_gb": [4, 8, 500, 4],
            "pulgadas": [15.6, 14.0, 13.3, 15.6],
            "rating": [3, 4, 5, 3],
            "opiniones": [5, 10, 15, 5],
            "url": ["u1", "u2", "u3", "u1"],
        }
    )


def test_limpiar_quita_duplicados_y_corrige_ram():
    datos = limpiar(datos_ejemplo())
    assert len(datos) == 3
    assert datos["ram_gb"].isna().sum() == 1  # el valor 500 no es RAM


def test_construir_reporte_genera_html_con_resultados():
    html = construir_reporte(limpiar(datos_ejemplo()))
    assert "<html" in html
    assert "Portátiles únicos analizados" in html
    assert "data:image/png;base64," in html
