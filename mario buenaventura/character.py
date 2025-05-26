import pygame
from constants import * # Importa todas las constantes

class Personaje:
    def __init__(self, id, nombre, x, y, estado="Vivo"):
        self.id = id
        self.nombre = nombre
        self.posicionX = x
        self.posicionY = y
        self.estado = estado
        self.image = None # La imagen actualmente escalada y lista para dibujar
        self.rect = pygame.Rect(x, y, 1, 1) # Rect inicial, se ajustará al cargar la imagen
        self.grounded = True # True si el personaje está en el suelo
        self.velocidadY = 0 # Agregamos velocidadY para la gravedad

    def mover(self, dx=0, dy=0):
        self.posicionX += dx
        self.posicionY += dy
        if self.rect:
            self.rect.x = self.posicionX
            self.rect.y = self.posicionY
            
    def set_image(self, image_surface, target_size=None, flip_x=False):
        """
        Asigna una imagen al personaje, la escala y opcionalmente la voltea.
        Ajusta el rect manteniendo la parte inferior del personaje en la misma posición Y.
        :param image_surface: La superficie de Pygame de la imagen original.
        :param target_size: Una tupla (ancho, alto) para escalar la imagen. Si es None, no se escala.
        :param flip_x: Booleano, si True, la imagen se voltea horizontalmente.
        """
        # Si el rect aún no se ha inicializado correctamente (e.g., al inicio del juego)
        # usamos self.posicionY como referencia.
        old_rect_bottom = self.rect.bottom if self.rect and self.rect.height > 1 else self.posicionY

        if target_size:
            scaled_image = pygame.transform.scale(image_surface, target_size)
        else:
            scaled_image = image_surface # Si no se especifica tamaño, usa la imagen tal cual

        if flip_x:
            self.image = pygame.transform.flip(scaled_image, True, False)
        else:
            self.image = scaled_image
        
        # Crear un nuevo rect y ajustarlo para que la parte inferior esté donde estaba antes
        new_rect = self.image.get_rect()
        new_rect.x = self.posicionX
        new_rect.bottom = old_rect_bottom # Mantiene la base del personaje en su lugar
        
        self.rect = new_rect
        self.posicionY = self.rect.y # Sincroniza posicionY con la nueva posición del rect

    def aplicar_gravedad(self):
        # Esta función es específica de personajes que pueden caer.
        if not self.grounded:
            self.velocidadY += GRAVITY # Usa la constante GRAVITY
            self.mover(dy=self.velocidadY)
            
            # Comprueba si ha tocado el suelo
            floor_y_for_char_bottom = SCREEN_HEIGHT - GROUND_LEVEL_OFFSET
            if self.rect.bottom >= floor_y_for_char_bottom:
                self.rect.bottom = floor_y_for_char_bottom
                self.posicionY = self.rect.y
                self.velocidadY = 0
                self.grounded = True
                self.is_jumping = False # Asegurarse de que el estado de salto se reinicie al tocar el suelo


class Enemigo(Personaje):
    def __init__(self, id, nombre, x, y, velocidad_x, estado="Vivo"):
        super().__init__(id, nombre, x, y, estado)
        self.velocidad_x = velocidad_x
        self.grounded = False 

    def update(self):
        self.mover(dx=self.velocidad_x)
        self.aplicar_gravedad() 


class Goomba(Enemigo):
    def __init__(self, id, x, y, velocidad_x=-GOOMBA_SPEED):
        super().__init__(id, "Goomba", x, y, velocidad_x, "Vivo")
        self.rect = pygame.Rect(x, y, GOOMBA_SIZE[0], GOOMBA_SIZE[1])


