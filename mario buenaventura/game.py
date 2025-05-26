import pygame
import random
import os
import sys # Asegúrate de que sys esté importado si lo usas en otro lugar
from pygame.locals import *

from constants import *
from character import Personaje, Enemigo, Goomba, Jugador
from powerup import Poder, Hongo, Moneda, Estrella

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() # Inicializa el módulo de mezcla de sonido
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario en Buenaventura")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 16)

        self.floor_y = SCREEN_HEIGHT - GROUND_LEVEL_OFFSET

        # Cargar imágenes
        self.imgs = {}
        self.load_images()

        # Cargar música de fondo
        # --- CAMBIO IMPORTANTE AQUÍ ---
        # Usa os.path.join para construir la ruta de manera segura
        # y asegúrate de que 'background_music.mp3' sea el nombre real de tu archivo de música.
        self.music_path = os.path.join(os.getcwd(), "assets", "sound", "background_music.mp3") 
        
        # Verifica si el archivo de música existe antes de cargarlo
        if os.path.exists(self.music_path):
            pygame.mixer.music.load(self.music_path)
            # Reproduce la música en bucle (-1 para reproducir indefinidamente)
            pygame.mixer.music.play(-1) 
        else:
            print(f"Advertencia: Archivo de música no encontrado en {self.music_path}. No se reproducirá la música.")
        # --- FIN DEL CAMBIO IMPORTANTE ---

        # Estados del juego
        self.game_running = False
        self.in_menu = True
        self.game_over = False

        # Elementos del juego
        self.players = []
        self.poderes_activos = []
        self.monedas_activas = []
        self.estrella_activa = None
        self.enemigos_activos = []
        self.total_goombas_generados = 0
        self.max_goombas = 2
        self.max_total_goombas = 10
        self.current_player = None

        # Temporizadores
        self.spawn_timer = 0
        self.goomba_timer = 0
        self.immunity_timers = {}

    def load_images(self):
        """Carga todas las imágenes del juego."""
        try:
            for key, path in IMG_PATHS.items():
                full_path = os.path.join(os.getcwd(), path)
                if not os.path.exists(full_path):
                    print(f"Error: Imagen no encontrada en {full_path}. Usando marcador de posición.")
                    if key == "fondo":
                        self.imgs[key] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                        self.imgs[key].fill(SKY_BLUE)
                        pygame.draw.rect(self.imgs[key], BROWN, (0, self.floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - self.floor_y))
                    else:
                        size = (30,30)
                        if "mario_normal" in key or "mario_corriendo" in key or "mario_agachado" in key: size = PLAYER_NORMAL_SIZE
                        elif "goomba" in key: size = GOOMBA_SIZE
                        elif "hongo" in key: size = MUSHROOM_SIZE
                        elif "moneda" in key: size = COIN_SIZE
                        elif "estrella" in key: size = STAR_SIZE

                        placeholder_img = pygame.Surface(size)
                        placeholder_img.fill(RED) 
                        pygame.draw.rect(placeholder_img, BLACK, placeholder_img.get_rect(), 1)
                        self.imgs[key] = placeholder_img
                    continue

                img = pygame.image.load(full_path).convert_alpha()
                if key == "fondo":
                    self.imgs[key] = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                # Las imágenes de Mario no se escalan aquí al cargar, solo se almacenan
                # para ser escaladas dinámicamente por la clase Jugador
                elif key.startswith("mario_"): # Solo para las imágenes de Mario, no las escalamos aquí
                    self.imgs[key] = img
                elif key == "hongo_crecimiento" or key == "hongo_vida":
                    self.imgs[key] = pygame.transform.scale(img, MUSHROOM_SIZE)
                elif key == "moneda":
                    self.imgs[key] = pygame.transform.scale(img, COIN_SIZE)
                elif key == "estrella":
                    self.imgs[key] = pygame.transform.scale(img, STAR_SIZE)
                elif key == "goomba":
                    self.imgs[key] = pygame.transform.scale(img, GOOMBA_SIZE)


        except pygame.error as e:
            print(f"Error al cargar imágenes: {e}")
            # Fallback para imágenes esenciales de Mario
            self.imgs["fondo"] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.imgs["fondo"].fill(SKY_BLUE)
            pygame.draw.rect(self.imgs["fondo"], BROWN, (0, self.floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - self.floor_y))
            
            # Crear marcadores de posición para las imágenes esenciales del jugador
            self.imgs["mario_normal"] = pygame.Surface(PLAYER_NORMAL_SIZE, pygame.SRCALPHA); self.imgs["mario_normal"].fill((0, 255, 0, 128))
            self.imgs["mario_normal_izquierda"] = pygame.transform.flip(self.imgs["mario_normal"], True, False)
            self.imgs["mario_corriendo_derecha_1"] = self.imgs["mario_normal"]
            self.imgs["mario_corriendo_izquierda_1"] = self.imgs["mario_normal_izquierda"]
            self.imgs["mario_agachado"] = pygame.Surface(PLAYER_DUCK_SIZE, pygame.SRCALPHA); self.imgs["mario_agachado"].fill((0, 0, 255, 128))
            
            self.imgs["goomba"] = pygame.Surface(GOOMBA_SIZE, pygame.SRCALPHA); self.imgs["goomba"].fill((128, 0, 128, 128))
            self.imgs["hongo_crecimiento"] = pygame.Surface(MUSHROOM_SIZE, pygame.SRCALPHA); self.imgs["hongo_crecimiento"].fill((255, 0, 255, 128))
            self.imgs["hongo_vida"] = pygame.Surface(MUSHROOM_SIZE, pygame.SRCALPHA); self.imgs["hongo_vida"].fill((0, 255, 255, 128))
            self.imgs["moneda"] = pygame.Surface(COIN_SIZE, pygame.SRCALPHA); self.imgs["moneda"].fill((255, 255, 0, 128))
            self.imgs["estrella"] = pygame.Surface(STAR_SIZE, pygame.SRCALPHA); self.imgs["estrella"].fill((255, 255, 100, 128))


    def start_game(self):
        """Inicia el juego principal."""
        self.players = []
        self.poderes_activos = []
        self.monedas_activas = []
        self.estrella_activa = None
        self.enemigos_activos = []
        self.total_goombas_generados = 0
        self.immunity_timers = {}

        self.in_menu = False
        self.game_running = True
        self.game_over = False

        p1 = Jugador(1, "Mario", SCREEN_WIDTH // 4, self.floor_y - PLAYER_NORMAL_SIZE[1])
        p1.load_player_images(self.imgs) 
        self.players.append(p1)
        self.current_player = p1
        self.current_player.set_current_animation_frame() 

        self.spawn_timer = pygame.time.get_ticks()
        self.goomba_timer = pygame.time.get_ticks()

        # Si la música se detuvo al reiniciar, la vuelves a reproducir
        if pygame.mixer.music.get_busy() == 0:
            if os.path.exists(self.music_path):
                pygame.mixer.music.play(-1) 
            else:
                print(f"Advertencia: Archivo de música no encontrado en {self.music_path} al intentar reiniciar.")

    def spawn_objects(self):
        """Genera objetos (hongos, monedas, estrellas) en el juego."""
        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_timer > random.randint(3000, 7000):
            self.spawn_timer = current_time

            object_type = random.choice(["hongo_crecimiento", "hongo_vida", "moneda", "estrella"])
            x_pos = SCREEN_WIDTH + 50

            if object_type.startswith("hongo"):
                y_pos = self.floor_y - MUSHROOM_SIZE[1] 
                tipo = object_type.split("_")[1]
                hongo = Hongo(len(self.poderes_activos), x_pos, y_pos, tipo)
                hongo.set_image(self.imgs[object_type], MUSHROOM_SIZE)
                self.poderes_activos.append(hongo)
            elif object_type == "moneda":
                y_pos = self.floor_y - random.randint(50, 150) 
                moneda = Moneda(len(self.monedas_activas), x_pos, y_pos)
                moneda.set_image(self.imgs["moneda"], COIN_SIZE)
                self.monedas_activas.append(moneda)
            elif object_type == "estrella" and not self.estrella_activa:
                y_pos = self.floor_y - random.randint(80, 200)
                estrella = Estrella(1, x_pos, y_pos)
                estrella.set_image(self.imgs["estrella"], STAR_SIZE)
                self.estrella_activa = estrella

    def spawn_goomba(self):
        """Genera enemigos (Goombas) en el juego."""
        current_time = pygame.time.get_ticks()
        if (current_time - self.goomba_timer > random.randint(2000, 5000)) and \
           (len(self.enemigos_activos) < self.max_goombas) and \
           (self.total_goombas_generados < self.max_total_goombas):

            self.goomba_timer = current_time
            x_pos = SCREEN_WIDTH + 50
            y_pos = self.floor_y - GOOMBA_SIZE[1] 

            goomba = Goomba(len(self.enemigos_activos), x_pos, y_pos)
            goomba.set_image(self.imgs["goomba"], GOOMBA_SIZE) 
            self.enemigos_activos.append(goomba)
            self.total_goombas_generados += 1

    def check_collision(self, rect1, rect2):
        """Verifica si dos rectángulos están colisionando."""
        if rect1 and rect2:
            return rect1.colliderect(rect2)
        return False

    def handle_collisions(self):
        """Maneja todas las colisiones del jugador."""
        player = self.current_player
        if not player or not player.rect:
            return

        # Colisión con hongos
        for hongo in list(self.poderes_activos):
            if self.check_collision(player.rect, hongo.rect):
                old_player_size = player.tamaño # Guarda el tamaño actual antes de cambiarlo
                
                if hongo.tipo == "crecimiento":
                    player.tamaño = "grande"
                    player.puntos += 100
                elif hongo.tipo == "vida":
                    player.vidas += 1
                    player.tamaño = "grande" 
                    player.puntos += 200

                # Solo ajusta la posición Y si el tamaño realmente cambió a grande
                if old_player_size != "grande" and player.tamaño == "grande":
                    # Calcular la diferencia de altura para mantener la base en el suelo
                    height_diff = PLAYER_BIG_SIZE[1] - PLAYER_NORMAL_SIZE[1]
                    player.posicionY -= height_diff # Mover hacia arriba para compensar el crecimiento
                    player.rect.y = player.posicionY 
                    player.set_current_animation_frame() # Actualiza la imagen y el rect después del ajuste de tamaño

                self.poderes_activos.remove(hongo)

        # Colisión con monedas
        for moneda in list(self.monedas_activas):
            if self.check_collision(player.rect, moneda.rect):
                player.monedas += 1
                player.puntos += 100
                self.monedas_activas.remove(moneda)
                if player.monedas >= 10:
                    player.vidas += 1
                    player.monedas = 0
                    player.puntos += 500

        # Colisión con estrella
        if self.estrella_activa and self.check_collision(player.rect, self.estrella_activa.rect):
            player.puntos += 500
            player.inmune = True
            self.immunity_timers[player.id] = pygame.time.get_ticks()
            self.estrella_activa = None

        # Colisión con Goombas
        for goomba in list(self.enemigos_activos):
            if self.check_collision(player.rect, goomba.rect):
                if player.velocidadY > 0 and player.rect.bottom - player.velocidadY <= goomba.rect.centery:
                    player.puntos += 100
                    self.enemigos_activos.remove(goomba)
                    player.velocidadY = -JUMP_STRENGTH_MIN 
                    player.grounded = False 
                    player.is_jumping = True 

                elif player.inmune:
                    player.puntos += 200
                    self.enemigos_activos.remove(goomba)
                else: # Mario es golpeado
                    if player.tamaño == "grande":
                        player.tamaño = "normal"
                        player.inmune = True
                        self.immunity_timers[player.id] = pygame.time.get_ticks()
                        # Al encogerse, ajusta la posición Y para que la base siga en el suelo
                        # La altura de Mario grande menos la altura de Mario normal
                        height_diff = PLAYER_BIG_SIZE[1] - PLAYER_NORMAL_SIZE[1]
                        player.posicionY += height_diff # Mover hacia abajo para compensar la reducción
                        player.rect.y = player.posicionY 
                        player.set_current_animation_frame() 
                    else:
                        player.vidas -= 1
                        if player.vidas <= 0:
                            player.estado = "Muerto"
                            self.game_over = True
                            self.game_running = False
                            pygame.mixer.music.stop() # Detener la música al terminar el juego
                        else:
                            player.inmune = True
                            self.immunity_timers[player.id] = pygame.time.get_ticks()
                    self.enemigos_activos.remove(goomba) 

    def update_immunity(self):
        """Actualiza el estado de inmunidad de los jugadores."""
        current_time = pygame.time.get_ticks()
        for player_id, start_time in list(self.immunity_timers.items()):
            if current_time - start_time > IMMUNITY_DURATION:
                for player in self.players:
                    if player.id == player_id:
                        player.inmune = False
                del self.immunity_timers[player_id]

    def update(self):
        """Actualiza el estado del juego."""
        if not self.game_running:
            return

        # Actualizar jugador
        if self.current_player:
            self.current_player.update() 
            self.current_player.aplicar_gravedad() 
            
            self.current_player.posicionX = max(0, min(self.current_player.posicionX, SCREEN_WIDTH - self.current_player.rect.width))
            self.current_player.rect.x = self.current_player.posicionX 

            self.current_player.set_current_animation_frame() 

        # Generar objetos y enemigos
        self.spawn_objects()
        self.spawn_goomba()

        # Actualizar posición de objetos y enemigos
        for hongo in self.poderes_activos:
            hongo.update()

        for moneda in self.monedas_activas:
            moneda.update()

        if self.estrella_activa:
            self.estrella_activa.update()

        for goomba in self.enemigos_activos:
            goomba.update()

        # Eliminar objetos fuera de pantalla
        self.poderes_activos = [obj for obj in self.poderes_activos if obj.posicionX > -obj.rect.width]
        self.monedas_activas = [obj for obj in self.monedas_activas if obj.posicionX > -obj.rect.width]
        if self.estrella_activa and self.estrella_activa.posicionX < -self.estrella_activa.rect.width:
            self.estrella_activa = None
        self.enemigos_activos = [obj for obj in self.enemigos_activos if obj.posicionX > -obj.rect.width]

        # Manejar colisiones
        self.handle_collisions()

        # Actualizar inmunidad
        self.update_immunity()

    def draw(self):
        """Dibuja todos los elementos del juego."""
        if "fondo" in self.imgs:
            self.screen.blit(self.imgs["fondo"], (0, 0))
        else:
            self.screen.fill(SKY_BLUE)
            pygame.draw.rect(self.screen, BROWN, (0, self.floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - self.floor_y))

        for hongo in self.poderes_activos:
            if hongo.image and hongo.rect:
                self.screen.blit(hongo.image, hongo.rect)

        for moneda in self.monedas_activas:
            if moneda.image and moneda.rect:
                self.screen.blit(moneda.image, moneda.rect)

        if self.estrella_activa and self.estrella_activa.image and self.estrella_activa.rect:
            self.screen.blit(self.estrella_activa.image, self.estrella_activa.rect)

        for goomba in self.enemigos_activos:
            if goomba.image and goomba.rect:
                self.screen.blit(goomba.image, goomba.rect)

        if self.current_player and self.current_player.image and self.current_player.rect:
            if self.current_player.inmune and pygame.time.get_ticks() % 200 < 100:
                pass 
            else:
                self.screen.blit(self.current_player.image, self.current_player.rect)

        if self.current_player:
            stats = [
                f"Vidas: {self.current_player.vidas}",
                f"Monedas: {self.current_player.monedas}",
                f"Puntos: {self.current_player.puntos}",
                f"Tamaño: {self.current_player.tamaño}",
                f"Inmune: {'Sí' if self.current_player.inmune else 'No'}"
            ]

            for i, stat in enumerate(stats):
                text = self.small_font.render(stat, True, BLACK)
                self.screen.blit(text, (10, 10 + i * 20))

        if self.in_menu:
            self.draw_menu()
        elif self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_menu(self):
        """Dibuja el menú principal."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("MARIO EN BUENAVENTURA", True, WHITE)
        start_text = self.small_font.render("Presiona ESPACIO para iniciar", True, WHITE)

        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def draw_game_over(self):
        """Dibuja la pantalla de fin de juego."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, RED)
        restart_text = self.small_font.render("Presiona R para reiniciar", True, WHITE)

        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    def handle_events(self):
        """Maneja los eventos del juego."""
        keys = pygame.key.get_pressed()
        running = True

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                if self.in_menu and event.key == K_SPACE:
                    self.start_game()
                elif self.game_over and event.key == K_r:
                    self.start_game()
                elif self.game_running and self.current_player:
                    if event.key in (K_LSHIFT, K_RSHIFT):
                        self.current_player.is_running = True
                    elif event.key == K_UP:
                        self.current_player.try_jump()
                    elif event.key == K_DOWN:
                        self.current_player.is_ducking = True
            if event.type == KEYUP and self.current_player:
                if event.key in (K_LSHIFT, K_RSHIFT):
                    self.current_player.is_running = False
                elif event.key == K_UP:
                    self.current_player.end_jump_key()
                elif event.key == K_DOWN:
                    self.current_player.is_ducking = False

        # Movimiento continuo basado en las teclas mantenidas
        if self.game_running and self.current_player:
            if not self.current_player.is_ducking:
                speed = PASO_X * (RUNNING_MULTIPLIER if self.current_player.is_running else 1)
                self.current_player.is_moving = False 

                if keys[K_RIGHT]:
                    self.current_player.direccion = "right"
                    self.current_player.mover(dx=speed)
                    self.current_player.is_moving = True
                elif keys[K_LEFT]:
                    self.current_player.direccion = "left"
                    self.current_player.mover(dx=-speed)
                    self.current_player.is_moving = True
            else:
                self.current_player.is_moving = False 
            
            # ¡Importante! Aquí ya no va la carga de música, eso va en __init__
            # y en start_game si necesitas reiniciarla.
            # La línea que tenías aquí se eliminó:
            # pygame.mixer.music.load("C:\Users\Jose\proyectomarioversion2\assets\sound")
            # pygame.mixer.music.play(-1)

        return running

    def run(self):
        """Bucle principal del juego."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60) 

        pygame.quit()