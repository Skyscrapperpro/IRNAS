import sys
import time
import sklearn.datasets as skdata
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
import scipy.optimize as opt
import scipy.sparse as sp
import qpsolvers as qp
import isadoralib as isl
import multiprocessing as mp
import tqdm
import warnings
warnings.filterwarnings("ignore")


# # carga el dataset de iris de sklearn
# dataset = skdata.load_iris()
# carga el dataset de dígitos de sklearn
dataset = skdata.load_digits()
# # carga el dataset de cancer de sklearn
#dataset = skdata.load_breast_cancer()
# # carga el dataset de vinos de sklearn
#dataset = skdata.load_wine()

# genera una lista de valores de alpha de 0 a 2 con paso 0.1
alphas = np.arange(0, 2.1, 0.1)

verbose = False

# numero de repeticiones
nrep = 1000

test_size = 0.5

balanced=False

# crea una lista para guardar el valor mínimo de precisión para el método del vector lambda
min_precisiones = []
# crea una lista para guardar el valor mínimo de precisión para el método del valor de la función objetivo
min_precisiones_fun = []

# crea una lista para guardar el valor máximo de precisión para el método del vector lambda
max_precisiones = []
# crea una lista para guardar el valor máximo de precisión para el método del valor de la función objetivo
max_precisiones_fun = []

# crea una lista para guardar el valor medio de precisión para el método del vector lambda
mean_precisiones = []
# crea una lista para guardar el valor medio de precisión para el método del valor de la función objetivo
mean_precisiones_fun = []

num_classes = len(np.unique(dataset.target))

#KRIGGING

# define una función para ejecutar en el proceso
def proc(alph):

    # separa los datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(dataset.data, dataset.target, test_size=test_size)#, random_state=42

    # si balanced es True, balancea los datos de entrenamiento
    if balanced:
        #obtiene el número de muestras de cada clase en los datos de entrenamiento
        ntrain = np.zeros(num_classes)
        for i in range(num_classes):
            ntrain[i] = np.where(y_train == i)[0].shape[0]
        # calcula el número de muestras de la clase minoritaria
        nmin = int(np.min(ntrain))
        # por cada clase
        for i in range(num_classes):
            # si el número de muestras de la clase i es mayor que nmin
            if ntrain[i] > nmin:
                #selecciona ntrain[i] - nmin muestras de la clase i para eliminar
                idx = np.random.choice(np.where(y_train == i)[0], int(ntrain[i] - nmin), replace=False)
                # elimina las muestras seleccionadas
                X_train = np.delete(X_train, idx, axis=0)
                y_train = np.delete(y_train, idx, axis=0)


    # método del vector lambda
    # marca el tiempo de inicio
    start_time = time.time()
    # crea un clasificador de krigging
    kr_lambda = isl.KriggingClassifier(X_train.T, alph, y_train)
    # kr_lambda.minTraining()
    # crea un vector de predicciones
    y_pred_lambda_ts = np.zeros(X_test.shape[0])

    # para cada muestra de test
    for i in range(X_test.shape[0]):
        # aplica el clasificador
        y_pred_lambda = kr_lambda.lambda_classifier(X_test[i])
        y_pred_lambda_ts[i] = y_pred_lambda


    # inicializa la matriz de confusión
    conf = np.zeros([num_classes, num_classes+1])

    # calcula la matriz de confusión
    for i in range(y_test.shape[0]):
        conf[int(y_test[i]), int(y_pred_lambda_ts[i])] += 1

    # calcula la precisión
    acc = np.sum(np.diag(conf))/np.sum(conf)



    # método del valor de la función objetivo
    # crea un clasificador de krigging
    kr_fun = isl.KriggingFunctionClassifier(X_train.T, alph, y_train)
    # crea un vector de predicciones
    y_pred_fun_ts = np.zeros(X_test.shape[0])

    # para cada muestra de test
    for i in range(X_test.shape[0]):
        # aplica el clasificador
        y_pred_fun = kr_fun.fun_classifier(X_test[i])
        y_pred_fun_ts[i] = y_pred_fun

    # crea otra matriz de confusión para el método del valor de la función objetivo
    conf_fun = np.zeros([num_classes, num_classes+1])

    # calcula la matriz de confusión
    for i in range(y_test.shape[0]):
        conf_fun[int(y_test[i]), int(y_pred_fun_ts[i])] += 1
    # print('Matriz de confusión: \n', conf_fun)

    # calcula la precisión
    acc_fun = np.sum(np.diag(conf_fun))/np.sum(conf_fun)
    # print('Precisión: ', acc_fun)

    # # calcula el valor mínimo de precisión para el método del vector lambda
    # min_precisiones.append(np.min(precisiones))
    # # calcula el valor mínimo de precisión para el método del valor de la función objetivo
    # min_precisiones_fun.append(np.min(precisiones_fun))

    # # calcula el valor máximo de precisión para el método del vector lambda
    # max_precisiones.append(np.max(precisiones))
    # # calcula el valor máximo de precisión para el método del valor de la función objetivo
    # max_precisiones_fun.append(np.max(precisiones_fun))

    # # calcula el valor medio de precisión para el método del vector lambda
    # mean_precisiones.append(np.mean(precisiones))
    # # calcula el valor medio de precisión para el método del valor de la función objetivo
    # mean_precisiones_fun.append(np.mean(precisiones_fun))

    # devuelve el valor minimo, medio y maximo para cada método
    return (acc, acc_fun)

