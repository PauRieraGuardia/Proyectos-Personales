# Ejercicio de herencia y uso de super:

# Crear un sistema para una escuela. En este sistema, vamos a tener dos clases principales: Persona y Estudiante. 
# La clase Persona tendrá los atributos de nombre y edad y un método que imprima el nombre y la edad de la persona.
# La clase Estudiante heredará de la clase Persona y también tendrá un atributo adicional: grado y un método que imprima el grado del estudiante.

# Deberás utilizar super en el método de inicialización (init) para reutilizar el código de la clase padre (Persona). Luego crea una instancia de la clase Estudiante e
# Imprime sus atributos y utiliza sus métodos para asegurarte de que todo funciona correctamente.

class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad
    def mostrar_datos(self):
        print(f"El nombre de la persona es {self.nombre} y la edad {self.edad}")

class Estudiante (Persona):
    def __init__(self,nombre,edad,grado):
        super().__init__(nombre,edad) # Para la funcion super(). no debemos pasar el parámetro self
        self.grado=grado
    
    def mostrar_grado(self):
        print(f"El grado del estudiante es {self.grado}")

estudiante = Estudiante("Pau",26,"Economía")

estudiante.mostrar_datos()
estudiante.mostrar_grado()