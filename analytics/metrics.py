# import pandas as pd

# def get_core_kpis(df: pd.DataFrame) -> dict:
#     """
#     Calcula los totales de Ingresos, Egresos y el Balance Neto.
#     Devuelve un diccionario listo para ser consumido por las tarjetas KPI.
#     """
#     if df.empty:
#         return {"ingresos": 0.0, "egresos": 0.0, "balance": 0.0}
    
#     ingresos = df[df['tipo'] == 'Ingreso']['importe'].sum()
#     egresos = df[df['tipo'] == 'Egreso']['importe'].sum()
#     balance = ingresos - egresos
    
#     return {
#         "ingresos": float(ingresos),
#         "egresos": float(egresos),
#         "balance": float(balance)
#     }

# def get_expenses_by_category(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Agrupa y suma los egresos por categoría, ordenados de mayor a menor.
#     Útil para gráficos de pastel o barras en el Dashboard.
#     """
#     egresos_df = df[df['tipo'] == 'Egreso']
#     if egresos_df.empty:
#         return pd.DataFrame(columns=['categoria', 'importe'])
    
#     agrupado = egresos_df.groupby('categoria')['importe'].sum().reset_index()
#     return agrupado.sort_values(by='importe', ascending=False)

# def get_monthly_cashflow(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Genera un resumen mensual de ingresos y egresos.
#     """
#     if df.empty:
#         return pd.DataFrame()
        
#     df_temp = df.copy()
#     # Asegurar que la fecha sea tipo datetime
#     df_temp['fecha'] = pd.to_datetime(df_temp['fecha'])
#     # Crear columna de 'Mes-Año' (Ej: 2026-01)
#     df_temp['mes'] = df_temp['fecha'].dt.to_period('M').astype(str)
    
#     # Agrupar por mes y tipo
#     pivot_df = df_temp.pivot_table(
#         index='mes', 
#         columns='tipo', 
#         values='importe', 
#         aggfunc='sum', 
#         fill_value=0
#     ).reset_index()
    
#     # Asegurar que existan ambas columnas aunque no haya datos
#     if 'Ingreso' not in pivot_df.columns: pivot_df['Ingreso'] = 0.0
#     if 'Egreso' not in pivot_df.columns: pivot_df['Egreso'] = 0.0
    
#     # Calcular balance mensual
#     pivot_df['Balance'] = pivot_df['Ingreso'] - pivot_df['Egreso']
    
#     return pivot_df.sort_values('mes')

import pandas as pd

def get_core_kpis(df: pd.DataFrame) -> dict:
    """
    Calcula los totales de Ingresos, Egresos y el Balance Neto.
    Devuelve un diccionario listo para ser consumido por las tarjetas KPI.
    """
    if df.empty:
        return {"ingresos": 0.0, "egresos": 0.0, "balance": 0.0}
    
    ingresos = df[df['tipo'] == 'Ingreso']['importe'].sum()
    egresos = df[df['tipo'] == 'Egreso']['importe'].sum()
    balance = ingresos - egresos
    
    return {
        "ingresos": float(ingresos),
        "egresos": float(egresos),
        "balance": float(balance)
    }

def get_expenses_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa y suma los egresos por categoría, ordenados de mayor a menor.
    """
    egresos_df = df[df['tipo'] == 'Egreso']
    if egresos_df.empty:
        return pd.DataFrame(columns=['categoria', 'importe'])
    
    agrupado = egresos_df.groupby('categoria')['importe'].sum().reset_index()
    return agrupado.sort_values(by='importe', ascending=False)

def get_monthly_cashflow(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un resumen mensual de ingresos y egresos.
    """
    if df.empty:
        return pd.DataFrame()
        
    df_temp = df.copy()
    df_temp['fecha'] = pd.to_datetime(df_temp['fecha'])
    df_temp['mes'] = df_temp['fecha'].dt.to_period('M').astype(str)
    
    pivot_df = df_temp.pivot_table(
        index='mes', 
        columns='tipo', 
        values='importe', 
        aggfunc='sum', 
        fill_value=0
    ).reset_index()
    
    if 'Ingreso' not in pivot_df.columns: pivot_df['Ingreso'] = 0.0
    if 'Egreso' not in pivot_df.columns: pivot_df['Egreso'] = 0.0
    
    pivot_df['Balance'] = pivot_df['Ingreso'] - pivot_df['Egreso']
    
    return pivot_df.sort_values('mes')


