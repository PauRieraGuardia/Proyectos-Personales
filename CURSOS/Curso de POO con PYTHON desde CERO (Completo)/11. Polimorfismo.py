# El Polimorfismo es la capacidad de que diferentes objetos respondan al mismo mensaje (o método) de maneras distintas.
# Es hacer que cuando nosotros le damos un método a un objeto se comporte diferente en función de sus propiedades

# 1. POLIMORFISMO DE INCLUSIÓN O "Duck Typing", el que usamos por defecto en python
class Gato():
    def sonido(self):
        return "Miau"
    
class Perro():
    def sonido(self):
        return "Guau"

gato = Gato() # Creación objeto tipo Gato()
perro = Perro() # Creación objeto tipo Perro()

print(gato.sonido())
print(perro.sonido()) # Aplicamos el mismo método, pero muestra otro resultado dependiendo del objeto creado. Esto es el polimorfismo


# 2. POLIMORFISMO DE FUNCIÓN
def hacer_sonido(animal): 
    print(animal.sonido())

hacer_sonido(gato)

# 3. POLIMORFISMO DE HERENCIA, no es necesraio en python, ahora bien, en otros lenguajes si es necesario
# Puesto que Python es de tipado dinámico, no es necesario.

class Animal():
    def sonido(self):
        pass

class Gato(Animal):
    def sonido(self):
        return "Miau"
    
class Perro():
    def sonido(self):
        return "Guau"
    

    
