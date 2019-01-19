import pandas as pd
df_cantabria = pd.read_csv('Cantabria_data/data_cantabria.csv')
#modify first column name
df_cantabria.columns.values[0] = 'Fecha'
#filtering data per year and avg visit
df_cantabria_años = df_cantabria.iloc[:118:13,:63:3]
df_cantabria_años.to_csv('Cantabria_data/data_cantabria_estancia_media_año.csv', encoding='utf-8', index=False)