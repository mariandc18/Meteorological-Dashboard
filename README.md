# Weather Dashboard ⛅

Este repositorio contiene un pipeline completo de ingeniería de datos, desde la ingesta hasta la visualización, con el objetivo de analizar los datos meteorológicos de Cuba tanto en tiempo real como históricamente. Realiza pronósticos de clima para las próximas 24 horas y brinda información detallada de los eventos meteorológicos más relevantes que han afectado a la isla desde el año 2000 hasta la actualidad(ciclones, huracanes, tormentas tropicales, etc).

![Weather Dashboard](assets/app.png)

## Pre-requisitos 📋

Para instalar las dependencias necesarias ejecute:

```
pip install -r requirements.txt
```

## Estructura del proyecto 🗂️

| Carpeta/Archivo       | Descripción                                              |
|-----------------------|----------------------------------------------------------|
| `src/data_ingestion`  | Contiene los scripts de ingesta de datos históricos y diarios |
| `src/storage`         | Maneja el almacenamiento de datos en PostgreSQL             |
| `src/transformation`  | Procesa y transforma los datos antes de su almacenamiento en la base de datos |
| `src/serving`         | Contiene la RestAPI para predecir el clima               |
| `src/auth`            | Contiene la lógica de autenticación               |
| `pages/forecast`      | Layouts y callbacks de la página de pronósticos de la app |
| `pages/historical`    | Layouts y callbacks de la página de análisis históricos de la app |
| `pages_admin`         | Layouts y callbacks de la página del administrador, incluyendo estadísticas de la página |
| `pages/cyclones`      | Layouts y callbacks de los datos de ciclones           |
| `pages/auth`          | Página de autenticación |
| `tracking`            | Registra las interacciones de los usuarios con la página |
| `assets/`            | Imágenes y estilos de la app                             |
| `Procfile`           | Configuración de despliegue en Render                    |
| `run_script.yml`     | Automatización de la extracción de datos climáticos de la API a diario |
| `requirements.txt`   | Dependencias necesarias                                    |

## Despliegue 📦

Puede acceder a la aplicación mediante el siguiente enlace: <https://meteorological-dashboard-hsr7.onrender.com>

## Herramientas y API utilizadas 🛠️

* [OpenWeatherMap](https://openweathermap.org/) - API de datos climáticos históricos
* [WeatherMap](https://www.weatherapi.com/) - API de datos climáticos en tiempo real
* [PostgreSQL](https://www.postgresql.org/docs/) - Para almacenar los datos climáticos
* [FastAPI](https://fastapi.tiangolo.com/) - Para RestAPI
* [Render](https://render.com/) - Para despliegue de la app y el modelo de predicción.
* [Dash Plotly](https://dash.plotly.com/) - Para crear la interfaz de usuario
* [TimescaleDB](https://docs.timescale.com/) - Para optimización de almacenamiento en PostgreSQL
* [Azure](https://learn.microsoft.com/en-us/azure/?product=popular) - Para montar una VM
