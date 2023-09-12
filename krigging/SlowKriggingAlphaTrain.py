import time
import sklearn.datasets as skdata
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
import scipy.optimize as opt


# # carga el dataset de iris de sklearn
# dataset = skdata.load_iris()
# carga el dataset de dígitos de sklearn
dataset = skdata.load_digits()
# # carga el dataset de cancer de sklearn
# dataset = skdata.load_breast_cancer()
# # carga el dataset de vinos de sklearn
# dataset = skdata.load_wine()

#guarda el tiempo de inicio
start_time = time.time()

# separa los datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(dataset.data, dataset.target, test_size=0.66, random_state=42)

#KRIGGING
# Define la función a minimizar
def fun(A,alph):
    return np.dot(A,A.T)+alph*np.sum(np.abs(A))

# Define las constraints
def const(a,X_train,x):
    # amplia la matriz X_train con una columna de unos y la transpone
    X_train_ext = np.hstack([X_train, np.ones([X_train.shape[0], 1])]).T
    # amplia el vector x con un 1
    x_ext = np.hstack([x, 1])
    # calcula el vector XA-x
    XA_x = np.dot(X_train_ext, a) - x_ext
    # devuelve XA-x
    return XA_x

#crea una lista de valores de alpha
alphas = np.arange(0,1,0.1)

#crea una lista para guardar la precisión en entrenamiento
acctr = np.zeros(alphas.shape)

#crea una lista para guardar la precisión en prueba
accts = np.zeros(alphas.shape)

# selecciona el valor alpha para krigging asignando valores de 0 a 1 con un paso de 0.1
for alph in alphas:

    # marca el tiempo de inicio de la iteración
    start_time_iter = time.time()
        
    # PREDICCION KRIGGING
    # Sobre entrenamiento

    # Crea un array de predicciones vacío
    y_train_pred = np.zeros(y_train.shape)

    # Obtiene las clases únicas
    classes = np.unique(y_train)
    # Obtiene el número de clases
    num_classes = classes.shape[0]

    # Crea un array de scores vacío
    scores_train = np.zeros([num_classes, X_train.shape[0]])

    # crea una matriz de numpy de datos ampliada con una columna de unos y la transpone
    X_train_ext = np.hstack([X_train, np.ones([X_train.shape[0], 1])]).T
    # calcula la pseudo-inversa
    X_train_pinv = np.linalg.pinv(X_train_ext)


    # Para cada dato de entrenamiento original
    for i in range(X_train.shape[0]):
        # Extrae el vector de características del dato de entrenamiento i
        x_i = X_train[i]

        # Crea un vector de características ampliado con un 1
        x_i_ext = np.hstack([X_train[i], 1])
        # Multiplica el vector de características ampliado por la pseudo-inversa para obtener el vector lambda de partida
        #lambda_i = np.dot(X_train_pinv, x_i_ext)
        #crea un lambda inicial de ceros
        lambda_i = np.zeros(X_train_pinv.shape[0])
        
        #calcula el vector lambda que minimiza la función fun sujeto a las constraints const
        opt_res=opt.minimize(fun, lambda_i, args=(alph), constraints={'fun': const, 'type': 'eq', 'args': (X_train, x_i)}, tol=1e-6, method='trust-constr',options={'disp': True})
        lambda_i = opt_res.x


        # Para cada clase
        for j in range(num_classes):
            # Obtiene los índices correspondientes a la clase j en el conjunto de entrenamiento
            idx = np.where(y_train==classes[j])

            # Obtiene el score de la clase j para el dato de entrenamiento i sumando los lambdas de los datos de la clase j
            scores_train[j, i] = np.sum(lambda_i[idx])

        # guarda la clase con mayor score para el dato de entrenamiento i en el array de predicciones
        y_train_pred[i] = np.argmax(scores_train[:, i])

    # calcula la precisión del modelo sobre el conjunto de entrenamiento
    acc = np.sum(y_train_pred==y_train)/y_train.shape[0]

    # guarda la precisión en la lista de precisión en entrenamiento
    acctr[alphas==alph] = acc

    # marca el tiempo de fin de entrenamiento
    end_time_tr = time.time()

    print('alpha: ', alph)
    print('suma de lambdas: ', np.sum(lambda_i))
    print(acc)
    print('tiempo de entrenamiento: ', end_time_tr-start_time_iter)
    # Sobre prueba

    # marca el tiempo de inicio de prueba
    start_time_ts = time.time()

    # Crea un array de predicciones vacío
    y_test_pred = np.zeros(y_test.shape)

    # Obtiene las clases únicas
    classes = np.unique(y_train)
    # Obtiene el número de clases
    num_classes = classes.shape[0]

    # Crea un array de scores vacío
    scores_test = np.zeros([num_classes, X_test.shape[0]])

    # Para cada dato de prueba
    for i in range(X_test.shape[0]):
        # Extrae el vector de características del dato de prueba i
        x_i = X_test[i]

        # Crea un vector de características ampliado con un 1
        x_i_ext = np.hstack([X_test[i], 1])
        # Multiplica el vector de características ampliado por la pseudo-inversa para obtener el vector lambda de partida
        lambda_i = np.dot(X_train_pinv, x_i_ext)

        #calcula el vector lambda que minimiza la función fun sujeto a las constraints const
        lambda_i = opt.minimize(fun, lambda_i, args=(alph), constraints={'fun': const, 'type': 'eq', 'args': (X_train, x_i)}, tol=1e-6, method='trust-constr').x

        # Para cada clase
        for j in range(num_classes):
            # Obtiene los índices correspondientes a la clase j en el conjunto de entrenamiento
            idx = np.where(y_train==classes[j])

            # Obtiene el score de la clase j para el dato de prueba i sumando los lambdas de los datos de la clase j
            scores_test[j, i] = np.sum(lambda_i[idx])

        # guarda la clase con mayor score para el dato de prueba i en el array de predicciones
        y_test_pred[i] = np.argmax(scores_test[:, i])

    # calcula la precisión del modelo sobre el conjunto de prueba
    acc = np.sum(y_test_pred==y_test)/y_test.shape[0]

    # guarda la precisión en la lista de precisión en prueba
    accts[alphas==alph] = acc

    # marca el tiempo de fin de prueba
    end_time_ts = time.time()

    print('suma de lambdas: ', np.sum(lambda_i))
    print(acc)
    print('tiempo de prueba: ', end_time_ts-start_time_ts)
    print('tiempo total: ', end_time_ts-start_time_iter)

#plotea la precisión en entrenamiento y en prueba en función de alpha
plt.plot(alphas, acctr, label='Entrenamiento')
plt.plot(alphas, accts, label='Prueba')
plt.xlabel('alpha')
plt.ylabel('Precisión')
plt.legend()
plt.show()