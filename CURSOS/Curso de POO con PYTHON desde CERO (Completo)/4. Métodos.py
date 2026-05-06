# Los métodos son la acciones que pueden hacer los objetos dentro de las clases
# Son funciones, todas las funciones que creamos dentro de una clase se llamaran métodos

class Celular:
    def __init__(self,marca, modelo, camara): 
        self.marca = marca
        self.modelo = modelo
        self.camara = camara 

    def llamar(self): # A los métodos debemos pasarle el parámetro self para que pueda ser llamado como objeto.
        print(f"Estas haciendo un llamado desde un: {self.modelo}") # Método 1 

    def cortar(self):
        print(f"Cortaste la llamada desde tu {self.modelo}") # Método 2


celular1 = Celular("Samsung","S23","48MP") 
celular2 = Celular("Apple","Iphone 15 pro","96MP") 

celular2.llamar() # Llamamos el método llamar() desde el objeto celular2 





