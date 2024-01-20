# TSP con templado simulado
import math
import random

from flask import Flask, render_template, request, jsonify
from operator import itemgetter

app = Flask(__name__)

coord = {
        'Jilotepec': (19.984146, -99.519127),
        'Toluca': (19.283389, -99.651294),
        'Atlacomulco': (19.797032, -99.875878),
        'Guadalajara': (20.666006, -103.343649),
        'Monterrey': (25.687299, -100.315655),
        'Cancun': (21.080865, -86.773482),
        'Morelia': (19.706167, -101.191413),
        'Aguascalientes': (21.861534, -102.321629),
        'Queretaro': (20.5856142, -100.392965),
        'Cdmx': (19.432361, -99.133111) 
}

def distancia(coord1, coord2):
    lat1=coord1[0]
    lon1=coord1[1]
    lat2=coord2[0]
    lon2=coord2[1]

    return math.sqrt((lat1-lat2)**2+(lon1-lon2)**2)

# calcula la distancia cubierta por una ruta
def evalua_ruta(ruta):
    total=0
    for i in range(0,len(ruta)-1):
        ciudad1=ruta[i]
        ciudad2=ruta[i+1]
        total+=distancia(coord[ciudad1], coord[ciudad2])
    ciudad1=ruta[i+1]
    ciudad2=ruta[0]
    total+=distancia(coord[ciudad1], coord[ciudad2])

    return total

def busqueda_tabu(ruta):
    mejor_ruta=ruta
    memoria_tabu={}
    persistencia=5
    mejora=False
    iteraciones=100

    while iteraciones>0:
        iteraciones = iteraciones-1
        dist_actual=evalua_ruta(ruta)
        # evaluar vecinos
        mejora=False
        for i in range(0,len(ruta)):
            if mejora:
                break
            for j in range(0,len(ruta)):
                if i!=j:
                    ruta_tmp=ruta[:]
                    ciudad_tmp=ruta_tmp[i]
                    ruta_tmp[i]=ruta_tmp[j]
                    ruta_tmp[j]=ciudad_tmp
                    dist=evalua_ruta(ruta_tmp)

                    # comprobar si el movimiento es tabú
                    tabu=False
                    if ruta_tmp[i]+"_"+ruta_tmp[j] in memoria_tabu:
                        if memoria_tabu[ruta_tmp[i]+"_"+ruta_tmp[j]]>0:
                            tabu=True
                    if ruta_tmp[j]+"_"+ruta_tmp[i] in memoria_tabu:
                        if memoria_tabu[ruta_tmp[j]+"_"+ruta_tmp[i]]>0:
                            tabu=True
                    if dist<dist_actual and not tabu:
                        # encontrado vecino que mejora el resultado
                        ruta=ruta_tmp[:]
                        if evalua_ruta(ruta)<evalua_ruta(mejor_ruta):
                            mejor_ruta=ruta[:]
                        # almacenamos en memoria tabú
                        memoria_tabu[ruta_tmp[i]+"_"+ruta_tmp[j]]=persistencia
                        mejora=True
                        break
                    elif dist<dist_actual and tabu:
                        # comprobamos criterio de aspiración
                        # aunque sea movimiento tabú
                        if evalua_ruta(ruta_tmp)<evalua_ruta(mejor_ruta):
                            mejor_ruta=ruta_tmp[:]
                            ruta=ruta_tmp[:]
                            # almacenamos en memoria tabú
                            memoria_tabu[ruta_tmp[i]+"_"+ruta_tmp[j]]=persistencia
                            mejora=True
                            break

        # rebajar persistencia de los movimientos tabú
        if len(memoria_tabu)>0:
            for k in memoria_tabu:
                if memoria_tabu[k]>0:
                    memoria_tabu[k]=memoria_tabu[k]-1
    return mejor_ruta

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/registrar_ciudad', methods=['POST'])
def registrar_ciudad():
    try:
        # Obtener los valores de latitud y longitud desde el formulario
        ciudad = str(request.form['persistencia'])
        latitud = float(request.form['iteraciones'])
        longitud = float(request.form['longitud'])

        #return render_template('resultado.html',nombre=nombre, latitud=latitud, longitud=longitud)
        coord[ciudad] = (latitud, longitud)
        return jsonify({"mensaje": f"Coordenadas de {ciudad} configuradas correctamente"})
    except ValueError:
        error_msg = "Por favor, ingresa todos los valores"
        return render_template('index.html', error_msg=error_msg)

@app.route('/mostrar_evaluacion', methods=['GET'])

def mostrar_evaluacion():
    try:
        ruta=[]
        for ciudad in coord:
            ruta.append(ciudad)
        random.shuffle(ruta)
        ruta = busqueda_tabu(ruta)
        distancia_total = evalua_ruta(ruta)
        #return jsonify({"ruta_optima": ruta, "Distacia": str(evalua_ruta(ruta))})
        return render_template("resultado.html", ruta=ruta, distancia_total=distancia_total)

    except ValueError:
        error_msg = "Ocurrió un error al calcular la evaluación de la ruta."
        return jsonify({"error": error_msg})

if __name__ == '__main__':
    app.run(debug=True)

