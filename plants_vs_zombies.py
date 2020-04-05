import random
import pygame
import sys
from pygame.locals import *

#列出各种可能用到的颜色
White = (255, 255, 255)
Black = (0, 0, 0)
Red = (255, 0, 0)
Green = (0, 255, 0)
DarkGreen = (0, 155, 0)
DarkGray = (40, 40, 40)
Yellow = (255, 255, 0)
RedDark = (150, 0, 0)
Blue = (0, 0, 255)
BlueDark = (0, 0, 150)

Width=880        #宽
Height =560      #高
Grass_size = 80  #每块草的大小为80
Screen = pygame.display.set_mode([Width, Height])    #设置游戏面板

#    背景类
class background():
    def __init__(self, x, y, index):
        if index == 0:
            self.picture = pygame.image.load('pictures/map1.png')
        else :
            self.picture = pygame.image.load('pictures/map2.png')
        self.rect = (x, y)
        self.can_be_grew = True   # 是否能够种植

    def draw_background(self):
         Screen.blit(self.picture, self.rect)
#   向日葵类
class Sunflower():
    def __init__(self,x,y):
        self.picture = pygame.image.load('pictures/sun_flower.png')
        self.rect = self.picture.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.price = 50      #50个阳光种植一个向日葵
        self.life = 100      #生命值为100
        self.alive = True    #活着
        self.count = 0       #循环到5生成1个阳光

    #   向日葵生成阳光
    def make_sun(self):
        self.count += 1
        if self.count == 5:
            game.sun += 1
            self.count = 0

    def draw_sun_flower(self):
        Screen.blit(self.picture, self.rect)

#   豌豆射手类
class PeaShooter():
    def __init__(self,x,y):
        self.picture = pygame.image.load('pictures/pea_shooter.png')
        self.rect = self.picture.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.price = 50     #50个阳光种植一个豌豆
        self.life = 1200
        self.alive = True
        self.count = 0      #循环到25就发射一次

    #   豌豆发射子弹
    def fire(self):
        #   判断是否应该射击
        flag = False
        for zombie in game.Zombies:
            if zombie.rect.y == self.rect.y and zombie.rect.x < Width + Grass_size/4 and zombie.rect.x > self.rect.x:
                flag = True

        if self.alive and flag:
            self.count += 1
            if self.count == 25:
                # 基于当前豌豆射手的位置，创建子弹
                pea_bullet = bullet(self)
                #6 将子弹存储到子弹列表中
                game.pea_bullets.append(pea_bullet)
                self.count = 0

    def draw_pea_shooter(self):
        Screen.blit(self.picture, self.rect)

#    豌豆子弹类
class bullet():
    def __init__(self, pea_shooter):
        self.alive = True
        self.picture = pygame.image.load('pictures/pea_bullet.png')
        self.rect = self.picture.get_rect()
        self.rect.x = pea_shooter.rect.x + 60
        self.rect.y = pea_shooter.rect.y + 15
        self.damage = 50
        self.speed  = 10

    #   子弹向右移动
    def move_bullet(self):
        if self.rect.x < Width + Grass_size / 4:
            self.rect.x += self.speed
        else:
            self.alive = False

    #   子弹打僵尸
    def hit_zombie(self):
        for zombie in game.Zombies:
            if pygame.sprite.collide_rect(self,zombie):
                #打中僵尸之后，子弹失效
                self.alive = False
                #僵尸掉血
                zombie.life -= self.damage
                if zombie.life <= 0:
                    zombie.alive = False
                    game.score += 1

    def draw_pea_bullet(self):
        Screen.blit(self.picture, self.rect)

