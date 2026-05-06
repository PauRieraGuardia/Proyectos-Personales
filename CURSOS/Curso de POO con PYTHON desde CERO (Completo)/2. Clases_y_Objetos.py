
# Para la creación de una Clase usamos class, seguidamente le daremos el nombre de la clase
# Snake case es escribir usando _ para el espacio

# Un objeto es una instancia en una clase

class Celular():
    marca = "samsung" # Estamos creando ATRIBUTOS ESTÁTICOS, pork para todos los objetos van a ser iguales 
    modelo = "S23"
    camara = "48MP"

celular1 = Celular() # Instanciar una clase: creamos un objeto mediante la clase, puesto que los atributos son estáticos, serán en todas las variables iguales
celular2 = Celular() 
celular3 = Celular()
celular3 = Celular()

print(celular1.marca) # Podemos acceder a los atributos del objeto creado mediante la instanción de la clase

