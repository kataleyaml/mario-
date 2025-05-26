import pygame
import os

# Dimensiones de la pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Física y movimiento del juego
PASO_X = 3 
RUNNING_MULTIPLIER = 2.5 
GROUND_LEVEL_OFFSET = 50
GOOMBA_SPEED = 2
OBJECT_SPEED = 2 

# Constantes para el salto variable y múltiple
GRAVITY = 0.5 
JUMP_STRENGTH_MIN = 8 
JUMP_STRENGTH_MAX = 14 
JUMP_ACCELERATION_FACTOR = -0.5 
JUMP_CUT_FACTOR = 0.5 
JUMP_AIR_IMPULSE_FACTOR = 0.7 

# Duraciones (en milisegundos)
IMMUNITY_DURATION = 3000  # 3 segundos
PLAYER_RUN_ANIMATION_SPEED = 100

# Colores (definiciones de colores RGB)
SKY_BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)

# Rutas de las imágenes (relativas al directorio del proyecto)
# Ahora solo necesitamos las imágenes de Mario "normal" y "agachado"
IMG_PATHS = {
    "fondo": "Fondo.png",  

    # Mario Normal (estas serán las imágenes base para ambos tamaños)
    "mario_normal": os.path.join("assets", "mario_normal.png"),              
    "mario_normal_izquierda": os.path.join("assets", "mario_normal_izquierda.png"), 
    "mario_corriendo_derecha_1": os.path.join("assets", "mario_corriendo_derecha.png"), 
    "mario_corriendo_izquierda_1": os.path.join("assets", "mario_corriendo_izquierda.png"), 

    # Mario Agachado
    "mario_agachado": os.path.join("assets", "mario_agachado.png"),         

    # Eliminamos las referencias a "mario_grande.png", "3.png", "5.png" directamente aquí,
    # ya que no las cargaremos como sets de imágenes separadas para Mario grande.
    # Si estas imágenes son las mismas que mario_normal, puedes mantenerlas,
    # pero el código no las usará para distinguir entre normal y grande, solo el escalado.

    # Poderes y Enemigos
    "hongo_crecimiento": os.path.join("assets", "hongo_Verde.png"),         
    "hongo_vida": os.path.join("assets", "hongo_Rojo.png"),                 
    "moneda": os.path.join("assets", "moneda.png"),                         
    "estrella": os.path.join("assets", "estrella.png"),                     
    "goomba": os.path.join("assets", "goomba.png"),                         
}

# Escalado de imágenes (tamaños finales deseados para los objetos)
PLAYER_NORMAL_SIZE = (40, 60)   
PLAYER_DUCK_SIZE = (40, 40)     
PLAYER_BIG_SIZE = (55, 80)      
# Opcional: Define un tamaño específico para Mario Grande Agachado si lo quieres diferente
# PLAYER_BIG_DUCK_SIZE = (55, 55)
GOOMBA_SIZE = (45, 45)          
MUSHROOM_SIZE = (35, 35)        
COIN_SIZE = (30, 30)            
STAR_SIZE = (40, 40)            