# Ejercicio de herencia múltiple y MRO

# Imagina que estás modelando aniamles en un zoológico. Crear tres clases: "Animal", "Mamifero" y "Ave". La clase "Animal" debe tener un método llamado "comer".
# La clase "Mamifero" debe tener un método llamad "amamantar" y la clase "Ave" un método llamado "volar"
# Ahora, crea una clase "Murcielago" que herede de "Mamifero" y "Ave", en este orde, y por lo tanto debe ser capaz de "amamantar" y "volar", además de "comer".

# Finalmente, juega con el orden de herencia de la clase "Murcielago" y observa cómo cambia el MRO y el comportamiento de los métodos al usar super()

class Animal:
    def comer(self):
        print("El animal esta comiendo")
        
class Mamifero(Animal):
    def amamantar(self):
        print("El animal esta amamantando")

class Ave(Animal):
    def volar(self):
        print("El animal esta volando")

class Murcielago(Mamifero,Ave):
    pass # Sirve para que la clase no tenga ningúna "utilidad", más que para ser conectada con las otras clases


murcielago = Murcielago()

murcielago.amamantar()
murcielago.comer()
murcielago.volar()

print(Murcielago.mro())