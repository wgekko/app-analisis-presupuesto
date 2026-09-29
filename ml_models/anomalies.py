# import pandas as pd
# from sklearn.ensemble import IsolationForest

# def detectar_anomalias(df: pd.DataFrame) -> pd.DataFrame:
#     """Aplica Isolation Forest para detectar registros financieros inusuales."""
#     if len(df) < 10: # Necesitamos un mínimo de datos para que el modelo aprenda
#         return pd.DataFrame()
    
#     df_model = df.copy()
    
#     # Preparamos los datos: Entrenaremos el modelo usando solo el 'importe'
#     X = df_model[['importe']].fillna(0)
    
#     # Configuración del modelo (asumimos que el ~5% de los datos podrían ser anómalos)
#     modelo_if = IsolationForest(contamination=0.05, random_state=42)
    
#     # -1 representa una anomalía, 1 es un dato normal
#     df_model['es_anomalia'] = modelo_if.fit_predict(X)
    
#     # Filtramos y devolvemos solo las anomalías detectadas
#     anomalias = df_model[df_model['es_anomalia'] == -1].copy()
#     return anomalias

import pandas as pd
from sklearn.ensemble import IsolationForest

def detectar_anomalias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Utiliza Machine Learning (Isolation Forest) para detectar 
    egresos o transacciones atípicas que se salgan del comportamiento normal.
    """
    if df.empty or len(df) < 5:
        return pd.DataFrame()
    
    egresos = df[df['tipo'] == 'Egreso'].copy()
    if len(egresos) < 5:
        return pd.DataFrame()
        
    # Seleccionamos la variable numérica (importe) para la detección
    X = egresos[['importe']]
    
    # Configuramos el modelo de aislamiento de anomalías
    iso = IsolationForest(contamination=0.05, random_state=42)
    egresos['anomaly'] = iso.fit_predict(X)
    
    # El valor -1 representa una anomalía/outlier detectado
    anomalias = egresos[egresos['anomaly'] == -1]
    return anomalias