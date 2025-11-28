# ProyGame: VAQUERO EN LA CUEVA
# Autor: Sanchez Chavarria Yeslie Alessandra  No.Control: 23760341
# Materia: Graficacion
# Descripcion:
# Juego en Python usando Pygame y SQLite
# Personaje: vaquero, debe escapar de la cueva
# El numero de muertes se guarda en una base de datos por nombre
# Movimiento con teclas WASD
# Disparo con click izquierdo
# Pierdes si el vaquero toca el borde superior

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

# balas
bullets = []  # lista de balas activas
bullet_speed = 10  # velocidad de las balas
total_bullets_fired = 0  # contador total de balas disparadas
max_bullets_total = 5  # maximo de balas en toda la partida

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
        elif event.type == pygame.MOUSEBUTTONDOWN:
             if event.button == 1:  # click izquierdo

                if total_bullets_fired < max_bullets_total:  # si aun quedan balas

                    # obtener posicion del mouse
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # centro del vaquero
                    bullet_x = player_x + frame_width // 2
                    bullet_y = player_y + frame_height // 2

                    # calcular vector direccion hacia el mouse
                    dx = mouse_x - bullet_x
                    dy = mouse_y - bullet_y

                    # normalizar vector
                    length = (dx**2 + dy**2) ** 0.5
                    if length != 0:
                        dx /= length
                        dy /= length

                    # guardar bala con posicion y direccion
                    bullets.append([bullet_x, bullet_y, dx, dy])
                    total_bullets_fired += 1  # incrementar contador total

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

    # limite de la pantalla para el jugador
    if player_x < 0:
        player_x = 0
    if player_x > width - frame_width:
        player_x = width - frame_width
    if player_y > height - frame_height:
        player_y = height - frame_height

    # ejemplo de "muerte"
    # simular que si el jugador toca el borde superior muere
    if player_y < 0:
        deaths += 1
        print(f"{player_name} ha muerto {deaths} veces")
        # reiniciar posicion
        player_y = height // 2 - frame_height // 2

    # control si se mueve
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

    # mover y dibujar balas
    for bullet in bullets[:]:  # iterar sobre copia para poder eliminar
        bullet[0] += bullet[2] * bullet_speed  # mover en X
        bullet[1] += bullet[3] * bullet_speed  # mover en Y
        pygame.draw.circle(screen, (255, 255, 0), (int(bullet[0]), int(bullet[1])), 5)

        # eliminar si sale de la pantalla
        if bullet[0] < 0 or bullet[0] > width or bullet[1] < 0 or bullet[1] > height:
            bullets.remove(bullet)

    # refresh screen
    pygame.display.flip()
    clock.tick(60)  # frames

pygame.quit()
# guardar datos al salir
cursor.execute("INSERT INTO jugadores (nombre, muertes) VALUES (?, ?)", (player_name, deaths))
conn.commit()
conn.close()