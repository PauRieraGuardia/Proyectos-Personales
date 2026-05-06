# Es la capacidad de crear una clase nueva a partir de una clase ya existente
# La Clase Hija hereda automáticamente todas las características (atributos) y comportamientos (métodos) de la Clase Padre, pero además puede tener los suyos propios
# Sirve para reutilizar código constantemente y hacer scripts más simples y limpios


# HERENCIA SIMPLE

# 1. SUPERCLASE
class Persona:
    def __init__(self,nombre,edad,nacionaldad):
        self.nombre = nombre
        self.edad = edad
        self.nacionalidad = nacionaldad

    def hablar(self):
        print("Hola, estoy hablando un poco")

# 2. SUBCLASE
class Empleado(Persona): # Estamos creando una Class Hija que hereda los atributos y los métodos de la clase persona, para heredarlo se indica la clase padre dentro del paréntesis
    def __init__(self,nombre,edad,nacionalidad,trabajo, salario): # Añadimos los atributos de la clase anterior más los atributos nuevos
        super().__init__(nombre,edad,nacionalidad) # La función super sirve para "invocar" a la clase padre. Debemos pasar los atributos del constructor padre.
        self.trabajo = trabajo
        self.salario = salario 

Roberto = Empleado("Roberto",26,"Argentina","Programador",10000) 

print(Roberto.salario)

Roberto.hablar()

# HERENCIA JERÁRQUICA

# 1. SUPERCLASE
class Persona:
    def __init__(self,nombre,edad,nacionaldad):
        self.nombre = nombre
        self.edad = edad
        self.nacionalidad = nacionaldad

    def hablar(self):
        print("Hola, estoy hablando un poco")

# 2. SUBCLASE 1
class Empleado(Persona): 
    def __init__(self,nombre,edad,nacionalidad,trabajo, salario): 
        super().__init__(nombre,edad,nacionalidad) 
        self.trabajo = trabajo
        self.salario = salario 

# 3. SUBCLASE 2
class Estudiante(Persona): 
    def __init__(self,nombre,edad,nacionalidad,notas, universidad): 
        super().__init__(nombre,edad,nacionalidad) 
        self.notas = notas
        self.universidad = universidad 


Roberto = Estudiante("Roberto",26,"Argentina","Programador",10000) 
print(Roberto.salario)
Roberto.hablar()