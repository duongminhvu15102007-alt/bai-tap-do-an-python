import pygame
import random

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Defender PRO")
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


clock = pygame.time.Clock()
FPS = 60

# Load ảnh
player_img = pygame.transform.scale(pygame.image.load("player.png"), (60, 50))
enemy_img = pygame.transform.scale(pygame.image.load("enemy.png"), (50, 50))
boss_img = pygame.transform.scale(pygame.image.load("boss.png"), (120, 100))
bullet_img = pygame.transform.scale(pygame.image.load("bullet.png"), (8, 20))

# Âm thanh
shoot_sound = pygame.mixer.Sound("shoot.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")

# Player
player = player_img.get_rect(midbottom=(WIDTH//2, HEIGHT-10))
player_speed = 6
player_hp = 3

# Bullet
bullets = []
bullet_speed = 10

# Enemy
enemies = []
enemy_speed = 3

# Boss
boss = None
boss_hp = 20

# Explosion effect
explosions = []

# Score
score = 0
font = pygame.font.SysFont(None, 36)

running = True
while running:
    clock.tick(FPS)
    screen.fill((0, 0, 0))

    # EVENT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = bullet_img.get_rect(midbottom=player.midtop)
                bullets.append(bullet)
                shoot_sound.play()

    # MOVE PLAYER
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] and player.right < WIDTH:
        player.x += player_speed

    # SPAWN ENEMY
    if random.randint(1, 30) == 1 and boss is None:
        enemy = enemy_img.get_rect(midtop=(random.randint(20, WIDTH-20), 0))
        enemies.append(enemy)

    # SPAWN BOSS
    if score >= 10 and boss is None:
        boss = boss_img.get_rect(midtop=(WIDTH//2, 0))

    # MOVE BULLETS
    for bullet in bullets:
        bullet.y -= bullet_speed
    bullets = [b for b in bullets if b.bottom > 0]

    # MOVE ENEMIES
    for enemy in enemies:
        enemy.y += enemy_speed

        # Nếu enemy chạm player → mất máu
        if enemy.colliderect(player):
            enemies.remove(enemy)
            player_hp -= 1

    # VA CHẠM ENEMY
    for enemy in enemies[:]:
        for bullet in bullets[:]:
            if enemy.colliderect(bullet):
                enemies.remove(enemy)
                bullets.remove(bullet)
                explosions.append(enemy.center)
                explosion_sound.play()
                score += 1
                break

    # VA CHẠM BOSS
    if boss:
        for bullet in bullets[:]:
            if boss.colliderect(bullet):
                bullets.remove(bullet)
                boss_hp -= 1
                explosion_sound.play()

        if boss_hp <= 0:
            boss = None
            score += 10

    # VẼ PLAYER
    screen.blit(player_img, player)

    # VẼ BULLET
    for bullet in bullets:
        screen.blit(bullet_img, bullet)

    # VẼ ENEMY
    for enemy in enemies:
        screen.blit(enemy_img, enemy)

    # VẼ BOSS
    if boss:
        screen.blit(boss_img, boss)

    # 💥 EXPLOSION (đơn giản)
    for pos in explosions:
        pygame.draw.circle(screen, (255, 100, 0), pos, 20)
    explosions.clear()

    # ❤️ HP
    hp_text = font.render(f"HP: {player_hp}", True, (255,0,0))
    screen.blit(hp_text, (10, 40))

    # SCORE
    score_text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(score_text, (10, 10))

    # GAME OVER
    if player_hp <= 0:
        over = font.render("GAME OVER", True, (255,0,0))
        screen.blit(over, (WIDTH//2 - 100, HEIGHT//2))
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False

    pygame.display.flip()

pygame.quit()