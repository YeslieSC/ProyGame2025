## ProyGame2025

# Descripcion
El jugador es un vaquero que despierta por alguna razon en una mazmorra, su misionn es encontrar la salida y para eso debera sobrevivir peleando contra
los enemigos que encuentre en el camino. Encontrara armas y algunos objetos para defenderse durante el proceso y contara con 2 vidas, si el jugador
pierde esas 2 vidas tendra que empezar desde 0.

## Acciones del jugador
El jugador avanza hacia cualquer zona del lugar para encontrar armas o enemigos.
El jugador debe pelear con los enemigos porque estos lo seguiran por la zona hasta derrotarlo.
Si el jugador pierde una vez seguira en el mismo lugar, si el jugador pierde 2 veces tendra que iniciar desde 0.
La pistala hara daño de inmediato con un solo disparo, pero solo tendra 5 balas.
Algunos objetos como palo y piedra haran menos daños por lo que debera golpear a los enemigos varias veces para derrotarlos.

## limitaciones
Pocas armas.
Un arma a la vez, debera soltar un arma para poder cargar otra.
Si se pierden las 2 vidas debera inicar desde 0.

## Caracteristicas
- El juego pide el *nombre del jugador* al iniciar.
- El personaje (vaquero) se mueve con las teclas **W, A, S, D**.
- Se cuenta el número de muertes (ejemplo: si toca el borde superior por ahora).
- Al cerrar el juego, se guarda en la base de datos `juego.db`:
  - Nombre del jugador
  - Número de muertes

## Logica
- El juego crea la tabla `jugadores (id, nombre, muertes)` en `juego.db` si no existe.
- Las "muertes" aumentan cuando el jugador cruza el borde superior (condicion simple implementada en `main.py`).
- Al salir, se inserta un registro con el nombre y el numero de muertes acumuladas.

## Archivos importantes
- `main.py` — codigo principal (control, animacion y guardado en BD).
- `vaquero.png` — spritesheet del personaje (debe estar en la misma carpeta que `main.py`).
- `juego.db` — base de datos SQLite creada automaticamente al ejecutar el juego.
- `README.md` — este archivo.

## Requisitos
- Python 3.10 o superior.
- Libreria Pygame
- SQLite (ya incluido en Python)
