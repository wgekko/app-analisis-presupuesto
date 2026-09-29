import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def agrupar_comportamiento_gastos(df: pd.DataFrame) -> pd.DataFrame:
    """Clasifica las categorías de egresos según su impacto y frecuencia."""
    egresos = df[df['tipo'] == 'Egreso'].copy()
    if len(egresos) < 3:
        return pd.DataFrame()

    # Resumir por categoría
    resumen = egresos.groupby('categoria').agg(
        frecuencia=('importe', 'count'),
        monto_total=('importe', 'sum')
    ).reset_index()

    # Escalar datos para K-Means
    scaler = StandardScaler()
    variables_escaladas = scaler.fit_transform(resumen[['frecuencia', 'monto_total']])

    # Aplicar clustering
    kmeans = KMeans(n_clusters=min(3, len(resumen)), random_state=42, n_init=10)
    resumen['cluster'] = kmeans.fit_predict(variables_escaladas)

    # Ordenar clústeres por monto para asignar nombres lógicos
    orden_clusters = resumen.groupby('cluster')['monto_total'].mean().sort_values().index
    mapeo = {orden_clusters[0]: 'Gasto Bajo/Controlado', 
             orden_clusters[1]: 'Gasto Medio/Frecuente', 
             orden_clusters[2]: 'Gasto Alto/Crítico'}
             
    resumen['perfil_gasto'] = resumen['cluster'].map(mapeo)
    return resumen.drop(columns=['cluster']).sort_values(by='monto_total', ascending=False)