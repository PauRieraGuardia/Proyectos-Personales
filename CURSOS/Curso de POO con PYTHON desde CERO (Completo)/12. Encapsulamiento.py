# El Encapsulamiento es el método para proteger elementos de una clase. Es decir, poner como privado determinadas partes del código

class MiClase:
    def __init__(self):
        self._atributo_protegido = "Valor" # La forma para indicar a python de que creamos un atributo privado es mediante el _ antes del nombre del atributo (_atributo_privado)

objeto = MiClase()
print(objeto._atributo_protegido)  # Intentamos acceder al atributo, y accede, se trata de un atributo protegido

# Ahora bien, si ponemos doble __, se aumenta la seguridad del atributo 
class MiClase:
    def __init__(self):
        self.__atributo_privado = "Valor" # En este caso, saltará un error al correr el código, se trata de un atributo privado

objeto = MiClase()
print(objeto.__atributo_privado) # Para acceder a los atributos privados es necesario usar getters y setters, siguiente script

# Tambíen existen los metodos privados

class MiClase:
    def __init__(self):
        self.__atributo_privado = "Valor"
        def __hablar(self):
            print("hola, como estas") # Método privado __

