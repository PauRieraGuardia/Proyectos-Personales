# Clases abstractas, es una clase que no podemos instanciar pero es como una plantilla para crear determinadas clases.
# Las Clases abstractas son, esencialmente, "esqueletos" o "plantillas" de clases. Su objetivo principal no es crear objetos, sino definir un contrato que todas sus clases hijas deben seguir obligatoriamente.

from abc import ABC, abstractmethod 

# Método abstracto, método declarado en la plantilla pero que no tiene ningúna implementación

# Creamos una plantilla para crear personas
class Persona(ABC): # Heredando de ABC al crear nuestra clase estamos creando una clase abstracta
    @abstractmethod # Aplicamos el decorador abstractclassmethod para determinar un método como abstracto
    def __init__(self, nombre, edad,sexo,actividad):
        self.nombre = nombre
        self.edad = edad
        self.sexo = sexo
        self.actividad = actividad

    @abstractmethod # otro método abstracto
    def hacer_actividad(self):
        pass

    def presentarse(self): # Un método genérico de la clase
        print(f"Hola, me llamo: {self.nombre} y tengo {self.edad} años")


class Estudiante(Persona):  # Creación de class que hereda de la clase abstracta Persona
    def __init__(self,nombre,edad,sexo,actividad):
        super().__init__(nombre,edad,sexo,actividad)

    def hacer_actividad(self):
        print(f"Estoy estudiando:{self.actividad}")

class Trabajador(Persona):  # Creación de class que hereda de la clase abstracta Persona
    def __init__(self,nombre,edad,sexo,actividad):
        super().__init__(nombre,edad,sexo,actividad)

    def hacer_actividad(self):
        print(f"Actualmente estoy trabajando como: {self.actividad}")

pedrito = Estudiante("Pedrito",25,"Masculino","Programación")
pau = Trabajador("Pau",26,"Masculino","Economista")

pedrito.presentarse()
pedrito.hacer_actividad()
pau.presentarse()
pau.hacer_actividad()