def get_ratio_cobertura(df: pd.DataFrame) -> dict:
    """
    Calcula el Ratio de Cobertura de Egresos: (Ingresos / Egresos) * 100.
    Indica qué porcentaje de los egresos está cubierto por los ingresos generados.
    """
    if df.empty:
        return {"ratio": 0.0, "ingresos": 0.0, "egresos": 0.0}
    
    ingresos = df[df['tipo'] == 'Ingreso']['importe'].sum()
    egresos = df[df['tipo'] == 'Egreso']['importe'].sum()
    
    if egresos == 0:
        ratio = 100.0 if ingresos > 0 else 0.0
    else:
        ratio = (ingresos / egresos) * 100.0
        
    return {
        "ratio": float(ratio),
        "ingresos": float(ingresos),
        "egresos": float(egresos)
    }

def get_top_concepts(df: pd.DataFrame, tipo: str = "Egreso", top_n: int = 10) -> pd.DataFrame:
    """
    Agrupa los movimientos por concepto y calcula el total acumulado y la frecuencia.
    """
    df_filtrado = df[df['tipo'] == tipo]
    if df_filtrado.empty:
        return pd.DataFrame(columns=['concepto', 'categoria', 'transacciones', 'monto_total'])
    
    agrupado = df_filtrado.groupby(['concepto', 'categoria']).agg(
        transacciones=('importe', 'count'),
        monto_total=('importe', 'sum')
    ).reset_index()
    
    # Ordenar por monto descendente y seleccionar Top N
    top_df = agrupado.sort_values(by='monto_total', ascending=False).head(top_n)
    return top_df



def get_pareto_data(df: pd.DataFrame, tipo: str = "Egreso") -> pd.DataFrame:
    """
    Calcula los datos para la Curva ABC / Diagrama de Pareto (Regla del 80/20).
    Suma importes por concepto, los ordena de mayor a menor y calcula el % acumulado.
    """
    df_filtrado = df[df['tipo'] == tipo]
    if df_filtrado.empty:
        return pd.DataFrame()
        
    pareto = df_filtrado.groupby('concepto')['importe'].sum().reset_index()
    pareto = pareto.sort_values(by='importe', ascending=False)
    
    total = pareto['importe'].sum()
    if total == 0:
        return pd.DataFrame()
        
    pareto['acumulado'] = pareto['importe'].cumsum()
    pareto['pct_acumulado'] = (pareto['acumulado'] / total) * 100.0
    return pareto

def get_heatmap_matrix(df: pd.DataFrame, tipo: str = "Egreso", dimension: str = "categoria") -> pd.DataFrame:
    """
    Genera una matriz pivote (Dimensión vs Mes) para construir la Matriz de Calor.
    """
    df_f = df[df['tipo'] == tipo].copy()
    if df_f.empty:
        return pd.DataFrame()
        
    df_f['fecha'] = pd.to_datetime(df_f['fecha'])
    df_f['mes'] = df_f['fecha'].dt.to_period('M').astype(str)
    
    pivot = df_f.pivot_table(
        index=dimension, 
        columns='mes', 
        values='importe', 
        aggfunc='sum', 
        fill_value=0.0
    )
    return pivot

def get_multiproject_margin(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el Margen Neto (Ingresos - Egresos) mensual desglosado por Proyecto.
    """
    if df.empty:
        return pd.DataFrame()
        
    df_c = df.copy()
    df_c['fecha'] = pd.to_datetime(df_c['fecha'])
    df_c['mes'] = df_c['fecha'].dt.to_period('M').astype(str)
    
    grouped = df_c.groupby(['mes', 'proyecto', 'tipo'])['importe'].sum().unstack(fill_value=0.0).reset_index()
    
    if 'Ingreso' not in grouped.columns: grouped['Ingreso'] = 0.0
    if 'Egreso' not in grouped.columns: grouped['Egreso'] = 0.0
    
    grouped['margen_neto'] = grouped['Ingreso'] - grouped['Egreso']
    return grouped.sort_values('mes')