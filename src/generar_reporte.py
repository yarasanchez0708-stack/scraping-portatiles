"""Genera el reporte HTML con los resultados del análisis de portátiles.

El pipeline de GitHub Actions ejecuta este script y publica el resultado
en GitHub Pages (despliegue continuo).
"""
import base64
import io
import os
from datetime import datetime, timezone

import matplotlib

matplotlib.use("Agg")  # sin ventana: necesario en el servidor de GitHub Actions
import matplotlib.pyplot as plt
import pandas as pd

from scraper_bs4 import scrapear_listado


def limpiar(df):
    """Elimina duplicados y corrige valores de RAM que en realidad son almacenamiento."""
    datos = df.drop_duplicates("url").copy()
    datos.loc[datos["ram_gb"] > 64, "ram_gb"] = None
    return datos


def grafico_base64(datos):
    """Crea dos gráficos (histograma de precios y precio promedio por RAM) en base64."""
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    datos["precio_usd"].plot.hist(bins=15, ax=ax[0], color="#2f6fb3")
    ax[0].set(title="Distribución de precios (USD)", xlabel="Precio (USD)", ylabel="Portátiles")
    promedio_ram = datos.groupby("ram_gb")["precio_usd"].mean()
    promedio_ram.plot.bar(ax=ax[1], color="#3a9a6b")
    ax[1].set(title="Precio promedio según RAM", xlabel="RAM (GB)", ylabel="Precio (USD)")
    plt.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=110)
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def construir_reporte(datos):
    """Devuelve el HTML del reporte a partir del DataFrame limpio."""
    precios = datos["precio_usd"]
    por_ram = (
        datos.groupby("ram_gb")["precio_usd"]
        .agg(["count", "mean", "min", "max"])
        .round(2)
        .reset_index()
        .rename(columns={"ram_gb": "RAM (GB)", "count": "Portátiles",
                         "mean": "Promedio", "min": "Mínimo", "max": "Máximo"})
    )
    caros = datos.nlargest(5, "precio_usd")[["titulo", "precio_usd", "ram_gb"]]
    corr = (
        datos[["precio_usd", "ram_gb", "pulgadas", "rating", "opiniones"]]
        .corr()["precio_usd"]
        .round(3)
        .drop("precio_usd")
        .reset_index()
        .rename(columns={"index": "Variable", "precio_usd": "Correlación con el precio"})
    )
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reporte de portátiles</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
  h1 {{ color: #1f4e79; }}
  table {{ border-collapse: collapse; margin: 1rem 0; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 12px; text-align: left; }}
  th {{ background: #eef3f8; }}
  img {{ max-width: 100%; }}
</style>
</head>
<body>
<h1>Reporte de portátiles (webscraper.io)</h1>
<p>Generado automáticamente por el pipeline de GitHub Actions el {fecha}.</p>
<h2>Resumen</h2>
<ul>
  <li>Portátiles únicos analizados: <b>{len(datos)}</b></li>
  <li>Precio promedio: <b>USD {precios.mean():.2f}</b></li>
  <li>Precio mínimo: <b>USD {precios.min():.2f}</b> · máximo: <b>USD {precios.max():.2f}</b></li>
</ul>
<img alt="Gráficos de precios" src="data:image/png;base64,{grafico_base64(datos)}">
<h2>Precio según memoria RAM</h2>
{por_ram.to_html(index=False)}
<h2>Los 5 portátiles más caros</h2>
{caros.to_html(index=False)}
<h2>Correlaciones con el precio</h2>
{corr.to_html(index=False)}
</body>
</html>
"""


if __name__ == "__main__":
    datos = limpiar(pd.DataFrame(scrapear_listado(pausa=0.5)))
    os.makedirs("site", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    datos.to_csv("data/portatiles_bs4.csv", index=False, encoding="utf-8-sig")
    with open("site/index.html", "w", encoding="utf-8") as f:
        f.write(construir_reporte(datos))
    print("Reporte generado en site/index.html")
