import pandas as pd

#definir el rango de fechas
fecha_inicio = pd.to_datetime('2024-06-17')
fecha_fin = pd.to_datetime('2024-09-14')

#definir cantidad sorteados
cant_sorteados = 10
sorteados = {}

#leer datos
df = pd.read_csv('data.csv')
df['hora1'] = pd.to_datetime(df['hora'], format='%Y-%m-%dT%H:%M:%S.%fZ')


#filtrar por fecha
df_filtrado = df[(df['hora1'] >= fecha_inicio) & (df['hora1'] <= fecha_fin)]

#sacar sorteados
while len(sorteados) < cant_sorteados:
    registro = df_filtrado.sample()
    _id = registro.values[0][0]  
    nombre = registro.values[0][1] 
    numero = registro.values[0][2] 
    sorteados[numero] = {'nombre': nombre, 'id_participacion': _id}


df_sorteados = pd.DataFrame(columns=df.columns)  
for numero, reg in sorteados.items():
    print(reg['id_participacion'])
    df_sorteados = df_sorteados._append(df_filtrado[df_filtrado['ID'] == reg['id_participacion']] )  # Agregar el registro correspondiente a df_sorteados

df_sorteados.to_csv('registros_sorteados.csv', index=False)

