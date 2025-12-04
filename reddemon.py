import heapq
import pyglet
from pyglet.window import key

# --- Üldised seaded ---
TILE = 40
current_level = 1
show_jumpscare = False
show_finish = False
game_started = False

window = pyglet.window.Window(800, 600, "2D Labürindi Mäng")

# --- Ressursid ---
start_bg = pyglet.image.load(r"assets/lukama pilt.png")
jumpscare_image = pyglet.image.load(r"assets/jumpscare.jpg")
jumpscare_sound = pyglet.media.load(r"assets/jumpscare.wav.mp3", streaming=False)
bg_music = pyglet.media.load(r"assets/dark-horror-soundscape-345814.mp3")
step_sound = pyglet.media.load(r"assets/step-351163.mp3", streaming=False)

# --- Taustamuusika ---
bg_player = pyglet.media.Player()
bg_player.queue(bg_music)
bg_player.loop = True

# --- Vaenlane ---
enemy_x, enemy_y = 1, 1
ENEMY_SPEED = 0.5

# --- Mängija ---
player_x = 0
player_y = 0

# --- Labürint ---
maze = []
ROWS = 0
COLS = 0

# --- Abifunktsioonid ---
def can_move(x, y):
    return 0 <= x < COLS and 0 <= y < ROWS and maze[y][x] != 1

def neighbors(node):
    x, y = node
    nbrs = []
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if can_move(nx, ny):
            nbrs.append((nx, ny))
    return nbrs

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(start, goal):
    if start == goal:
        return [start]

    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, None))
    came_from = {}
    gscore = {start: 0}
    closed = set()

    while open_set:
        _, g, current, parent = heapq.heappop(open_set)
        if current in closed:
            continue
        came_from[current] = parent
        if current == goal:
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from.get(node)
            return path[::-1]
        closed.add(current)

        for nbr in neighbors(current):
            tentative_g = g + 1
            if tentative_g < gscore.get(nbr, 1e9):
                gscore[nbr] = tentative_g
                f = tentative_g + heuristic(nbr, goal)
                heapq.heappush(open_set, (f, tentative_g, nbr, current))
    return []

# --- Mängija liikumine ---
def try_move_player(dx, dy):
    global player_x, player_y

    nx = player_x + dx
    ny = player_y + dy

    if can_move(nx, ny):
        player_x = nx
        player_y = ny
        return True

    return False

# --- Levelid ---
def load_level(level_number):
    global maze, player_x, player_y, ROWS, COLS, enemy_x, enemy_y, ENEMY_SPEED

    if level_number == 1:
        maze = [
            [1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,1,1,1,1],
            [1,1,1,1,1,2,1,1,1,1]
        ]
        ENEMY_SPEED = 0.6
        player_x, player_y = 8, 1
        enemy_x, enemy_y = 1, 1

    elif level_number == 2:
        maze = [
            [1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,0,1,0,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,0,1,0,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,2,1],
            [1,1,1,1,1,1,1,1,1,1]
        ]
        ENEMY_SPEED = 0.35
        player_x, player_y = 8, 1
        enemy_x, enemy_y = 1, 1

    elif level_number == 3:
        maze = [
            [1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,2,1],
            [1,1,1,1,1,1,1,1,1,1]
        ]
        ENEMY_SPEED = 0.15
        player_x, player_y = 8, 1
        enemy_x, enemy_y = 1, 1

    ROWS = len(maze)
    COLS = len(maze[0])

def load_next_level():
    global current_level, show_finish
    current_level += 1

    if current_level > 3:
        show_finish = True
        pyglet.clock.schedule_once(lambda dt: window.close(), 5)
    else:
        load_level(current_level)
        schedule_enemy_speed()

def check_finish():
    if maze[player_y][player_x] == 2:
        load_next_level()

# --- Vaenlane A* liikumine ---
def move_enemy_towards_player(dt):
    global enemy_x, enemy_y, show_jumpscare

    if show_jumpscare or show_finish or not game_started:
        return

    start = (enemy_x, enemy_y)
    goal = (player_x, player_y)
    path = astar(start, goal)

    if len(path) >= 2:
        enemy_x, enemy_y = path[1]

    if enemy_x == player_x and enemy_y == player_y:
        show_jumpscare = True
        jumpscare_sound.play()
        pyglet.clock.schedule_once(lambda dt: window.close(), 3)

def schedule_enemy_speed():
    pyglet.clock.unschedule(move_enemy_towards_player)
    pyglet.clock.schedule_interval(move_enemy_towards_player, ENEMY_SPEED)

# --- DRAW ---
@window.event
def on_draw():
    window.clear()
    pyglet.gl.glClearColor(0.05,0.05,0.05,1)

    if not game_started:
        start_bg.blit(0,0,width=window.width,height=window.height)
        pyglet.text.Label("red demon", font_size=64, x=window.width//2, y=window.height//2+50,
                          anchor_x='center', anchor_y='center', color=(255,0,0,255)).draw()
        pyglet.text.Label("Press SPACE to Play", font_size=36, x=window.width//2, y=window.height//2-50,
                          anchor_x='center', anchor_y='center').draw()
        return

    if show_jumpscare:
        jumpscare_image.blit(0,0,width=window.width,height=window.height)
        return

    if show_finish:
        pyglet.text.Label("U escaped the demon...", font_size=48,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center',
                          color=(255,0,0,255)).draw()
        return

    # Maze
    for y in range(ROWS):
        for x in range(COLS):
            tile = maze[y][x]
            if tile == 1:
                color = [50,50,50]*4
            elif tile == 2:
                color = [0,255,0]*4
            else:
                continue
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2f',[x*TILE,y*TILE, x*TILE+TILE,y*TILE,
                        x*TILE+TILE,y*TILE+TILE, x*TILE,y*TILE+TILE]),
                ('c3B',color))

    # Player
    px, py = player_x*TILE, player_y*TILE
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
        ('v2f',[px,py, px+TILE,py, px+TILE,py+TILE, px,py+TILE]),
        ('c3B',[210,105,30]*4))

    # Enemy
    ex, ey = enemy_x*TILE, enemy_y*TILE
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
        ('v2f',[ex,ey, ex+TILE,ey, ex+TILE,ey+TILE, ex,ey+TILE]),
        ('c3B',[255,0,0]*4))

# --- KEY PRESS ---
@window.event
def on_key_press(symbol, modifiers):
    global game_started

    if not game_started and symbol == key.SPACE:
        load_level(current_level)
        game_started = True
        bg_player.play()
        schedule_enemy_speed()
        return

    if not game_started or show_jumpscare or show_finish:
        return

    moved = False

    if symbol == key.W:
        moved = try_move_player(0, 1)
    elif symbol == key.S:
        moved = try_move_player(0, -1)
    elif symbol == key.A:
        moved = try_move_player(-1, 0)
    elif symbol == key.D:
        moved = try_move_player(1, 0)

    if moved:
        step_sound.play()
        check_finish()

# --- RUN ---
pyglet.app.run()

