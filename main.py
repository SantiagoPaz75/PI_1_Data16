from fastapi import FastAPI
app = FastAPI()

import pandas as pd

# Importamos los archivos y los almacenamos como DataFrames
df_games = pd.read_csv('steam_games.csv')
df_reviews = pd.read_csv('reviews.csv')
df_items = pd.read_csv('items.csv')

@app.get('/developer/') 
def developer(desarrolladora: str):
    # Creamos un DataFrame más reducido
    df_end1 = df_games.loc[:,['developer', 'item_id', 'price','release_date']]
    # Utiliza el método str.split para dividir la fecha en sus componentes (Año, Mes, Día) dejando solo el año
    df_end1['release_date'] = df_end1['release_date'].str.split('-').str.get(0)
    # Filtra el DataFrame para los juegos de la empresa desarrolladora especificada
    juegos_desarrolladora = df_end1[df_end1['developer'] == desarrolladora]
    # Agrupa por año y cuenta la cantidad de juegos
    juegos_por_ano = juegos_desarrolladora.groupby('release_date').size().reset_index(name='Cantidad de Items')
    # Filtra los juegos gratuitos
    juegos_gratuitos = juegos_desarrolladora[juegos_desarrolladora['price'] == 0]
    # Agrupa los juegos gratuitos por año y cuenta la cantidad
    juegos_gratuitos_por_ano = juegos_gratuitos.groupby('release_date').size().reset_index(name='cantidad_juegos_gratuitos')
    # Combina los datos de juegos totales y juegos gratuitos por año
    resultado = pd.merge(juegos_por_ano, juegos_gratuitos_por_ano, on='release_date', how='left')
    # Rellena los valores nulos en juegos gratuitos con 0
    resultado['cantidad_juegos_gratuitos'].fillna(0, inplace=True)
    # Calcula el porcentaje de juegos gratuitos por año
    resultado['porcentaje_juegos_gratuitos'] = (resultado['cantidad_juegos_gratuitos'] / resultado['Cantidad de Items']) * 100
    # Elimina la columna 'cantidad_juegos_gratuitos'
    resultado.drop(columns='cantidad_juegos_gratuitos', inplace=True)
    # Renombra las columnas
    resultado.rename(columns={'release_date': 'Año', 'porcentaje_juegos_gratuitos': 'Contenido Free'}, inplace=True)
    # Convierte la columna 'Cantidad de Items' a enteros y 'Contenido Free' a flotantes
    resultado['Cantidad de Items'] = resultado['Cantidad de Items'].astype(int)
    resultado['Contenido Free'] = resultado['Contenido Free'].astype(float)
    # Convierte el DataFrame a una lista de diccionarios para asegurarse de que los tipos de datos sean estándar de Python (evita errores en FastAPI)
    resultado_dict_list = resultado.to_dict(orient='records')
    return resultado_dict_list

@app.get('/userdata/') 
def userdata(user_id:str):
    # Convierte user_id a tipo str
    user_id = str(user_id)    
    # Filtra las compras del usuario en df_items
    compras_usuario = df_items[df_items['user_id'] == user_id]
    # Combina la información de las compras con los datos de los juegos en df_games
    compras_usuario = pd.merge(compras_usuario, df_games, on='item_id', how='inner')
    # Calcula el gasto total del usuario
    gasto_total = compras_usuario['price'].sum()
    # Filtra las revisiones del usuario en df_reviews
    revisiones_usuario = df_reviews[(df_reviews['user_id'] == user_id) & (df_reviews['item_id'].isin(compras_usuario['item_id']))]
    # Calcula el porcentaje de recomendación positiva
    porcentaje_recomendacion = (revisiones_usuario['recommend'].sum() / len(revisiones_usuario)) * 100
    # Calcula la cantidad de ítems comprados
    cantidad_items = len(compras_usuario)
    # Devuelve las estadísticas
    return {
        'Gasto Total': round(gasto_total,2),
        'Porcentaje de Recomendación Promedio': porcentaje_recomendacion,
        'Cantidad de Ítems': cantidad_items
    }
