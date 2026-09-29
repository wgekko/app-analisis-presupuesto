# import pandas as pd
# from io import BytesIO

# class ExportService:
#     @staticmethod
#     def to_excel(df: pd.DataFrame) -> BytesIO:
#         """Convierte un DataFrame en un archivo Excel en memoria."""
#         output = BytesIO()
#         with pd.ExcelWriter(output, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False, sheet_name='Movimientos')
#         output.seek(0)
#         return output

#     @staticmethod
#     def to_csv(df: pd.DataFrame) -> str:
#         """Convierte un DataFrame en formato CSV optimizado."""
#         return df.to_csv(index=False).encode('utf-8')


import pandas as pd
import io

class ExportService:
    """Servicio para convertir DataFrames a formatos descargables."""
    
    @staticmethod
    def to_csv(df: pd.DataFrame) -> bytes:
        return df.to_csv(index=False).encode('utf-8')

    @staticmethod
    def to_excel(df: pd.DataFrame) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Reporte_Financiero')
            
            # Auto-ajustar columnas (Opcional, mejora visual)
            worksheet = writer.sheets['Reporte_Financiero']
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)
                
        return output.getvalue()    