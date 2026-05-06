
# HERENCIA MÚLTIPLE

# 1. SUPERCLASE 1
class Persona:
    def __init__(self,nombre,edad,nacionaldad):
        self.nombre = nombre
        self.edad = edad
        self.nacionalidad = nacionaldad

    def hablar(self):
        print("Hola, estoy hablando un poco")

# 2. SUPERCLASE 2
class Artista: 
    def __init__(self, habilidad):
        self.habilidad = habilidad
    
    def mostrar_habilidad(self):
        return f"Mi habilidad es {self.habilidad}"

# 3.  HERENCIA MÚLTIPLE
class EmpleadoArtista(Persona, Artista):
    def __init__(self, nombre,edad,nacionaldad, habilidad, salario, empresa):
        Persona.__init__(self,nombre,edad,nacionaldad) # En vez de super, debemos indicar el nombre de la class que queremos heredar los atributos
        Artista.__init__(self, habilidad) # En vez de super, debemos indicar el nombre de la class que queremos heredar los atributos
        self.salario= salario 
        self.empresa= empresa

    def mostrar_habilidad(self):
        print("no tengo")
        
    def presentarse(self):
        return f"{super().mostrar_habilidad()}" # Con super(), accedemos siempre a la clase padre donde corresponde ese método siguiendo el orden MRO
    
    # def presentarse(self):
    #     return f"{self.mostrar_habilidad()} # Si pusiearmos self nos llamaría el método de la misma clase en la que nos encontramos

# Como saber si una clase es una subclase de otra clase.

herencia = issubclass(EmpleadoArtista,Artista) # issubclase nos mostrara un resultado Booleano
print(herencia)
    
# También, podemos saber si un objeto es instancia de una clase

roberto = EmpleadoArtista("Roberto",26,"argentina","Cantar",7000,"Google") # Creamos un nuevo objeto usando la clase con herencia múltiple

instancia = isinstance(roberto,EmpleadoArtista)
print(instancia)

