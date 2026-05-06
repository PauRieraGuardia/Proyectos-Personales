# El Decorador Propery es la forma "oficial" y más elegante de Python para implementar Getters sin que parezcan métodos.
# Su función principal es permitirte acceder a un método como si fuera un atributo normal, pero manteniendo todas las ventajas de una función
# Nos pertime definir GETTES, SETTERS y DELETERS
# Esto sirve sobretodo para establecer nombres a determinadas variables y que estos no se cambien en el momento que otro usuario utiliceeste script. basicamente bloqueamos determiando código

class Persona:
    def __init__(self, nombre, edad):
        self.__nombre = nombre
        self._edad = edad
    
    @property # Decorador que define como GETTER, lo usamos como una propiedad. Deja de ser una función y pasa a ser una propeidad
    def nombre(self): # Convertimso la función en el nombre del artributo
        return self.__nombre
    
    @nombre.setter # Definición del SETTER para el atributo que queremos modificar
    def nombre(self,new_nombre):
        self.__nombre = new_nombre

    @nombre.deleter # Definición del DELETER para el atributo que queremos eliminar
    def nombre(self):
        del self.__nombre


pau = Persona("Pau",26) # creación del objeto

nombre = pau.nombre # Podemos usar el nombre como propiedad aun que este en formato privado
print(nombre)

pau.nombre = "Pepe" # Saltará un error siempre y cuando no tengamos setter. si tenemos un setter, como es este caso, se actualiazrá el nombre
print(pau.nombre)

del pau.nombre # Eliminará la modificación anterior 
print(nombre)