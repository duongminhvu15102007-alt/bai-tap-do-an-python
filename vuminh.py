import pygame, random, math

# Khoi tao
pygame.init()

W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Space Defender PRO")
clock = pygame.time.Clock()

# He thong hinh anh (bo toan bo am thanh)
bg         = pygame.transform.scale(pygame.image.load("background.png"), (W, H))
player_img = pygame.transform.scale(pygame.image.load("player.png"),     (80, 70))
enemy_img  = pygame.transform.scale(pygame.image.load("enemy.png"),      (50, 50))
boss_img   = pygame.transform.scale(pygame.image.load("boss.png"),       (120, 100))
bullet_img = pygame.transform.scale(pygame.image.load("bullet.png"),     (10, 20))

fnt  = pygame.font.SysFont(None, 36)
fntL = pygame.font.SysFont(None, 80)
fntM = pygame.font.SysFont(None, 44)
fntS = pygame.font.SysFont(None, 32)

# Hang so
P_SPD, B_SPD, E_SPD              = 6, 10, 3
BOSS_HP_MAX, BOSS_B_SPD, BOSS_CD = 30, 5, 90
BOSS_SCORE_THRESHOLD             = 20

# Trang thai toan cuc
STATE = "menu"


# Ve nut bam chuot
def draw_button(text, rect, hover, red=False):
    if red:
        c_fill   = (200,  60,  60) if hover else (140, 30, 30)
        c_border = (255, 160, 160) if hover else (200, 60, 60)
    else:
        c_fill   = ( 60, 180,  60) if hover else ( 30,120, 30)
        c_border = (160, 255, 160) if hover else ( 60,180, 60)
    pygame.draw.rect(screen, c_fill,   rect, border_radius=12)
    pygame.draw.rect(screen, c_border, rect, 3, border_radius=12)
    lbl = fntS.render(text, True, (255, 255, 255))
    screen.blit(lbl, (rect.centerx - lbl.get_width()//2,
                      rect.centery - lbl.get_height()//2))


# Rect cac nut
BTN_START  = pygame.Rect(W//2 - 150, H//2 +  20, 300, 58)
BTN_QUIT0  = pygame.Rect(W//2 - 150, H//2 +  95, 300, 58)

BTN_REPLAY = pygame.Rect(W//2 - 165, H//2 +  70, 155, 58)
BTN_QUIT1  = pygame.Rect(W//2 +  10, H//2 +  70, 155, 58)


def overlay():
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 145))
    screen.blit(ov, (0, 0))

def draw_menu():
    screen.blit(bg, (0, 0)); overlay()
    mx, my = pygame.mouse.get_pos()

    t = fntL.render("SPACE DEFENDER PRO", True, (255, 60, 60))
    screen.blit(t, (W//2 - t.get_width()//2, H//2 - 150))

    draw_button("  Bat dau choi", BTN_START, BTN_START.collidepoint(mx, my))
    draw_button("Thoat game",   BTN_QUIT0, BTN_QUIT0.collidepoint(mx, my), red=True)
    pygame.display.flip()

def draw_endscreen(win, score):
    screen.blit(bg, (0, 0)); overlay()
    mx, my = pygame.mouse.get_pos()

    if win:
        title = fntL.render("YOU WIN!",              True, (0,  255, 120))
        sub   = fntM.render("Boss da bi tieu diet!", True, (255, 240,  80))
    else:
        title = fntL.render("GAME OVER",             True, (255,  60,  60))
        sub   = fntM.render("Ban da bi tieu diet!",  True, (255, 160,  80))

    screen.blit(title, (W//2 - title.get_width()//2, H//2 - 170))
    screen.blit(sub,   (W//2 - sub.get_width()//2,   H//2 -  80))

    sc = fntM.render(f"Diem so: {score}", True, (255, 255, 255))
    screen.blit(sc, (W//2 - sc.get_width()//2, H//2 - 15))

    draw_button("Choi lai", BTN_REPLAY, BTN_REPLAY.collidepoint(mx, my))
    draw_button("Thoat",    BTN_QUIT1,  BTN_QUIT1.collidepoint(mx, my), red=True)
    pygame.display.flip()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit(); exit()
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if BTN_REPLAY.collidepoint(ev.pos): return "replay"
            if BTN_QUIT1.collidepoint(ev.pos):  return "quit"
    return None


def new_game():
    return {
        "player"     : player_img.get_rect(midbottom=(W//2, H-10)),
        "hp"         : 3,
        "score"      : 0,
        "bullets"    : [],
        "enemies"    : [],
        "expl"       : [],
        "you_win"    : False,
        "gameover"   : False,
        "sfx_played" : False,
        "boss": {
            "rect": None, "hp": BOSS_HP_MAX,
            "vx": 3, "vy": 1,
            "mv_t": 0, "mv_cd": 90,
            "sh_t": 0, "bullets": [],
        },
    }


def boss_update(bs, target):
    r = bs["rect"]
    if not r: return

    bs["mv_t"] += 1
    if bs["mv_t"] >= bs["mv_cd"]:
        bs["mv_t"]  = 0
        bs["mv_cd"] = random.randint(40, 120)
        bs["vx"]    = random.choice([-1, 1]) * random.uniform(2, 5)
        bs["vy"]    = random.uniform(0.3, 2.0)

    r.x += bs["vx"]; r.y += bs["vy"]
    if r.left   <= 0:   r.left   = 0;    bs["vx"] =  abs(bs["vx"])
    if r.right  >= W:   r.right  = W;    bs["vx"] = -abs(bs["vx"])
    if r.top    <  20:  r.top    = 20;   bs["vy"] =  abs(bs["vy"])
    if r.bottom > H//2: r.bottom = H//2; bs["vy"] = -abs(bs["vy"])

    bs["sh_t"] += 1
    if bs["sh_t"] >= BOSS_CD:
        bs["sh_t"] = 0
        ox, oy = r.midbottom
        dx, dy = target.centerx - ox, target.centery - oy
        dist   = math.hypot(dx, dy) or 1
        ang    = random.uniform(-60, 60)
        for vx, vy in [
            (0, BOSS_B_SPD),
            (dx/dist*BOSS_B_SPD, dy/dist*BOSS_B_SPD),
            (math.sin(math.radians(ang))*BOSS_B_SPD,
             math.cos(math.radians(ang))*BOSS_B_SPD),
        ]:
            bs["bullets"].append({
                "rect": bullet_img.get_rect(midtop=(ox, oy)),
                "vx": vx, "vy": vy
            })

    for bb in bs["bullets"]:
        bb["rect"].x += bb["vx"]; bb["rect"].y += bb["vy"]
    bs["bullets"] = [bb for bb in bs["bullets"] if bb["rect"].top < H]


# Vong lap chinh
gs = new_game()

while True:
    clock.tick(60)

    # MENU
    if STATE == "menu":
        draw_menu()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if BTN_START.collidepoint(ev.pos):
                    gs = new_game(); STATE = "play"
                if BTN_QUIT0.collidepoint(ev.pos):
                    pygame.quit(); exit()
        continue

    # MAN HINH KET THUC
    if STATE in ("youwin", "gameover"):
        result = draw_endscreen(STATE == "youwin", gs["score"])
        if result == "replay":
            gs = new_game(); STATE = "play"
        elif result == "quit":
            pygame.quit(); exit()
        continue

    # GAMEPLAY FRAME
    screen.blit(bg, (0, 0))

    pl  = gs["player"]
    bs  = gs["boss"]
    bul = gs["bullets"]
    ene = gs["enemies"]

    alive = gs["hp"] > 0 and not gs["you_win"] and not gs["gameover"]

    # Events
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: pygame.quit(); exit()
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE and alive:
            bul.append(bullet_img.get_rect(midbottom=pl.midtop))
            # (da bo shoot_sfx.play())

    if alive:
        keys = pygame.key.get_pressed()
        # Chi di chuyen TRAI / PHAI, bo up/down
        if keys[pygame.K_LEFT]  and pl.left  > 0: pl.x -= P_SPD
        if keys[pygame.K_RIGHT] and pl.right < W: pl.x += P_SPD

        # Spawn ke thu / boss
        if random.randint(1, 30) == 1 and not bs["rect"]:
            ene.append(enemy_img.get_rect(midtop=(random.randint(20, W-20), 0)))
        if gs["score"] >= BOSS_SCORE_THRESHOLD and not bs["rect"]:
            bs.update({
                "rect": boss_img.get_rect(midtop=(W//2, 20)),
                "hp": BOSS_HP_MAX,
                "vx": random.choice([-3, 3]), "vy": 1,
                "mv_t": 0, "sh_t": 0, "bullets": []
            })
            ene.clear()

    boss_update(bs, pl)

    # Di chuyen dan player
    for b in bul: b.y -= B_SPD
    gs["bullets"] = bul = [b for b in bul if b.bottom > 0]

    def lose_hp(n=1):
        if not alive: return
        gs["hp"] -= n
        if gs["hp"] <= 0:
            gs["hp"] = 0
            gs["gameover"] = True

    # Ke thu di chuyen
    for e in ene[:]:
        e.y += E_SPD
        if   e.colliderect(pl): ene.remove(e); lose_hp()
        elif e.top > H:         ene.remove(e)

    # Dan player vs ke thu
    for e in ene[:]:
        for b in bul[:]:
            if e.colliderect(b):
                ene.remove(e); bul.remove(b)
                gs["expl"].append(e.center)
                # (da bo explode_sfx.play())
                gs["score"] += 1; break

    # Dan player vs boss
    if bs["rect"]:
        for b in bul[:]:
            if bs["rect"].colliderect(b):
                bul.remove(b); bs["hp"] -= 1
                # (da bo explode_sfx.play())
        if bs["hp"] <= 0:
            gs["expl"].append(bs["rect"].center)
            bs["rect"] = None
            gs["score"] += 10
            gs["you_win"] = True

    # Dan boss vs player
    if bs["rect"]:
        for bb in bs["bullets"][:]:
            if bb["rect"].colliderect(pl):
                bs["bullets"].remove(bb); lose_hp()
        if bs["rect"] and bs["rect"].colliderect(pl):
            lose_hp(gs["hp"])

    # Chuyen trang thai ket thuc (bo phat nhac, bo pygame.time.wait)
    if (gs["you_win"] or gs["gameover"]) and not gs["sfx_played"]:
        gs["sfx_played"] = True
        STATE = "youwin" if gs["you_win"] else "gameover"

    # Ve game
    screen.blit(player_img, pl)
    for b   in bul:         screen.blit(bullet_img, b)
    for e   in ene:         screen.blit(enemy_img,  e)
    for pos in gs["expl"]:  pygame.draw.circle(screen, (255, 100, 0), pos, 20)
    gs["expl"].clear()

    if bs["rect"]:
        screen.blit(boss_img, bs["rect"])
        for bb in bs["bullets"]:
            pygame.draw.rect(screen, (255, 80, 0),
                             bb["rect"].inflate(6, 6), border_radius=4)
        bw = 220; bx = W//2 - bw//2; by = 10
        pygame.draw.rect(screen, (80,  0,   0), (bx, by, bw, 18))
        pygame.draw.rect(screen, (255, 0,   0), (bx, by, int(bw*bs["hp"]/BOSS_HP_MAX), 18))
        pygame.draw.rect(screen, (255, 255, 0), (bx, by, bw, 18), 2)
        screen.blit(fnt.render("BOSS", True, (255, 0, 0)), (bx-60, by-2))

    screen.blit(fnt.render(f"Score: {gs['score']}", True, (255,255,255)), (10, 10))
    screen.blit(fnt.render(f"HP: {gs['hp']}",       True, (255,  0,  0)), (10, 40))

    pygame.display.flip()

pygame.quit()