#proceso main
if __name__ == '__main__':
    print(alphas)

    precisiones = np.zeros(nrep)

    #crea otra lista para probar el método del valor de la función objetivo
    precisiones_fun = np.zeros(nrep)

    # crea una lista para guardar los tiempos de ejecución del clasificador lambda
    tiempos_lambda = []
    # crea una lista para guardar los tiempos de ejecución del clasificador función objetivo
    tiempos_fun = []
    #crea un pool de procesos
    pool = mp.Pool(mp.cpu_count())
    #ejecuta el proceso 100 veces para cada valor de alpha
    for alph in alphas:
        print(alph)
        # crea una lista con el valor alpha repetido nrep veces
        alpharep = [alph]*nrep
        #ejecuta el nrep veces
        results = list(tqdm.tqdm(pool.imap(proc, alpharep), total=nrep))
        #guarda los resultados en la lista de precisiones
        (precisiones,precisiones_fun) = zip(*results)
        # calcula el valor mínimo de precisión para el método del vector lambda
        min_precisiones.append(np.min(precisiones))
        # calcula el valor mínimo de precisión para el método del valor de la función objetivo
        min_precisiones_fun.append(np.min(precisiones_fun))
        # calcula el valor máximo de precisión para el método del vector lambda
        max_precisiones.append(np.max(precisiones))
        # calcula el valor máximo de precisión para el método del valor de la función objetivo
        max_precisiones_fun.append(np.max(precisiones_fun))
        # calcula el valor medio de precisión para el método del vector lambda
        mean_precisiones.append(np.mean(precisiones))
        # calcula el valor medio de precisión para el método del valor de la función objetivo
        mean_precisiones_fun.append(np.mean(precisiones_fun))


    #grafica los resultados
    plt.figure()
    #grafica el valor medio de precisión para el método del vector lambda
    plt.plot(alphas, mean_precisiones, 'b', label='lambda')
    #grafica el valor medio de precisión para el método del valor de la función objetivo
    plt.plot(alphas, mean_precisiones_fun, 'r', label='fun')
    plt.xlabel('alpha')
    plt.ylabel('accuracy')
    plt.legend()
    #añade el valor mínimo de precisión para el método del vector lambda
    plt.plot(alphas, min_precisiones, 'b--')
    #añade el valor mínimo de precisión para el método del valor de la función objetivo
    plt.plot(alphas, min_precisiones_fun, 'r--')
    #añade el valor máximo de precisión para el método del vector lambda
    plt.plot(alphas, max_precisiones, 'b--')
    #añade el valor máximo de precisión para el método del valor de la función objetivo
    plt.plot(alphas, max_precisiones_fun, 'r--')

    plt.show()