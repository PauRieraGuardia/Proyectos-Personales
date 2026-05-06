# Un decorador es una función que envuelve a otra función para añadirle una funcionalidad extra sin modificar su código original.

def decorador(funcion): # Creación función decoradora que nos pide como parametro una función
    def funcion_modificada():
        print("Antes de llamar a la función") # Aplicamos las distintas modificaciones
        funcion() # Añadimos la funcion 
        print("Después de llamar a la función") # Aplicamos las distintas modificaciones
    return funcion_modificada

# def saludo():
#     print("Hola Mundo")
          
# saludo_modificado = decorador(saludo) # Aplicamos a la función decorador la función saludo
# saludo_modificado()

@decorador # Llamamos a la función decoradora mediante un @ para que, a la nueva función que vamos a definir, aplique las modificaciones existenes, en esta caso los dos prints
def saludo(): # Definimos la nueva función 
    print("Hola Pau como andas") # Se trata de un print

saludo() # Nos tendrá que devolver la función definida, es decir el print así como lo definidos en la función decoradora, los prints antes y después

