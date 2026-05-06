# Abstracción, administrar la complejidad ocultando todos los detalles inecesarios al programador o al usuario y dandole solo las funcionalidades relevantes.
# Es decir, simplificar la realidad
# Básicamente se trata de agrupar y ordenar por clases las distintas funciones para simplificar al usuario el uso de las clases. Lo mismo que se hace con las librerias

class Auto():
    def __init__(self):
        self._estado = "apagado"

    def encender(self):
        self._estado = "encendido"
        print("El auto está encendido")
    
    def conducir(self):
        if self._estado == "apagado":
            self.encender()
        print("Conduciendo el auto")

mi_auto = Auto()

mi_auto.conducir()