#   僵尸类
class Zombie():
    def __init__(self,x,y,index):
        super(Zombie, self).__init__()
        if index == 1:
            self.picture = pygame.image.load('pictures/1.png')
        elif index == 2:
            self.picture = pygame.image.load('pictures/2.png')
        elif index == 3:
            self.picture = pygame.image.load('pictures/3.png')
        elif index == 4:
            self.picture = pygame.image.load('pictures/4.png')
        self.picture = pygame.transform.scale(self.picture, (Grass_size, Grass_size))
        self.rect = self.picture.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.life = 1000 + index * 1000
        self.damage = 1 + index
        self.speed = 0.5 + 0.5 * index
        self.alive = True
        self.stop = False

    #   僵尸向左移动
    def move_zombie(self):
        if self.alive and not self.stop:
            self.rect.x -= self.speed
            if self.rect.x < -Grass_size:
                return True
        return False

    #   判断僵尸是否碰撞到植物，如果碰撞，调用攻击植物的方法
    def hit_plant(self):
        for sun_flower in game.sun_flowers:
            if pygame.sprite.collide_rect(self,sun_flower):
                #   僵尸移动状态的修改
                self.stop = True
                self.eat_plant(sun_flower)
        for pea_shooter in game.pea_shooters:
            if pygame.sprite.collide_rect(self,pea_shooter):
                #   僵尸移动状态的修改
                self.stop = True
                self.eat_plant(pea_shooter)

    #   僵尸攻击植物
    def eat_plant(self,plant):
        #  植物生命值减少
        plant.life -= self.damage
        #  植物死亡后的状态修改，以及背景状态的修改
        if plant.life <= 0:
            x = int(plant.rect.y / 80)
            y = int(plant.rect.x / 80)
            map = game.grasses[x - 1][y]
            map.can_be_grew = True
            plant.alive = False
            #   修改僵尸的移动状态
            self.stop = False

    def draw_zombie(self):
        Screen.blit(self.picture, self.rect)
#   主类
class main():
    def __init__(self):
        self.step = 1                 #关数
        self.score = 0                #击杀僵尸的数量
        self.sun = 200                #累积的阳光
        self.grasses = []             #所有操块的坐标
        self.sun_flowers = []         #所有向日葵的坐标
        self.pea_shooters = []        #所有豌豆射手的坐标
        self.pea_bullets = []         #所有子弹的坐标
        self.Zombies = []             #所有僵尸的坐标

    def draw_start_screen(self):
        Screen.fill((Black))  # 设置背景为白色
        Screen.blit(print_text('提示: 鼠标操作游戏 左键种植向日葵 右键种植豌豆射手(均为50个阳光)', 26, Red), (5, 5))
        Screen.blit(print_text('剩余阳光值 {}'.format(game.sun), 26, White), (640, 40))
        Screen.blit(print_text(
            '关数 {}  成功击杀僵尸 {} 只'.format(game.step, game.score), 26,
            White), (5, 40))

    #   打印游戏结束得界面
    def draw_game_over_screen(self):
        GameOverFont = pygame.font.Font('freesansbold.ttf', 180)
        GameSurf = GameOverFont.render('Game', True, White)
        OverSurf = GameOverFont.render('Over', True, White)
        GameRect = GameSurf.get_rect()
        overRect = OverSurf.get_rect()
        GameRect.midtop = (Width / 2, 80)
        overRect.midtop = (Width / 2, GameRect.height + 100)
        Screen.blit(GameSurf, GameRect)
        Screen.blit(OverSurf, overRect)
        Screen.blit(print_text('Press any key to continue', 20, Blue), (Width - 250, Height - 30))
        pygame.display.update()
        pygame.time.wait(500)
        checkForKeyPress()
        while True:
            if checkForKeyPress():
                pygame.event.get()
                return

    #   初始化坐标点
    def init_grasses(self):
        self.grass_points=[]
        for y in range(1, 7):
            points = []
            for x in range(11):
                point = (x, y)
                points.append(point)
            self.grass_points.append(points)
        for points in self.grass_points:
            temp = []
            for point in points:
                if (point[0] + point[1]) % 2 == 0:
                    map = background(point[0] * Grass_size, point[1] * Grass_size, 0)
                else:
                    map = background(point[0] * Grass_size, point[1] * Grass_size, 1)
                temp.append(map)
            self.grasses.append(temp)

    #   新增初始化僵尸
    def init_zombies(self):
        for time in range(self.step * 2):
            for i in range(1, 7):
                distance = random.randint(1, 5) * 100
                if time <= 3:
                    zombie = Zombie(Width + distance, i * Grass_size, 1)
                    self.Zombies.append(zombie)
                elif time <= 7 and time >= 4:
                    zombie = Zombie(Width + distance, i * Grass_size, 2)
                    self.Zombies.append(zombie)
                elif time <= 11 and time >= 8:
                    zombie = Zombie(Width + distance, i * Grass_size, 3)
                    self.Zombies.append(zombie)
                elif time <= 15 and time >= 12:
                    zombie = Zombie(Width + distance, i * Grass_size, 4)
                    self.Zombies.append(zombie)
                else :
                    zombie = Zombie(Width + distance, i * Grass_size, random.randint(1,4))
                    self.Zombies.append(zombie)

    #   打印背景
    def draw_background(self):
        for temp_map_list in self.grasses:
            for map in temp_map_list:
                map.draw_background()

    #   打印向日葵并且启动生成阳光
    def draw_sun_flowers(self):
        for sun_flower in self.sun_flowers:
            if sun_flower.alive:
                sun_flower.draw_sun_flower()
                sun_flower.make_sun()
            else:
                self.sun_flowers.remove(sun_flower)

    #   打印豌豆射手并且启动发射
    def draw_pea_shooters(self):
        for pea_shooter in self.pea_shooters:
            if pea_shooter.alive:
                pea_shooter.draw_pea_shooter()
                pea_shooter.fire()
            else:
                self.pea_shooters.remove(pea_shooter)

    #   打印所有子弹
    def draw_pea_bullets(self):
        for bullet in self.pea_bullets:
            if bullet.alive:
                bullet.draw_pea_bullet()
                bullet.move_bullet()
                bullet.hit_zombie()
            else:
                self.pea_bullets.remove(bullet)

    #   打印所有僵尸
    def draw_zombies(self):
        flag = False
        for zombie in self.Zombies:
            if zombie.alive:
                zombie.draw_zombie()
                if zombie.move_zombie() == True:
                    flag = True
                zombie.stop = False
                zombie.hit_plant()
            else:
                self.Zombies.remove(zombie)
        return flag      #true表示僵尸胜利 游戏结束

    #   处理事件
    def deal_events(self):
        for event in pygame.event.get():        # 从队列当中获取事件 遍历事件列表，判断
            if event.type == pygame.QUIT:
                GameOver()
            elif event.type == pygame.MOUSEBUTTONDOWN:   #如果type的是鼠标
                x = int(event.pos[0] / Grass_size)
                y = int(event.pos[1] / Grass_size)
                position = self.grasses[y - 1][x]        #因为草的坐标定义再左上角  所以整除要减一
                if event.button == 1:                    #左键增加向日葵
                    if position.can_be_grew and self.sun >= 50:
                        sunflower = Sunflower(position.rect[0], position.rect[1])
                        self.sun_flowers.append(sunflower)
                        position.can_be_grew = False
                        self.sun -= 50
                elif event.button == 3:                  #右键增加豌豆
                    if position.can_be_grew and self.sun >= 50:
                        peashooter = PeaShooter(position.rect[0], position.rect[1])
                        self.pea_shooters.append(peashooter)
                        position.can_be_grew = False
                        self.sun -= 50

