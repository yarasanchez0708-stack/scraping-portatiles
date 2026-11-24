"""App web: explorador de portátiles (datos extraídos por scraping en EA1)."""
import streamlit as st
from src.data_utils import cargar_datos, filtrar_por_precio, buscar_por_texto

RUTA_CSV = "data/portatiles_consolidado.csv"

st.set_page_config(page_title="Portátiles - EA3", page_icon="💻", layout="wide")
st.title("💻 Explorador de portátiles")
st.caption("Datos extraídos con BeautifulSoup, Selenium y Scrapy (EA1) · "
           "Pipeline CI/CD con GitHub Actions (EA2 y EA3)")


@st.cache_data
def obtener_datos():
    return cargar_datos(RUTA_CSV)


df = obtener_datos()

# Barra lateral con filtros
st.sidebar.header("Filtros")
pmin, pmax = float(df["precio"].min()), float(df["precio"].max())
rango = st.sidebar.slider("Rango de precio (USD)", pmin, pmax, (pmin, pmax))
texto = st.sidebar.text_input("Buscar en el título (ej. Lenovo, Asus)")

filtrado = buscar_por_texto(filtrar_por_precio(df, *rango), texto)

# Métricas
c1, c2, c3 = st.columns(3)
c1.metric("Productos", len(filtrado))
c2.metric("Precio promedio", f"${filtrado['precio'].mean():,.2f}" if len(filtrado) else "—")
c3.metric("Precio mínimo", f"${filtrado['precio'].min():,.2f}" if len(filtrado) else "—")

# Gráfico y tabla
st.subheader("Distribución de precios")
if len(filtrado):
    st.bar_chart(filtrado["precio"].round(-2).value_counts().sort_index())
else:
    st.info("No hay productos con esos filtros.")

st.subheader("Datos")
st.dataframe(filtrado, use_container_width=True)
