import pygame
import sys
import random
import math

# --- 초기화 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("탑다운 액션 슈터 - 보스 업데이트")
clock = pygame.time.Clock()

font = pygame.font.SysFont(["malgungothic", "applegothic", "nanumgothic", "notosanscjk", None], 24)
large_font = pygame.font.SysFont(["malgungothic", "applegothic", "nanumgothic", "notosanscjk", None], 60)

buffer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# --- 화면 흔들기 시스템 ---
shake_amount = 0

def trigger_shake(amount=10):
    global shake_amount
    shake_amount = amount

def get_shake_offset():
    global shake_amount
    if shake_amount > 0:
        ox = random.randint(-shake_amount, shake_amount)
        oy = random.randint(-shake_amount, shake_amount)
        shake_amount = max(0, shake_amount - 1)
        return ox, oy
    return 0, 0

# --- 게임 상태 변수들 ---
def init_game():
    global player, player_speed, lives, score, enemies, bullets, enemy_bullets, particles, game_over
    global boss, boss_active, boss_timer, next_boss_score
    player = pygame.Rect(SCREEN_WIDTH // 2 - 15, SCREEN_HEIGHT // 2 - 15, 30, 30)
    player_speed = 5
    lives = 3
    score = 0
    enemies = []
    bullets = []
    enemy_bullets = [] # 보스 총알 리스트 추가
    particles = []
    game_over = False
    
    # 보스 관련
    boss = None
    boss_active = False
    next_boss_score = 1000 # 1000점마다 보스 등장

init_game()

# --- 시스템 설정 ---
ENEMY_SPAWN_RATE = 60
enemy_timer = 0
shoot_cooldown = 0

def spawn_enemy():
    if boss_active: return # 보스전 중에는 일반 적 스폰 중단
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top": x, y = random.randint(0, SCREEN_WIDTH), -30
    elif side == "bottom": x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 30
    elif side == "left": x, y = -30, random.randint(0, SCREEN_HEIGHT)
    else: x, y = SCREEN_WIDTH + 30, random.randint(0, SCREEN_HEIGHT)
    
    enemies.append({
        "rect": pygame.Rect(x, y, 24, 24),
        "speed": random.uniform(1.5, 3.0),
        "hp": 2
    })

def spawn_boss():
    global boss, boss_active
    boss_active = True
    boss = {
        "rect": pygame.Rect(SCREEN_WIDTH // 2 - 50, -100, 100, 80),
        "hp": 50,
        "max_hp": 50,
        "speed": 3,
        "direction": 1,
        "shoot_timer": 0
    }

def spawn_particles(x, y, color=(255, 200, 50), count=15):
    for _ in range(count):
        particles.append({
            "x": x, "y": y,
            "vx": random.uniform(-5, 5),
            "vy": random.uniform(-5, 5),
            "life": random.randint(15, 30),
            "color": color
        })

# --- 메인 루프 ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            if event.key == pygame.K_r and game_over: init_game()

    keys = pygame.key.get_pressed()
    
    if not game_over:
        # 플레이어 이동
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  player.x = max(0, player.x - player_speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player.x = min(SCREEN_WIDTH - player.width, player.x + player_speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:    player.y = max(0, player.y - player_speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  player.y = min(SCREEN_HEIGHT - player.height, player.y + player_speed)

        # 사격
        mouse_buttons = pygame.mouse.get_pressed()
        if shoot_cooldown > 0: shoot_cooldown -= 1
        if mouse_buttons[0] and shoot_cooldown <= 0:
            mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my - player.centery, mx - player.centerx)
            bullets.append({
                "rect": pygame.Rect(player.centerx - 5, player.centery - 5, 10, 10),
                "vx": math.cos(angle) * 12, "vy": math.sin(angle) * 12
            })
            trigger_shake(2)
            shoot_cooldown = 10

        # 보스 스폰 체크
        if score >= next_boss_score and not boss_active:
            spawn_boss()
            next_boss_score += 1500 # 다음 보스는 더 높은 점수에서

        # 보스 로직
        if boss_active and boss:
            # 보스 등장 연출 (화면 안으로 들어옴)
            if boss["rect"].y < 50:
                boss["rect"].y += 2
            else:
                # 보스 좌우 이동 패턴
                boss["rect"].x += boss["speed"] * boss["direction"]
                if boss["rect"].right >= SCREEN_WIDTH or boss["rect"].left <= 0:
                    boss["direction"] *= -1

                # 보스 공격 패턴 (3갈래 탄막)
                boss["shoot_timer"] += 1
                if boss["shoot_timer"] > 40:
                    for a in [-0.3, 0, 0.3]: # 세 방향으로 발사
                        angle = math.atan2(player.centery - boss["rect"].centery, player.centerx - boss["rect"].centerx) + a
                        enemy_bullets.append({
                            "rect": pygame.Rect(boss["rect"].centerx, boss["rect"].bottom, 12, 12),
                            "vx": math.cos(angle) * 5, "vy": math.sin(angle) * 5
                        })
                    boss["shoot_timer"] = 0

        # 일반 적 스폰 및 이동
        enemy_timer += 1
        current_spawn_rate = max(15, ENEMY_SPAWN_RATE - (score // 100)) 
        if enemy_timer >= current_spawn_rate:
            spawn_enemy()
            enemy_timer = 0

        for e in enemies:
            dx, dy = player.centerx - e["rect"].centerx, player.centery - e["rect"].centery
            dist = math.hypot(dx, dy)
            if dist > 0:
                e["rect"].x += (dx / dist) * e["speed"]
                e["rect"].y += (dy / dist) * e["speed"]

        # 총알들 이동
        for b in list(bullets):
            b["rect"].x += b["vx"]; b["rect"].y += b["vy"]
            if not screen.get_rect().colliderect(b["rect"]): bullets.remove(b)
            
        for eb in list(enemy_bullets):
            eb["rect"].x += eb["vx"]; eb["rect"].y += eb["vy"]
            if not screen.get_rect().colliderect(eb["rect"]): enemy_bullets.remove(eb)
            elif eb["rect"].colliderect(player): # 보스 총알에 플레이어 피격
                enemy_bullets.remove(eb)
                lives -= 1
                trigger_shake(15)
                spawn_particles(player.centerx, player.centery, (255, 0, 0), 20)

        # 충돌 처리: 플레이어 총알 vs 적/보스
        for b in list(bullets):
            hit = False
            # 일반 적 충돌
            for e in list(enemies):
                if b["rect"].colliderect(e["rect"]):
                    e["hp"] -= 1; hit = True
                    spawn_particles(e["rect"].centerx, e["rect"].centery, (200, 200, 200), 5)
                    if e["hp"] <= 0:
                        enemies.remove(e); score += 50
                        trigger_shake(6); spawn_particles(e["rect"].centerx, e["rect"].centery, (255, 80, 80), 20)
                    break
            # 보스 충돌
            if not hit and boss_active and b["rect"].colliderect(boss["rect"]):
                boss["hp"] -= 1; hit = True
                trigger_shake(4); spawn_particles(b["rect"].centerx, b["rect"].centery, (255, 255, 255), 5)
                if boss["hp"] <= 0:
                    boss_active = False; score += 500
                    trigger_shake(30); spawn_particles(boss["rect"].centerx, boss["rect"].centery, (255, 200, 0), 50)
                    boss = None
            if hit and b in bullets: bullets.remove(b)

        # 충돌 처리: 플레이어 vs 적
        for e in list(enemies):
            if player.colliderect(e["rect"]):
                enemies.remove(e); lives -= 1
                trigger_shake(20); spawn_particles(player.centerx, player.centery, (255, 0, 0), 30)

        if lives <= 0: game_over = True

    # 파티클 업데이트
    for p in list(particles):
        p["x"] += p["vx"]; p["y"] += p["vy"]
        p["vx"] *= 0.95; p["vy"] *= 0.95; p["life"] -= 1
        if p["life"] <= 0: particles.remove(p)

    # --- 렌더링 ---
    buffer.fill((20, 20, 25))
    for i in range(0, 800, 100): pygame.draw.line(buffer, (40, 40, 50), (i, 0), (i, 600))
    for i in range(0, 600, 100): pygame.draw.line(buffer, (40, 40, 50), (0, i), (800, i))

    for p in particles:
        size = max(1, int(4 * p["life"] / 30))
        pygame.draw.circle(buffer, p["color"], (int(p["x"]), int(p["y"])), size)

    for b in bullets: pygame.draw.circle(buffer, (255, 255, 100), b["rect"].center, 5)
    for eb in enemy_bullets: pygame.draw.circle(buffer, (255, 50, 50), eb["rect"].center, 6)
    for e in enemies: 
        pygame.draw.rect(buffer, (220, 50, 50), e["rect"])
        pygame.draw.rect(buffer, (255, 150, 150), e["rect"], 2)

    if boss_active and boss:
        pygame.draw.rect(buffer, (150, 0, 255), boss["rect"]) # 보스 보라색
        pygame.draw.rect(buffer, (200, 100, 255), boss["rect"], 4)
        # 보스 체력바 UI
        hp_bar_width = 400
        hp_ratio = boss["hp"] / boss["max_hp"]
        pygame.draw.rect(buffer, (50, 50, 50), (SCREEN_WIDTH//2 - hp_bar_width//2, 20, hp_bar_width, 15))
        pygame.draw.rect(buffer, (200, 0, 0), (SCREEN_WIDTH//2 - hp_bar_width//2, 20, int(hp_bar_width * hp_ratio), 15))
        boss_label = font.render("BOSS APPEARED!", True, (200, 100, 255))
        buffer.blit(boss_label, (SCREEN_WIDTH//2 - boss_label.get_width()//2, 40))

    if not game_over:
        pygame.draw.rect(buffer, (50, 200, 255), player)
        pygame.draw.rect(buffer, (255, 255, 255), player, 2)

    buffer.blit(font.render(f"SCORE: {score}", True, (255, 255, 255)), (10, 10))
    buffer.blit(font.render(f"LIVES: {'♥' * lives}", True, (255, 50, 50)), (10, 40))

    if game_over:
        go_text = large_font.render("GAME OVER", True, (255, 50, 50))
        re_text = font.render("Press 'R' to Restart", True, (200, 200, 200))
        buffer.blit(go_text, (SCREEN_WIDTH//2 - go_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        buffer.blit(re_text, (SCREEN_WIDTH//2 - re_text.get_width()//2, SCREEN_HEIGHT//2 + 20))

    ox, oy = get_shake_offset()
    screen.fill((0, 0, 0))
    screen.blit(buffer, (ox, oy))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()