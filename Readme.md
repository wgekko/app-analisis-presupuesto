# Enterprise Financial Intelligence & Budget ERP

Sistema integral de gestión presupuestaria y análisis financiero avanzado desarrollado en Python. Diseñado bajo una arquitectura modular y desacoplada (N-Tier), combina la agilidad de los dashboards interactivos con modelos de Machine Learning y procesamiento de datos para transformar registros contables en inteligencia de negocios procesable.

---

## Arquitectura del Sistema (Diseño Modular N-Tier)

El proyecto está estructurado para garantizar escalabilidad, separación de responsabilidades y mantenibilidad a nivel empresarial, organizado en las siguientes capas lógicas:

### 1. Capa de Presentación (UI/UX)

Desarrollada íntegramente con Streamlit, la interfaz se divide en componentes modulares y vistas enrutadas:
***Enrutador Principal:** El flujo de la aplicación es orquestado desde la raíz por `app.py`.

***Vistas de Usuario (`pages/`):** Páginas modulares e independientes como `page_dashboard.py`, `page_movimientos.py`, `page_inteligencia.py`, `page_simulador.py`, `page_reportes.py` y `page_configuracion.py`.

***Componentes Reutilizables (`components/`):** Elementos visuales aislados para mantener el código DRY (Don't Repeat Yourself), incluyendo `charts.py` para visualizaciones, `forms.py` para la captura de datos y `kpi_cards.py` para métricas de alto impacto.

***Dashboarding Dual (`dashboard/`):** Separación conceptual de las vistas de control en perspectivas directivas (`executive.py`) y de análisis profundo (`analytical.py`).

### 2. Capa de Lógica de Negocio y Servicios (`services/` & `analytics/`)

Encapsula las reglas de negocio, aislando los controladores de la vista y la base de datos:

***Servicios Transaccionales (`services/`):** Incluye `auth_service.py` para la gestión de accesos, `mov_service.py` para el control contable, `export_service.py` para la generación de reportes y `backup_service.py` para la resiliencia operativa.

***Motores Analíticos (`analytics/`):** Módulos dedicados al cálculo puro como `financial_math.py` y el cálculo de indicadores en `metrics.py`.

### 3. Capa de Inteligencia Artificial (`ml_models/`)

El núcleo predictivo del ERP que transforma datos históricos en proyecciones futuras:

*`clustering.py`: Segmentación de perfiles de gasto y detección de comportamiento de consumo mediante aprendizaje no supervisado.

*`forecasting.py`: Proyección de tendencias financieras a mediano plazo mediante series temporales.

*`anomalies.py`: Detección estadística de atípicos (*outliers*) para identificar fraudes o desvíos críticos.

*`risk_scorer.py`: Algoritmo de calificación cuantitativa del riesgo de liquidez.

*`insights_gen.py`: Generador automatizado de diagnósticos financieros.

### 4. Capa de Datos y Persistencia (`models/` & `database/`)

Gestión robusta del almacenamiento relacional mediante SQLAlchemy sobre SQLite:
***Modelado ORM (`models/`):** Definición estricta de entidades heredadas de `base.py`, incluyendo estructuras para usuarios (`user.py`) y transacciones contables (`movimiento.py`).

***Conexión y Sesiones (`database/`):** Administración del ciclo de vida de la conexión en `db_session.py` y rutinas de creación de esquemas en `init_db.py`.

### 5. Configuración e Interoperabilidad

***Parámetros Globales (`config/`):** Centralización de variables de entorno en `settings.py` y adaptación multi-idioma mediante `i18n.py`.

***I/O de Datos (`imports/` & `exports/`):** Carpetas dedicadas a la ingesta masiva de registros históricos (ej. `bd-datos.xlsx`) y la salida de reportes gerenciales.

---

## ⚙️ Funcionalidades Principales

***Simulador Financiero Avanzado:** A través del módulo `page_simulador.py`, permite a la gerencia modelar escenarios de liquidez basados en el comportamiento validado por los modelos de Machine Learning.

***Centro de Alertas Proactivas:** Monitoreo constante de desviaciones presupuestarias, evaluando automáticamente variaciones sobre la media histórica y notificando cuentas por cobrar/pagar críticas.
***Seguridad Basada en Roles (RBAC):** La interacción entre `user.py` y `auth_service.py` garantiza autenticación cifrada por *bcrypt* y asigna privilegios específicos (Administrador, Operador, Solo Lectura).

***Resiliencia Automatizada:** El módulo `backup_service.py` genera copias de seguridad de forma proactiva hacia el directorio `backups/`, asegurando la disponibilidad de la información ante fallos.

***Análisis Dinámico Interactivo:** Manipulación tabular de alta velocidad y gráficos jerárquicos que permiten aislar costos por proyecto, categoría o rango temporal con precisión milimétrica.

si desea tener la misma configuración de esta app
debe generar una carpeta .streamlit 
archivo config.toml

----
[server]
enableStaticServing = false

[theme]
primaryColor = "#FF8C00"
backgroundColor = "#0D1B2A"
secondaryBackgroundColor = "#1B263B"
textColor = "#FFA500"
font = "sans serif"
---------


 APP DE PRESUPUESTO INMOBILIARIO/
│
├── app.py                  # Entry point. Inicializa sesión, ruteo principal y sidebar.
├── requirements.txt        # Dependencias fijadas con versiones exactas.
├── README.md               # Documentación completa de despliegue y uso.
├
│
├── config/                 # Configuración global.
│   ├── settings.py         # Carga de variables, constantes de UI (colores, temas).
│   └── i18n.py             # Internacionalización y formatos de moneda/fecha.
│
├── database/               # Conexión y gestión de DB.
│   ├── db_session.py       # Engine de SQLAlchemy y SessionMaker.
│   └── init_db.py          # Script para poblar la DB inicial (Admin user).
│
├── models/                 # Modelos ORM (SQLAlchemy).
│   ├── base.py             # Clase base declarativa.
│   ├── user.py             # Tabla Usuarios (Auth y roles).
│   └── movimiento.py       # Tabla principal: MOVIMIENTOS.
│
├── services/               # Lógica de negocio (CRUD y cálculos).
│   ├── auth_service.py     # Hashing de passwords y validación de usuarios.
│   ├── mov_service.py      # Operaciones CRUD para movimientos.
│   └── export_service.py   # Lógica para generar Excel, CSV y PDF.
│   └── backup_service.py   # Lógica para generar backup de los analisis .
│
├── dashboard/              # Lógica de armado de Dashboards.
│   ├── executive.py        # KPIs, Alertas y semáforos.
│   └── analytical.py       # Preparación de datos para Plotly/Sankey.
│
├── analytics/              # Análisis financiero puro.
│   ├── financial_math.py   # Cálculos de balances, ABC, Pareto.
│   └── metrics.py          # Variaciones interanuales y mensuales.
│
├── ml_models/              # Módulo de Inteligencia Artificial.
│   ├── forecasting.py      # Prophet / XGBoost para proyección.
│   ├── anomalies.py        # Isolation Forest para detección de atípicos.
│   ├── clustering.py       # KMeans para segmentación de proyectos.
│   ├── risk_scorer.py      # Motor de cálculo de índice de riesgo.
│   └── insights_gen.py     # Generador de recomendaciones en lenguaje natural.
│
├── components/             # UI Reutilizable.
│   ├── kpi_cards.py        # Tarjetas de métricas modernas.
│   ├── charts.py           # Wrappers de Plotly (Treemap, Sunburst, Waterfall).
│   └── forms.py            # Formularios modulares para crear/editar.
│
├── pages/                  # Vistas individuales de Streamlit.
│   ├── page_Dashboard.py     # Resumen ejecutivo y analítico.
│   ├── page_Movimientos.py   # DataGrid con CRUD completo y filtros.
│   ├── page_Inteligencia.py  # Modelos ML, anomalías e insights.
│   ├── page_Simulador.py     # Simulador de escenarios financieros.
│   ├── page_Reportes.py      # Descarga y visualización de reportes.
│   └── page_Configuracion.py # Gestión de usuarios, sistema y backups.
│
├── utils/                  # Funciones de soporte.
│   ├── formatters.py       # Formateo de números, fechas.
│   └── validators.py       # Validación de inputs.
│
├── backups/                # Destino de backups de SQLite.
├── exports/                # Archivos generados (Excel, PDF).
├── imports/                # Archivos subidos por usuarios.
├── logs/                   # Archivos de auditoría y errores.
└── assets/                 # CSS custom, logos, íconos.

para clonar el proyecto 
https://github.com/wgekko/app-analisis-presupuesto.git


Video demo





https://github.com/user-attachments/assets/05d2d6c4-5396-44bc-8e58-5adb8dc6fc2a




