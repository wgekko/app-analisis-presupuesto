# import pandas as pd
# import numpy as np
# from sklearn.linear_model import LinearRegression
# from datetime import timedelta

# def proyectar_tendencia(df: pd.DataFrame, dias_futuro: int = 30, tipo_movimiento: str = 'Ingreso') -> pd.DataFrame:
#     """Proyecta tendencias a futuro basándose en los datos históricos."""
#     df_filtrado = df[df['tipo'] == tipo_movimiento].copy()
    
#     if len(df_filtrado) < 5:
#         return pd.DataFrame()
    
#     # Agrupamos por fecha para tener la suma diaria
#     df_filtrado['fecha'] = pd.to_datetime(df_filtrado['fecha'])
#     df_diario = df_filtrado.groupby('fecha')['importe'].sum().reset_index()
#     df_diario = df_diario.sort_values('fecha')
    
#     # Ingeniería de características: Convertimos las fechas a "días transcurridos"
#     fecha_inicio = df_diario['fecha'].min()
#     df_diario['dias_transcurridos'] = (df_diario['fecha'] - fecha_inicio).dt.days
    
#     X = df_diario[['dias_transcurridos']]
#     y = df_diario['importe']
    
#     # Entrenamos el modelo
#     modelo = LinearRegression()
#     modelo.fit(X, y)
    
#     # Generamos los días futuros
#     ultimo_dia = df_diario['dias_transcurridos'].max()
#     X_futuro = np.array(range(ultimo_dia + 1, ultimo_dia + 1 + dias_futuro)).reshape(-1, 1)
#     fechas_futuras = [fecha_inicio + timedelta(days=int(d)) for d in X_futuro.flatten()]
    
#     # Predecimos
#     predicciones = modelo.predict(X_futuro)
    
#     # Prevenimos predicciones negativas para importes
#     predicciones = np.maximum(predicciones, 0)
    
#     df_proyeccion = pd.DataFrame({
#         'fecha': fechas_futuras,
#         'importe': predicciones,
#         'tipo': f'Proyección {tipo_movimiento}'
#     })
    
#     return df_proyeccion


import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def proyectar_tendencia(df: pd.DataFrame, meses_futuros: int = 3) -> pd.DataFrame:
    """
    Calcula una proyección de tendencia lineal basada en el comportamiento histórico mensual.
    """
    if df.empty or len(df) < 3:
        return pd.DataFrame()
    
    df_temp = df.copy()
    df_temp['fecha'] = pd.to_datetime(df_temp['fecha'])
    df_temp['mes_idx'] = df_temp['fecha'].dt.year * 12 + df_temp['fecha'].dt.month
    
    # Agrupar importes por mes índice
    mensual = df_temp.groupby('mes_idx')['importe'].sum().reset_index()
    if len(mensual) < 2:
        return pd.DataFrame()
        
    X = mensual[['mes_idx']]
    y = mensual['importe']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Generar índices futuros
    ultimo_idx = mensual['mes_idx'].max()
    futuros_idx = [ultimo_idx + i for i in range(1, meses_futuros + 1)]
    predicciones = model.predict(pd.DataFrame({'mes_idx': futuros_idx}))
    
    # Reconstruir fechas legibles para el gráfico
    fechas_futuras = pd.to_datetime([f"{idx // 12}-{idx % 12:02d}-01" for idx in futuros_idx])
    
    df_res = pd.DataFrame({
        'fecha': fechas_futuras,
        'prediccion': predicciones
    })
    return df_res