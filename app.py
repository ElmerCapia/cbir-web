from flask import Flask, render_template, request
import cv2
import os
import numpy as np

app = Flask(__name__)

# ======================================================
# DATASET
# ======================================================

ruta_dataset = "dataset/training_set"

imagenes = []
etiquetas = []
rutas = []

# ======================================================
# CARGAR DATASET
# ======================================================

def cargar_dataset():

    print("===================================")
    print("CARGANDO DATASET...")
    print("===================================")

    for clase in os.listdir(ruta_dataset):

        ruta_clase = os.path.join(
            ruta_dataset,
            clase
        )

        if os.path.isdir(ruta_clase):

            print(f"Clase encontrada: {clase}")

            for archivo in os.listdir(ruta_clase):

                ruta_img = os.path.join(
                    ruta_clase,
                    archivo
                )

                img = cv2.imread(ruta_img)

                if img is not None:

                    imagenes.append(img)

                    etiquetas.append(clase)

                    # ruta para web
                    ruta_web = ruta_img.replace("\\", "/")

                    ruta_web = ruta_web.replace(
                        "dataset/",
                        "static/dataset/"
                    )

                    rutas.append(ruta_web)

                    print(f"Imagen cargada: {archivo}")

# ======================================================
# CARGAR TODO
# ======================================================

cargar_dataset()

print("===================================")
print("DATASET CARGADO")
print("TOTAL IMÁGENES:", len(imagenes))
print("===================================")

# ======================================================
# PREPROCESAMIENTO
# ======================================================

def preprocesar(img):

    img = cv2.resize(
        img,
        (256, 256)
    )

    return img

# ======================================================
# DESCRIPTOR HISTOGRAMA
# ======================================================

def descriptor_histograma(img):

    img = preprocesar(img)

    hist = cv2.calcHist(

        [img],
        [0,1,2],
        None,
        [8,8,8],
        [0,256,0,256,0,256]

    )

    hist = cv2.normalize(
        hist,
        hist
    ).flatten()

    return hist

# ======================================================
# DESCRIPTOR ORB
# ======================================================

orb = cv2.ORB_create(
    nfeatures=500
)

def descriptor_orb(img):

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

    kp, des = orb.detectAndCompute(
        gray,
        None
    )

    if des is None:

        return np.zeros(32)

    des = np.mean(
        des,
        axis=0
    )

    return des

# ======================================================
# DESCRIPTOR COMBINADO
# ======================================================

def descriptor_combinado(img):

    # histograma
    h = descriptor_histograma(img)

    # orb
    o = descriptor_orb(img)

    # normalizar histograma
    h = h / np.linalg.norm(h)

    # normalizar orb
    if np.linalg.norm(o) != 0:

        o = o / np.linalg.norm(o)

    # fusionar
    combinado = np.concatenate(
        (h, o)
    )

    return combinado

# ======================================================
# GENERAR DESCRIPTORES
# ======================================================

print("===================================")
print("GENERANDO DESCRIPTORES...")
print("===================================")

train_vec = []

for img in imagenes:

    vec = descriptor_combinado(img)

    train_vec.append(vec)

train_vec = np.array(train_vec)

print("DESCRIPTORES GENERADOS")

# ======================================================
# DISTANCIA EUCLIDIANA
# ======================================================

def distancia_euclidiana(a, b):

    return np.linalg.norm(a - b)

# ======================================================
# DISTANCIA MANHATTAN
# ======================================================

def distancia_manhattan(a, b):

    return np.sum(
        np.abs(a - b)
    )

# ======================================================
# SIMILITUD COSENO
# ======================================================

def similitud_coseno(a, b):

    return np.dot(a, b) / (

        np.linalg.norm(a) *
        np.linalg.norm(b)

    )

# ======================================================
# HOME
# ======================================================

@app.route("/")
def home():

    return render_template(

        "index.html",

        total=len(imagenes)

    )

# ======================================================
# BUSCAR
# ======================================================

@app.route("/buscar", methods=["POST"])
def buscar():

    archivo = request.files["imagen"]

    metodo = request.form["metodo"]

    # guardar query
    ruta_query = "static/uploads/query.jpg"

    archivo.save(ruta_query)

    # leer query
    img_query = cv2.imread(ruta_query)

    # descriptor query
    query_vec = descriptor_combinado(
        img_query
    )

    resultados = []

    # ==================================================
    # COMPARAR
    # ==================================================

    for i in range(len(train_vec)):

        # ----------------------------------------------
        # COSENO
        # ----------------------------------------------

        if metodo == "coseno":

            valor = similitud_coseno(

                query_vec,
                train_vec[i]

            )

        # ----------------------------------------------
        # EUCLIDIANA
        # ----------------------------------------------

        elif metodo == "euclidiana":

            valor = distancia_euclidiana(

                query_vec,
                train_vec[i]

            )

        # ----------------------------------------------
        # MANHATTAN
        # ----------------------------------------------

        elif metodo == "manhattan":

            valor = distancia_manhattan(

                query_vec,
                train_vec[i]

            )

        resultados.append(

            (
                valor,
                etiquetas[i],
                rutas[i]
            )

        )

    # ==================================================
    # ORDENAR
    # ==================================================

    if metodo == "coseno":

        resultados.sort(

            key=lambda x: x[0],
            reverse=True

        )

    else:

        resultados.sort(

            key=lambda x: x[0]

        )

    # ==================================================
    # TOP RESULTADOS
    # ==================================================

    top5 = resultados[:6]

    return render_template(

        "resultado.html",

        resultados=top5,

        metodo=metodo

    )

# ======================================================

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)