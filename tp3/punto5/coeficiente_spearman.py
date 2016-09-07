
# coding: utf-8

import csv
import pandas as pd
import numpy as np
import os
import sys
import re

def getListas():
    listas = []
    for i in range(2):
        got = raw_input("Ingresar ruta a lista %s: " % (i+1))
        pattern = re.compile(r"(?:^['\"])(.+?)(?:['\"](?:\s)*)")
        m = pattern.match(got)
        if m:
            got = m.groups()[0]
        if not(os.path.isfile(got)):
            print "Path a archivo no es válido"
            return False
        else:
            listas.append(got)
    return listas

def coeficienteSpearman(df):
    n = len(df)
    df['d'] = df[df.columns[0]] - df[df.columns[1]]
    df['d_cuadrado'] = np.power(df['d'],2)
    sum_d_cuadrado = sum(df['d_cuadrado']) 
    resultado = 1 - ( (6.0 * sum_d_cuadrado) / (n * ( np.power(n,2.0) - 1.0 ) ) )
    # WARNING: NO ANDA BIEN
    #if n > 20:
    #    resultado = resultado / np.sqrt( (1.0 - np.power( resultado,2.0 )) / (n - 2.0) )
    return resultado 

def main():
    listas = getListas()
    if not listas:
        sys.exit()

    data = []
    for i in range(2):
        data.append(pd.read_csv(listas[i], sep=" ", header = None, names=["Id query", "Q", "Id doc", "Ranking", "Similtud", "Modelo"], index_col=["Id query","Id doc"]))
        modelo = data[i]['Modelo'].iloc[0]
        data[i].drop(['Q','Modelo'], axis=1, inplace=True)
        data[i].columns = ["Ranking - "+modelo, "Similtud - "+modelo]

    df = pd.concat([data[0], data[1]],axis=1,join="outer")

    # Ordeno por iDQUERY y luego por ranking del primero de los dos modelos
    df = df.reset_index()
    df = df.sort_values(["Id query",df.columns[2]])
    df = df.set_index(["Id query", "Id doc"])

    df.to_csv("resultados_queries.csv")

    # Elimino columnas que contienen valor de similtud (no me interesa para clcular spearman)
    spearman = df.drop(df.columns[[1,3]], axis=1)

    # Remuevo valores NaN (cuando un modelo devuelve un documento pero el otro no)
    # NaN los relleno con el maximo rank + 1 de cada modelo en cada query
    fillValues = spearman.max(level="Id query")+1
    spearman = spearman.fillna(value=fillValues)

    # Creo el data frame resultado en donde muestro el coeficiente obtenido para cada query
    spearman = spearman.reset_index()
    df = pd.DataFrame(index=np.arange(min(spearman['Id query']), max(spearman['Id query'])+1), columns=['Coeficiente (n=10)', 'Coeficiente (n=25)', 'Coeficiente (n=50)'], dtype = 'float64')
    df.index.name = "Id query"

    # A cada index le doy su coeficiente para los primeros 'n' resultados
    for i in df.index:
        
        # creo dataframe 'query' con los datos del query con id 'i'
        query = spearman[spearman['Id query'] == i]
        query = query.drop("Id query", axis=1)
        query = query.set_index(["Id doc"])
        # Calculo coeficiente
        df.loc[i,"Coeficiente (n=10)"] = coeficienteSpearman(query.head(n=10)) 
        df.loc[i,"Coeficiente (n=25)"] = coeficienteSpearman(query.head(n=25)) 
        df.loc[i,"Coeficiente (n=50)"] = coeficienteSpearman(query.head(n=50)) 
        
    # Restauro index 
    spearman = spearman.set_index(["Id query", "Id doc"])

    df.to_csv("coeficiente_spearman.csv")

if __name__ == "__main__":
    main()

