# El MRO (Method Resolution Order) es el método por el cual python busca métodos y atributos en las clases y le da un ordern

# CASO 1
class A:
    def hablar(self):
        print("Hola desde A")

class B(A):
    def hablar(self):
        print("Hola desde B")

class C(A):
    def hablar(self):
        print("Hola desde C")

class D(B,C):
    def hablar(self):
        print("Hola desde D")

d = D()
d.hablar()

# Si vamos aplicando pass a cada función, vamos a ver el orden que sigue el siguiente script
# Primero llamara a D, luego pasara a B y después C, siguiendo el orden (B,C) y, finalmente, A. (D>B>C>A)

# CASO 2

class A:
    def hablar(self):
        print("Hola desde A")

class F:
    def hablar(self):
        print("Hola desde F")

class B(A):
    def hablar(self):
        print("Hola desde B")

class C(F):
    def hablar(self):
        print("Hola desde C")

class D(B,C):
    def hablar(self):
        print("Hola desde D")

d = D()
d.hablar()

# Si vamos aplicando pass a cada función, vamos a ver el orden que sigue el siguiente script
# Vamos a ver que, en este caso, si no encuentra directamente en D, seguira el camino de B, por lo tanto, si no está be irá a buscar A
# En cambio, si va por el "camino" de C, y no encuentra C, irá a buscar a F

# Para saber el orden que tiene el distinto objeto existe el método mro
print(D.mro())

# Si yo quiero llamar directamente una clase, debo mencionar dicha clase mencionado el objeto
B.hablar(d)