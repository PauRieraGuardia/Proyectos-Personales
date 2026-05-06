# Los Getters y Setters son métodos especiales que sirven para controlar cómo se accede y cómo se modifican los atributos de una clase

# Getter: Es un método que lee el valor de un atributo y lo devuelve. Se usa para consultar el dato.
# Setter: Es un método que recibe un valor y lo asigna al atributo. Se usa para cambiar el dato, pero permitiéndote poner reglas (validaciones).


class Persona:
    def __init__(self, nombre, edad):
        self._nombre = nombre
        self._edad = edad

    def get_nombre(self): # GETTER, para activar un getter debemos tener un método dentro de la clase que nos devuelba ese atributo privado
        # El GETTER es un método que accede a un valor de un atributo que debería ser privado
        return self._nombre # Usa el return para mostrar el atributo privado
    
    def set_nombre(self, new_nombre): # SETTER, para establecer el nuevo valor medainte un metodo
        # El SETTER es un método para modificar un valor de un atributo que debería ser privado
        self._nombre = new_nombre # Establece un nuevo atributo privado
    

dalto = Persona("Lucas",21) # Creamos un objeto 
nombre = dalto.get_nombre() # llamamos al método para tener el nombre
print(nombre) # printeamos
    

nombre = dalto.set_nombre("Pepito") # Llamamos el metod set_nombre para establecer el nuevo nombre
print(dalto.get_nombre()) 