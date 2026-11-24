"""Funciones de carga y filtrado de los datos de portátiles (EA1/EA2)."""
import re
import pandas as pd

# Nombres posibles de columnas -> nombre estándar
COLUMN_ALIASES = {
    "titulo": ["titulo", "título", "title", "nombre", "name", "producto"],
    "precio": ["precio", "precio_usd", "price"],
    "descripcion": ["descripcion", "descripción", "description"],
    "reseñas": ["reseñas", "resenas", "reviews", "num_reviews"],
}


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Renombra las columnas a nombres estándar (titulo, precio, ...)."""
    renombres = {}
    for col in df.columns:
        clave = str(col).strip().lower()
        for estandar, alias in COLUMN_ALIASES.items():
            if clave in alias:
                renombres[col] = estandar
    return df.rename(columns=renombres)


def limpiar_precio(valor) -> float:
    """Convierte '$1,139.54' o 1139.54 en float. Devuelve NaN si no se puede."""
    if pd.isna(valor):
        return float("nan")
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = re.sub(r"[^\d.,]", "", str(valor)).replace(",", "")
    try:
        return float(texto)
    except ValueError:
        return float("nan")


def cargar_datos(ruta: str) -> pd.DataFrame:
    """Lee el CSV, normaliza columnas y limpia el precio."""
    df = normalizar_columnas(pd.read_csv(ruta, encoding="utf-8-sig"))
    if "precio" not in df.columns:
        raise ValueError("El CSV debe tener una columna de precio (precio, precio_usd o price).")
    # El CSV consolidado de la EA1 trae los mismos productos extraídos con
    # 3 herramientas: se deja una sola fila por producto (misma url).
    if "url" in df.columns:
        df = df.drop_duplicates(subset="url")
    df["precio"] = df["precio"].apply(limpiar_precio)
    return df.dropna(subset=["precio"]).reset_index(drop=True)


def filtrar_por_precio(df: pd.DataFrame, minimo: float, maximo: float) -> pd.DataFrame:
    """Devuelve los portátiles con precio entre minimo y maximo (inclusive)."""
    return df[(df["precio"] >= minimo) & (df["precio"] <= maximo)]


def buscar_por_texto(df: pd.DataFrame, texto: str) -> pd.DataFrame:
    """Filtra por texto en el título (sin distinguir mayúsculas)."""
    if not texto or "titulo" not in df.columns:
        return df
    return df[df["titulo"].astype(str).str.contains(texto, case=False, na=False)]
