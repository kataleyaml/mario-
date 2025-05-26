import pygame
from constants import * # Importa todas las constantes

class Poder:
    def __init__(self, id, nombre, descripcion, x, y, estado="activo"):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.posicionX = x
        self.posicionY = y
        self.estado = estado
        self.image = None
        self.rect = None
        self.original_image = None
        
    def set_image(self, image, size=None):
        self.original_image = image
        if size:
            self.image = pygame.transform.scale(self.original_image, size)
        else:
            self.image = self.original_image
            
        if self.image:
            self.rect = self.image.get_rect()
            self.rect.x = self.posicionX
            self.rect.y = self.posicionY
            
    def update(self):
        self.mover(dx=-OBJECT_SPEED) # Todos los power-ups se mueven hacia la izquierda
        
    def mover(self, dx=0, dy=0):
        self.posicionX += dx
        self.posicionY += dy
        if self.rect:
            self.rect.x = self.posicionX
            self.rect.y = self.posicionY

class Hongo(Poder):
    def __init__(self, id, x, y, tipo, estado="activo"):
        nombre = "Hongo de crecimiento" if tipo == "crecimiento" else "Hongo de vida"
        descripcion = "Hace crecer al jugador" if tipo == "crecimiento" else "Da una vida extra"
        super().__init__(id, nombre, descripcion, x, y, estado)
        self.tipo = tipo

class Moneda(Poder):
    def __init__(self, id, x, y, estado="activa"):
        super().__init__(id, "Moneda", "Otorga puntos y contribuye a una vida extra", x, y, estado)

class Estrella(Poder):
    def __init__(self, id, x, y, estado="activa"):
        super().__init__(id, "Estrella", "Otorga inmunidad temporal", x, y, estado)
