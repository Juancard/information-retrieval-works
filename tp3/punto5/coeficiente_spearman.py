# coding: utf-8

import csv
import pandas as pd
import numpy as np
import os
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

def sp(a):
    CONSTANTE = 6.0 #  valor que se multiplica por sumatoria del cuadrado de las diferencias
    N = len(a) - 1.0 # posicion maxima del ranking
    
    diferencia = a[a.columns[2]] - a[a.columns[3]]
    diferenciaCuadrado = np.power(diferencia, 2.0)
    sumDifCuad = sum(diferenciaCuadrado)
    dividendo = sumDifCuad * CONSTANTE
    divisor = N * (np.power(N, 2.0) - 1.0)

    if divisor == 0 or dividendo == 0:
        cs = 1
    else:
        cs = 1 - (dividendo / divisor) 
    
    return cs

def getTopN(df, n):
    return df.sort_values(["Id query",df.columns[0]]).groupby("Id query").head(n)

def main():

    listasPath = getListas()
    if not listasPath:
        sys.exit()

    lista = []
    for i in range(2):
        lista.append(pd.read_csv(listasPath[i], sep=" ", header = None, names=["Id query", "Q", "Id doc", "Ranking", "Similtud", "Modelo"], index_col=["Id query","Id doc"]))
        modelo = lista[i]['Modelo'].iloc[0]
        lista[i].drop(['Q','Modelo', "Similtud"], axis=1, inplace=True)
        lista[i].columns = ["Ranking - "+modelo]
    lista[1].tail()

    tops = {
        10: [],
        25: [],
        50: []
    }
    for k in tops:
        # Obtengo top k para ambas listas
        ranks = [getTopN(df.reset_index(), k).set_index(["Id query", "Id doc"]) for df in lista]
        
        # Concateno listas
        ranksConcat = pd.concat(ranks, axis=1, join="outer")

        # Docs id que se encuentran en una lista y no en otra se rellenan con el rank maximo + 1
        fillValues = ranksConcat.max(level="Id query") + 1
        ranksConcat = ranksConcat.fillna(value=fillValues)

        # Calculo coeficiente de spearman
        tops[k] = ranksConcat.reset_index().groupby(["Id query"]).apply(sp)

    cs = pd.concat([tops[k] for k in sorted(tops)], axis=1,join="outer")
    cs.columns = ["Top %d" % k for k in sorted(tops)]

    cs.to_csv("coeficiente_spearman.csv")

if __name__ == "__main__":
    main()