game = main()

#游戏结束
def GameOver():
    pygame.quit()
    sys.exit()

def drawStartScreen():
    Screen.fill(White)
    picture = pygame.image.load('pictures/begin.jpg')
    picture = pygame.transform.scale(picture, (Width, Height - 50))
    Screen.blit(picture, (0, 0))
    font = pygame.font.Font('思源黑体.otf', 40)
    text = font.render('请按任意键开始游戏', True, Red)
    Screen.blit(text, (250, 510))
    while True:
        if checkForKeyPress():
            pygame.event.get()
            return
        pygame.display.update()

def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        GameOver()
    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        GameOver()
    return keyUpEvents[0].key

#   文本打印
def print_text(text, size, color):
    font = pygame.font.SysFont('kaiti', size)
    text = font.render(text, True, color)
    return text

def play_game(game):
    game.init_grasses()
    game.init_zombies()
    count = 0
    while True:
        game.draw_start_screen()         #打印提示
        game.draw_background()           #打印背景
        game.draw_sun_flowers()          #打印向日葵
        game.draw_pea_shooters()         #打印豌豆射手
        game.draw_pea_bullets()          #打印子弹
        game.deal_events()               #处理事件
        if count == 0:
            if game.draw_zombies() == True:  #打印僵尸
                return
        else :
            count += 1
            if count == 60:              #count计数到60期间打印一大波....
                count = 0
            Screen.blit(print_text('第 {} 关'.format(game.step), 80, Yellow), (300, 80))
            Screen.blit(print_text('一大波僵尸', 150, Red), (80, 150))
            Screen.blit(print_text('即将来袭', 150, Red), (135, 350))

        if len(game.Zombies) == 0:       #杀完全部僵尸就进入下一关
            game.step += 1
            game.init_zombies()          #重新定义一批数量更多能力更强的僵尸
            count = 1

        pygame.time.wait(10)
        pygame.display.update()          #更新页面

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('植物大战僵尸   author:宣启楠')
    pygame.mixer.music.load('植物大战僵尸.mp3')
    pygame.mixer.music.play(-1, 0)      # 背景音乐循环播放
    drawStartScreen()
    while True:
        game = main()
        play_game(game)
        game.draw_game_over_screen()