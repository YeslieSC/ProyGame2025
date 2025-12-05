# ProyGame: VAQUERO EN LA CUEVA
# Autor: Sanchez Chavarria Yeslie Alessandra  No.Control: 23760341
# Materia: Graficacion
# Descripcion:
# Juego en Python usando Pygame y SQLite
# Personaje: vaquero, debe escapar de la cueva
# El numero de muertes se guarda en una base de datos por nombre
# Movimiento con teclas WASD
# Disparo con click izquierdo
# Objetivo: llegar a la salida

import sqlite3
import pygame
import sys

pygame.init()

# configuracion de pantalla
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("VAQUERO")

# fuentes
font = pygame.font.SysFont(None, 20)
title_font = pygame.font.SysFont(None, 20)
big_font = pygame.font.SysFont(None, 20)

# base de datos
conn = sqlite3.connect("juego.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS jugadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    muertes INTEGER NOT NULL
)
""")

# variables de juego por defecto
deaths = 0  # conteo de muertes del jugador

# balas: se permite disparar solo 5 en total
bullets = []  # cada bala: {x,y,dx,dy}
bullet_speed = 12
total_bullets_fired = 0
max_bullets_total = 5

# spritesheets
villano_spritesheet = pygame.image.load("villanos.png").convert_alpha()
villano_frame_width = 134
villano_frame_height = 124
villano_speed = 3  # velocidad de persecucion

vaquero_spritesheet = pygame.image.load("vaquero.png").convert_alpha()
frame_width = 48
frame_height = 48

# posicion inicial jugador centrada
player_x = width // 2 - frame_width // 2
player_y = height // 2 - frame_height // 2
move_speed = 5

# animacion del jugador
col = 0
row = 0
frame_rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
frame_count = 0
max_frames = 4  # columnas en spritesheet del vaquero

# tiempo antes de que los villanos empiecen a perseguir al jugador
pursue_delay_ms = 5000 # milisegundos

# posicion inicial para villanos (arriba)
top_y = 20
x_spacing = width // 6

# crear villanos
villanos = []
for i in range(5):
    x = (i + 1) * x_spacing - villano_frame_width // 2
    y = top_y + (i % 2) * 10
    fila = i % 3
    villanos.append({
        "initial_x": float(x),
        "x": float(x),
        "y": float(y),
        "frame": 0,
        "fila": fila,
        "alive": True
    })

def reset_villanos_to_top(only_alive=True):
    """Coloca a los villanos (o solo los vivos) en la fila superior en sus posiciones iniciales."""
    for idx, v in enumerate(villanos):
        if only_alive and not v["alive"]:
            continue
        v["x"] = v["initial_x"]
        v["y"] = top_y + (idx % 2) * 10
        v["frame"] = 0

def reset_all_villanos():
    """Revivir y colocar a todos los villanos arriba (uso en reintento)."""
    for idx, v in enumerate(villanos):
        v["alive"] = True
        v["x"] = v["initial_x"]
        v["y"] = top_y + (idx % 2) * 10
        v["frame"] = 0

# reloj y estado
running = True
clock = pygame.time.Clock()

# estado para entrada de nombre en pantalla
entering_name = True
name_text = ""
max_name_len = 20
cursor_visible = True
cursor_timer = 0.0
cursor_interval = 0.5  # parpadeo del cursor en segundos
player_name = None  # se asignara cuando el usuario confirme en pantalla

# estados de juego que inician despues de confirmar nombre
start_ticks = None
pursuing = False
game_over = False  # cuando True, mostrar "Has muerto" y detener la logica activa
won = False  # cuando True, mostrar menu de victoria

# salida: rectangulo blanco arriba (objetivo)
exit_w, exit_h = 160, 40
exit_rect = pygame.Rect(width // 2 - exit_w // 2, 8, exit_w, exit_h)

# botones del menu de victoria
button_w, button_h = 160, 50
retry_button = pygame.Rect(width // 2 - button_w - 20, height // 2 + 20, button_w, button_h)
quit_button = pygame.Rect(width // 2 + 20, height // 2 + 20, button_w, button_h)

# funciones auxiliares
def draw_name_input():
    screen.fill((29, 41, 61))
    title_surf = title_font.render("Introduce tu nombre", True, (255, 255, 255))
    screen.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 60))

    # Caja de texto
    box_w, box_h = min(520, width - 40), 50
    box_x = width // 2 - box_w // 2
    box_y = height // 2 - box_h // 2
    pygame.draw.rect(screen, (230, 230, 230), (box_x - 2, box_y - 2, box_w + 4, box_h + 4))  # borde
    pygame.draw.rect(screen, (20, 20, 30), (box_x, box_y, box_w, box_h))  # fondo caja

    # texto dentro de la caja
    display_text = name_text if name_text != "" else "Escribe aquí..."
    color = (255, 255, 255) if name_text != "" else (150, 150, 150)
    txt_surf = font.render(display_text, True, color)
    screen.blit(txt_surf, (box_x + 10, box_y + (box_h - txt_surf.get_height()) // 2))

    # cursor parpadeante
    if cursor_visible and name_text != "":
        cursor_x = box_x + 10 + txt_surf.get_width() + 2
        cursor_y = box_y + 10
        cursor_h = box_h - 20
        pygame.draw.rect(screen, (255, 255, 255), (cursor_x, cursor_y, 2, cursor_h))

    # indicaciones
    hint = font.render("Enter para confirmar", True, (180, 180, 180))
    screen.blit(hint, (width // 2 - hint.get_width() // 2, box_y + box_h + 10))

    pygame.display.flip()

def draw_hud(name, bullets_left, deaths, pursuing, seconds_left):
    # exit box (blanco) con etiqueta
    pygame.draw.rect(screen, (255, 255, 255), exit_rect)
    exit_label = font.render("SALIDA", True, (0, 0, 0))
    screen.blit(exit_label, (exit_rect.centerx - exit_label.get_width() // 2, exit_rect.centery - exit_label.get_height() // 2))

    status_text = f"Villanos: {'persiguen' if pursuing else f'esperando {seconds_left}s'}"
    hud_text = f"{name}    Balas restantes: {bullets_left}    Muertes: {deaths}    {status_text}"
    hud_surf = font.render(hud_text, True, (255, 255, 255))
    screen.blit(hud_surf, (10, height - 30))

def draw_game_over():
    screen.fill((29, 41, 61))
    over_surf = big_font.render("Has muerto", True, (255, 80, 80))
    info_surf = font.render("Presiona ESC o cierra la ventana para salir", True, (200, 200, 200))
    screen.blit(over_surf, (width // 2 - over_surf.get_width() // 2, height // 2 - 30))
    screen.blit(info_surf, (width // 2 - info_surf.get_width() // 2, height // 2 + 20))
    pygame.display.flip()

def draw_win_menu():
    # pantalla tenue de fondo
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    win_surf = big_font.render("¡Has llegado a la salida!", True, (220, 255, 220))
    screen.blit(win_surf, (width // 2 - win_surf.get_width() // 2, height // 2 - 80))

    # dibujar botones
    pygame.draw.rect(screen, (200, 200, 200), retry_button)
    pygame.draw.rect(screen, (200, 200, 200), quit_button)
    retry_label = font.render("Reintentar", True, (0, 0, 0))
    quit_label = font.render("Salir", True, (0, 0, 0))
    screen.blit(retry_label, (retry_button.centerx - retry_label.get_width() // 2, retry_button.centery - retry_label.get_height() // 2))
    screen.blit(quit_label, (quit_button.centerx - quit_label.get_width() // 2, quit_button.centery - quit_label.get_height() // 2))
    pygame.display.flip()

def reset_for_retry():
    """Reinicia el estado del juego para un reintento completo (mantiene player_name)."""
    global bullets, total_bullets_fired, deaths, player_x, player_y, start_ticks, game_over, won
    bullets = []
    total_bullets_fired = 0
    deaths = 0
    player_x = width // 2 - frame_width // 2
    player_y = height // 2 - frame_height // 2
    reset_all_villanos()
    start_ticks = pygame.time.get_ticks()
    game_over = False
    won = False

# bucle principal
while running:
    dt = clock.tick(60) / 1000.0  # segundos desde el ultimo frame

    # entrada de nombre en pantalla
    if entering_name:
        cursor_timer += dt
        if cursor_timer >= cursor_interval:
            cursor_timer = 0.0
            cursor_visible = not cursor_visible

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if name_text.strip() != "":
                        player_name = name_text.strip()[:max_name_len]
                        entering_name = False
                        # iniciar el juego: marcar tiempo de inicio para delay de villanos
                        start_ticks = pygame.time.get_ticks()
                    # si es vacio, no confirmamos; puedes mostrar mensaje si quieres
                elif event.key == pygame.K_BACKSPACE:
                    name_text = name_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    break
                else:
                    # capturar caracteres imprimibles
                    if len(name_text) < max_name_len and event.unicode.isprintable():
                        name_text += event.unicode

        # dibujar cuadro de entrada
        draw_name_input()
        continue  # saltar la logica del juego hasta que el nombre este confirmado

    # si estamos en pantalla de victoria, manejar clicks en botones
    if won:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if retry_button.collidepoint(mx, my):
                    reset_for_retry()
                elif quit_button.collidepoint(mx, my):
                    running = False
                    break
        draw_win_menu()
        continue

    # si game over, solo permitir cerrar con ESC o cerrar ventana
    if game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                break
        draw_game_over()
        continue

    # logica del juego normal
    elapsed_ms = pygame.time.get_ticks() - start_ticks
    pursuing = (elapsed_ms >= pursue_delay_ms) and (not game_over)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        # manejar disparo
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if total_bullets_fired < max_bullets_total:
                mx, my = pygame.mouse.get_pos()
                bullet_x = player_x + frame_width / 2
                bullet_y = player_y + frame_height / 2
                dx = mx - bullet_x
                dy = my - bullet_y
                length = (dx * dx + dy * dy) ** 0.5
                if length == 0:
                    dx, dy = 1.0, 0.0
                else:
                    dx /= length
                    dy /= length
                bullets.append({"x": bullet_x, "y": bullet_y, "dx": dx, "dy": dy})
                total_bullets_fired += 1

    # movimiento del jugador con teclado
    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_a]:
        player_x -= move_speed
        row = 1
        moved = True
    if keys[pygame.K_d]:
        player_x += move_speed
        row = 2
        moved = True
    if keys[pygame.K_w]:
        player_y -= move_speed
        row = 3
        moved = True
    if keys[pygame.K_s]:
        player_y += move_speed
        row = 0
        moved = True

    # limitar al area de juego
    player_x = max(0, min(player_x, width - frame_width))
    player_y = max(0, min(player_y, height - frame_height))

    # animacion del jugador
    if moved:
        frame_count += 1
        if frame_count >= 10:
            col = (col + 1) % max_frames
            frame_count = 0
    else:
        col = 0
    frame_rect.x = col * frame_width
    frame_rect.y = row * frame_height

    # fondo
    screen.fill((29, 41, 61))

    # dibujar salida
    pygame.draw.rect(screen, (255, 255, 255), exit_rect)
    exit_label = font.render("SALIDA", True, (0, 0, 0))
    screen.blit(exit_label, (exit_rect.centerx - exit_label.get_width() // 2, exit_rect.centery - exit_label.get_height() // 2))

    # dibujar jugador
    player_frame = vaquero_spritesheet.subsurface(frame_rect)
    screen.blit(player_frame, (player_x, player_y))
    player_center_x = player_x + frame_width / 2
    player_center_y = player_y + frame_height / 2

    # mover y dibujar balas
    for bullet in bullets[:]:
        bullet["x"] += bullet["dx"] * bullet_speed
        bullet["y"] += bullet["dy"] * bullet_speed
        pygame.draw.circle(screen, (255, 255, 0), (int(bullet["x"]), int(bullet["y"])), 5)
        if bullet["x"] < -10 or bullet["x"] > width + 10 or bullet["y"] < -10 or bullet["y"] > height + 10:
            bullets.remove(bullet)

    # actualizar villanos: si pursuing True persiguen, sino permanecen arriba
    for idx, villano in enumerate(villanos):
        if not villano["alive"]:
            continue

        if pursuing:
            vx = player_center_x - (villano["x"] + villano_frame_width / 2)
            vy = player_center_y - (villano["y"] + villano_frame_height / 2)
            dist = (vx * vx + vy * vy) ** 0.5
            if dist != 0:
                vx /= dist
                vy /= dist
            else:
                vx, vy = 0.0, 0.0
            villano["x"] += vx * villano_speed
            villano["y"] += vy * villano_speed

            # clamp dentro pantalla
            villano["x"] = max(0, min(villano["x"], width - villano_frame_width))
            villano["y"] = max(0, min(villano["y"], height - villano_frame_height))
        else:
            # mantienen su posicion superior (ya estan en top)
            pass

        # animacion del villano
        villano["frame"] = (villano["frame"] + 1) % 5
        vr = pygame.Rect(
            int(villano["frame"]) * villano_frame_width,
            int(villano["fila"]) * villano_frame_height,
            villano_frame_width,
            villano_frame_height
        )
        screen.blit(villano_spritesheet.subsurface(vr), (int(villano["x"]), int(villano["y"])))

    # colisiones bala villano: 1 bala mata 1 villano
    for bullet in bullets[:]:
        brect = pygame.Rect(int(bullet["x"]) - 5, int(bullet["y"]) - 5, 10, 10)
        hit = False
        for villano in villanos:
            if not villano["alive"]:
                continue
            vrect = pygame.Rect(int(villano["x"]), int(villano["y"]), villano_frame_width, villano_frame_height)
            if brect.colliderect(vrect):
                villano["alive"] = False
                try:
                    bullets.remove(bullet)
                except ValueError:
                    pass
                hit = True
                break
        if hit:
            continue

    # colisiones villano jugador: solo aqui muere el jugador
    player_rect = pygame.Rect(int(player_x), int(player_y), frame_width, frame_height)
    died_this_frame = False
    for villano in villanos:
        if not villano["alive"]:
            continue
        vrect = pygame.Rect(int(villano["x"]), int(villano["y"]), villano_frame_width, villano_frame_height)
        if player_rect.colliderect(vrect):
            deaths += 1
            print(f"{player_name} ha muerto {deaths} veces")
            died_this_frame = True
            break

    if died_this_frame:
        bullets.clear()  # limpiar balas al morir para evitar muertes instantaneas
        if deaths == 1:
            # primera muerte: reposicionar villanos vivos arriba y esperar 5s antes de perseguir otra vez
            reset_villanos_to_top(only_alive=True)
            player_x = width // 2 - frame_width // 2
            player_y = height // 2 - frame_height // 2
            start_ticks = pygame.time.get_ticks()
            pursuing = False
        elif deaths >= 2:
            # segunda muerte: game over
            game_over = True

    # comprobar si llego a la salida (victoria)
    if player_rect.colliderect(exit_rect) and not game_over:
        # llego a la salida => victoria
        won = True

    # hud simple: balas restantes, muertes y estado villanos
    remaining_bullets = max_bullets_total - total_bullets_fired
    seconds_left = max(0, (pursue_delay_ms - elapsed_ms + 999) // 1000)
    draw_hud(player_name if player_name else "Anon", remaining_bullets, deaths, pursuing, seconds_left)

    # mensaje de victoria si todos los villanos estan muertos
    if all(not v["alive"] for v in villanos) and not won:
        win_surf = font.render("¡Has eliminado a todos los villanos!", True, (180, 255, 180))
        screen.blit(win_surf, (width // 2 - win_surf.get_width() // 2, height // 2 - 10))

    pygame.display.flip()

# guardar datos en la DB (UPSERT sumando muertes) y cerrar
try:
    if player_name is None or player_name == "":
        player_name = "Anon"
    cursor.execute("""
    INSERT INTO jugadores (nombre, muertes) VALUES (?, ?)
    ON CONFLICT(nombre) DO UPDATE SET muertes = jugadores.muertes + excluded.muertes
    """, (player_name, deaths))
    conn.commit()
    print(f"Guardadas {deaths} muertes para {player_name}")
except Exception as e:
    print("Error guardando en DB:", e)
finally:
    conn.close()
    pygame.quit()
    sys.exit()