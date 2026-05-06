# Métodos Especiales

class Persona:
    def __init__(self,nombre,edad): # Primer método especial, creación del objeto y asignación de atributos del objeto
        self.nombre = nombre
        self.edad = edad 

    def __str__(self): # Método para determinar como debo mostrar en el terminal el objeto cuando solo llamo al objeto
        return f'Persona(nombre={self.nombre},edad={self.edad})' # Este es el formato con el que se mostrará
    
    def __repr__(self):# Método especial de representación
        return f'Persona("{self.nombre}",{self.edad})'
    
    def __add__(self,otro): # Método de agregación (suma), definir que pasa con los objetos cuando los sumamos. Sobrecarga de operadores
        nuevo_valor = self.edad + otro.edad
        return Persona(self.nombre+otro.nombre,nuevo_valor)

pau = Persona("Pau",26)
repre = repr(pau)
resultado = eval(repre)

print(pau)
print(repre)
print(resultado)

pedro = Persona("Pedro",25)

resultado_1 = pau + pedro

print(resultado_1)
