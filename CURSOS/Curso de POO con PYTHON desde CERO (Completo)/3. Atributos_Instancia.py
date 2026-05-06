# Los atributos son variables que pertenence a una clase

# ATRIBUTOS DE INSTANCIA, definidos cuando instanciamos una clase, es decir, creamos un objeto
# Para la creación de atributos de instancia es necesario la función __init__

class Celular:
    # self sirve para hacer referencia al mismo objeto que crearemos al instanciar la clase, en __init__ debemos llamar los atributos que queremos que tenga el objeto
    def __init__(self,marca, modelo, camara): # La función __init__ es una función que se ejecuta directamente, de ahi que necesitemos self. Se llama FUNCIÓN CONSTRUCTORA
        self.marca = marca
        self.modelo = modelo
        self.camara = camara # Definimos los atributos del objeto


celular1 = Celular("Samsung","S23","48MP") # Creamos el objeto mediante la instancia de la class con atributos de Instancia
celular2 = Celular("Apple","Iphone 15 pro","96MP") 

print(celular2.modelo)

