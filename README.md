# Análisis de Permisos de Circulación 2023 — Municipalidad de Calbuco

Aplicación web desarrollada con **Streamlit** que consume la API REST pública del **Portal de Datos Abiertos del Gobierno de Chile** ([datos.gob.cl](https://datos.gob.cl)) para obtener, analizar y visualizar el registro de permisos de circulación 2023 publicado por la Municipalidad de Calbuco.

> **Asignatura:** FITO9017 — Programación en Python  
> **Evaluación:** Solemne II — Unidad 3, Semana 13  
> **Universidad:** San Sebastián — FIAD

---

## Ejecutar la aplicación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

La app se abre en `http://localhost:8501`.

---

## ¿Qué hace?

1. Consulta la API CKAN de `datos.gob.cl` para obtener el dataset de permisos de circulación.
2. Descarga y carga el CSV (más de 10.000 registros vehiculares).
3. Permite filtrar por tipo de combustible y tipo de vehículo.
4. Muestra métricas: vehículos, recaudación, valor promedio, antigüedad.
5. Genera visualizaciones: top marcas, distribución de combustible, antigüedad del parque.
6. Permite descargar los datos filtrados.

---

## Librerías utilizadas

| Librería | Uso |
|----------|-----|
| `requests` | Consulta HTTP GET a la API REST |
| `json` | Parseo de la respuesta JSON |
| `pandas` | Análisis y manipulación de datos |
| `matplotlib` | Generación de gráficos |
| `streamlit` | Interfaz web interactiva |

---

## Fuente de datos

- **Portal:** https://datos.gob.cl
- **Dataset:** Permiso de Circulación Año 2023 — Municipalidad de Calbuco
- **Endpoint:** `GET /api/3/action/package_show?id={DATASET_ID}`