class Jugador(Personaje):
    def __init__(self, id, nombre, x, y):
        super().__init__(id, nombre, x, y, "Vivo")
        self.is_ducking = False
        self.vidas = 3
        self.monedas = 0
        self.puntos = 0
        self.tiempo = 300 
        self.dispara = False 
        self.direccion = "right" 
        self.tamaño = "normal" # Este valor se usará para determinar el tamaño objetivo
        self.inmune = False
        self.inmunidad_timer = None 
        self.is_jumping = False
        self.jump_key_held = False 
        self.is_running = False
        self.is_moving = False 

        # Estado de animación
        self.current_frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()

        # Almacenamiento de imágenes: ahora solo un set "base" de imágenes de Mario normal
        self.images = {
            "idle_right": None,
            "idle_left": None,
            "run_right": [],
            "run_left": [],
            "jump_right": None, 
            "jump_left": None,  
            "duck": None 
        }
        
    def load_player_images(self, imgs_dict):
        """
        Carga y prepara todas las imágenes base de Mario (normal).
        El escalado a "grande" se hará en set_current_animation_frame.
        """
        self.images["idle_right"] = imgs_dict["mario_normal"]
        self.images["idle_left"] = imgs_dict.get("mario_normal_izquierda", pygame.transform.flip(imgs_dict["mario_normal"], True, False))

        # Puedes decidir si quieres una animación de correr más compleja o simplemente dos frames
        self.images["run_right"].append(imgs_dict["mario_normal"]) 
        self.images["run_right"].append(imgs_dict["mario_corriendo_derecha_1"])

        self.images["run_left"].append(imgs_dict.get("mario_normal_izquierda", pygame.transform.flip(imgs_dict["mario_normal"], True, False))) 
        self.images["run_left"].append(imgs_dict["mario_corriendo_izquierda_1"])
        
        # Para la pose de salto, usamos la imagen "idle" por simplicidad.
        self.images["jump_right"] = imgs_dict["mario_normal"]
        self.images["jump_left"] = imgs_dict.get("mario_normal_izquierda", pygame.transform.flip(imgs_dict["mario_normal"], True, False))

        self.images["duck"] = imgs_dict["mario_agachado"] 

        self.set_current_animation_frame()


    def set_current_animation_frame(self):
        """Determina y establece la imagen actual de Mario basándose en su estado y tamaño."""
        current_time = pygame.time.get_ticks()
        
        # Determinar el tamaño objetivo según el atributo self.tamaño
        if self.tamaño == "normal":
            target_size = PLAYER_NORMAL_SIZE
            target_duck_size = PLAYER_DUCK_SIZE
        elif self.tamaño == "grande":
            target_size = PLAYER_BIG_SIZE
            # Ajustar el tamaño de agacharse para Mario Grande si es diferente
            # Aquí, asumimos que se agacha a un tamaño similar al normal agachado,
            # pero puedes definir PLAYER_BIG_DUCK_SIZE si lo necesitas.
            target_duck_size = (PLAYER_BIG_SIZE[0], PLAYER_BIG_SIZE[1] * 0.7) # Ejemplo: 70% de la altura de Mario grande
        else:
            target_size = PLAYER_NORMAL_SIZE # Default
            target_duck_size = PLAYER_DUCK_SIZE


        # Guardar la parte inferior del rect antes de cualquier cambio para mantenerla
        old_rect_bottom = self.rect.bottom

        # 1. Lógica para agacharse (tiene prioridad)
        if self.is_ducking:
            # Usar la imagen de agacharse y escalarla al tamaño de pato correspondiente
            self.set_image(self.images["duck"], target_duck_size, flip_x=(self.direccion == "left"))
            self.rect.bottom = SCREEN_HEIGHT - GROUND_LEVEL_OFFSET # Asegurar que esté en el suelo
            self.posicionY = self.rect.y
            return 

        # 2. Lógica para salto/caída (tiene prioridad sobre correr/quieto si no está agachado)
        if not self.grounded: 
            if self.direccion == "right":
                self.set_image(self.images["jump_right"], target_size) # Usar la imagen de salto y escalarla
            else:
                self.set_image(self.images["jump_left"], target_size)  # Usar la imagen de salto y escalarla
            self.rect.topleft = (self.posicionX, self.posicionY)
            return 

        # 3. Lógica para correr/movimiento (solo si no está agachado o saltando/cayendo)
        if self.is_moving:
            if current_time - self.last_frame_update > PLAYER_RUN_ANIMATION_SPEED:
                self.current_frame_index = (self.current_frame_index + 1) % len(self.images["run_right"])
                self.last_frame_update = current_time

            if self.direccion == "right":
                self.set_image(self.images["run_right"][self.current_frame_index], target_size) # Escalar la imagen de correr
            else:
                self.set_image(self.images["run_left"][self.current_frame_index], target_size)  # Escalar la imagen de correr
        else: # Quieto
            self.current_frame_index = 0 
            if self.direccion == "right":
                self.set_image(self.images["idle_right"], target_size) # Escalar la imagen de quieto
            else:
                self.set_image(self.images["idle_left"], target_size)  # Escalar la imagen de quieto
                
        # Asegurarse de que la parte inferior del jugador esté siempre en el suelo si está grounded
        if self.grounded:
            self.rect.bottom = SCREEN_HEIGHT - GROUND_LEVEL_OFFSET
            self.posicionY = self.rect.y


    def try_jump(self):
        """
        Intenta iniciar un salto o añadir un impulso si ya está en el aire.
        Permite múltiples "saltos" si se presiona el botón.
        """
        if self.grounded:
            self.is_jumping = True
            self.grounded = False
            self.jump_key_held = True 
            self.velocidadY = -JUMP_STRENGTH_MIN 
            self.set_current_animation_frame() 
        elif self.velocidadY > 0: # Si está cayendo (velocidadY positiva)
            self.velocidadY = -JUMP_STRENGTH_MIN * JUMP_AIR_IMPULSE_FACTOR 
            self.is_jumping = True
            self.jump_key_held = True
            self.set_current_animation_frame()
        elif self.velocidadY < 0 and self.jump_key_held: 
            pass


    def end_jump_key(self):
        """
        Finaliza la fase de "mantener presionado" el salto.
        """
        self.jump_key_held = False
        if self.velocidadY < 0:
            self.velocidadY *= JUMP_CUT_FACTOR 

    def update_jump_height(self):
        """
        Actualiza la altura del salto basándose en si la tecla de salto está siendo mantenida.
        """
        if self.is_jumping and self.jump_key_held and self.velocidadY < 0:
            self.velocidadY += JUMP_ACCELERATION_FACTOR 
            self.velocidadY = max(self.velocidadY, -JUMP_STRENGTH_MAX) 
        
    def update(self):
        self.update_jump_height()