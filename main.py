import sqlite3
import pygame
pygame.init()

# nombre y base de datos
player_name = input("Introduce tu nombre: ")

# conectar a la base de datos
conn = sqlite3.connect("juego.db")
cursor = conn.cursor()

# crear tabla 
cursor.execute("""
CREATE TABLE IF NOT EXISTS jugadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    muertes INTEGER NOT NULL
)
""")

# muertes
deaths = 0

# screen
width, height = 950, 580
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("VAQUERO")

# spritesheet
spritesheet = pygame.image.load("vaquero.png").convert_alpha()

# configuracion spritesheet
frame_width = 48  # ancho de cada cuadrado del personaje
frame_height = 48  # alto de cada cuadrado

# posicion inicial vaquero (centrado)
player_x = width // 2 - frame_width // 2
player_y = height // 2 - frame_height // 2
move_speed = 5  # velocidad del personaje

# seleccion cuadro inicial poses (fila 0, columna 0)
col = 0
row = 0

# recorte del personaje
frame_rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)

# configuracion
running = True
clock = pygame.time.Clock()

# contador animacion
frame_count = 0
max_frames = 4  # numero de frames en spritesheet para animar

# bucle principal
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # movimiento con teclas
    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_a]:
        player_x -= move_speed
        row = 1  # fila 1 caminar hacia izquierda
        moved = True
    if keys[pygame.K_d]:
        player_x += move_speed
        row = 2  # fila 2 caminar hacia derecha
        moved = True
    if keys[pygame.K_w]:
        player_y -= move_speed
        row = 3  # fila 3 caminar hacia arriba
        moved = True
    if keys[pygame.K_s]:
        player_y += move_speed
        row = 0  # fila 0 sea caminar abajo o estatica
        moved = True

    # ejemplo de "muerte"
    # simular que si el jugador toca el borde superior muere
    if player_y < 0:
        deaths += 1
        print(f"{player_name} ha muerto {deaths} veces")
        # reiniciar posición
        player_y = height // 2 - frame_height // 2

    # Control si se mueve
    if moved:
        frame_count += 1
        if frame_count >= 10:  # cambiar cuadro cada 10 frames
            col = (col + 1) % max_frames
            frame_count = 0
    else:
        # pose estatica
        col = 0

    # actualizar rectangulo frame a recortar
    frame_rect.x = col * frame_width
    frame_rect.y = row * frame_height

    # background
    screen.fill((29, 41, 61))

    # recorte sprite del spritesheet y posicion del jugador
    frame = spritesheet.subsurface(frame_rect)
    screen.blit(frame, (player_x, player_y))

    # refresh screen
    pygame.display.flip()
    clock.tick(60)  # frames

pygame.quit()
# guardar datos al salir
cursor.execute("INSERT INTO jugadores (nombre, muertes) VALUES (?, ?)", (player_name, deaths))
conn.commit()
conn.close()