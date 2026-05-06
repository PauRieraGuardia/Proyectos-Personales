# Vamos a realizar un ejercicio en función de lo que hemos aprendido has ahora

# Enunciado: Crear una clase estudiante que tenga los atributos nombre, edad y Grado. Además hay que agregar un método llamado estudiar() que imprima 
# "el estudiante (nombre) está estudiando". Crear un objeto Estudiante y usar el método estudiar().

class Estudiante():
    def __init__(self, nombre, edad, grado):
        self.nombre = nombre
        self.edad = edad
        self.grado = grado 

    def estudiar(self):
        print(f"El estudiante {self.nombre} está estudiando ")

nombre = input("Digame su nombre: ")
edad = input("Digame su edad: ")
grado = input("Digame su grado: ")

Estudiante = Estudiante(nombre,edad,grado).estudiar()
