# -*- coding:utf-8 -*-

import pygame
import time
import random
import sys
from pygame.locals import *

#全局变量
#窗口
window_screen = None
#hero
hero = None
#得分
hit_score = 0
#是否暂停
is_pause = False

#图片变量
#暂停图片
pause_image = None
#hero_fire_music
hero_fire_music = None
#number照片
number_image = []
#score_hp照片
score_hp_image = None
#单三管炮弹照片
one_or_three_barral = []
#三管炮弹子弹余量照片
bullet_3_stock = None
#max_score
max_score_image = None
#boss_hp
boss_HP_image = None
#line
line_image = None
#背景
background = None
#重新开始
restart = None
#退出游戏
exit_game = None
#操作说明
description = None


#关于飞机
##飞机HP
HP_list = [1, 20, 100, 20]#enemy0, enemy1, enemy2, hero
#飞机大小
plane_size = [{"width":51, "height":39}, {"width":69, "height":89}, {"width":165, "height":246}, {"width":100, "height":124}]
#各种飞机爆炸效果计数更换图片
plane_bomb_time = [5, 8, 14, 8]#enemy0, enemy1, enemy2, hero
#飞机最大子弹数
plane_maximum_bullet = [2, 5, 7, 8]#enemy0, enemy1, enemy2, hero
#血量补给
blood_supply = None
#子弹补给
bullet_supply = None

#关于子弹
#敌机子弹类型
bullet_type = ["bullet1.png", "bullet-1.gif", "bullet2.png", "bullet.png"]
#子弹伤害值
bullet_damage_value = [1, 1, 3, 1]#enemy0, enemy1, enemy2, hero
#补给
supply_image = ["bomb-1.gif", "bomb-2.gif"]
#补给的大小
supply_size = [{"width":58, "height":88}, {"width":60, "height":103}]
#敌机引用列表
enemy0_list = []#enemy0存在飞机列表
enemy0_maximum = 8#enemy0飞机存在最大值
enemy1_list = []#enemy1存在飞机列表
enemy1_maximum = 1
enemy2_list = []#enemy2存在飞机列表
enemy2_maximum = 1


class Base(object):
    """所有类的基类"""
    def __init__(self, screen_temp, x, y, image_name):
        self.x = x
        self.y = y
        self.screen = screen_temp
        self.image = pygame.image.load(image_name)
        

class BasePlane(Base):
    """飞机基类"""
    def __init__(self, plane_type, screen_temp, x, y, image_name, picture_num, HP_temp):
        Base.__init__(self, screen_temp, x, y, image_name)#plane_type飞机类型
        self.bullet_list = [] #存储发射出去的子弹的引用
        self.plane_type = plane_type #飞机类型标示, 3是hero
        #爆炸效果用的如下属性
        self.hitted = False #表示是否要爆炸
        self.bomb_picture_list = [] #用来存储爆炸时需要的图片
        self.bomb_picture_num = picture_num #飞机爆炸效果的图片数量
        self.picture_count = 0#用来记录while True的次数,当次数达到一定值时才显示一张爆炸的图,然后清空,,当这个次数再次达到时,再显示下一个爆炸效果的图片
        self.image_index = 0#用来记录当前要显示的爆炸效果的图片的序号
        self.HP = HP_temp #飞机hp
        self.fire_bullet_count = 0#飞机已发射子弹计数

    def display(self):
        """显示玩家的飞机"""
        global hit_score
        global HP_list
        global plane_bomb_time#飞机爆炸效果计数
        #如果被击中,就显示爆炸效果,否则显示普通的飞机效果
        if self.hitted == True and self.image_index < self.bomb_picture_num and self.HP <= 0:
            self.screen.blit(self.bomb_picture_list[self.image_index], (self.x, self.y))
            if self.plane_type != 3 and self.image_index == 0 and self.picture_count == 0:
                if self.plane_type == 0:#击毁enemy0得分＋HP
                    if hit_score < 650:#初始血量为1
                        hit_score += HP_list[self.plane_type]
                    else:#初始血量为2
                        hit_score += HP_list[self.plane_type]/2
                elif self.plane_type == 1:#击毁enemy1得分＋HP/2
                    hit_score += HP_list[self.plane_type]/2
                else:#击毁enemy2得分＋HP/4
                    hit_score += HP_list[self.plane_type]/4
            self.picture_count += 1
            if self.picture_count == plane_bomb_time[self.plane_type]: #根据飞机类型不同，爆炸效果持续的时间不同
                self.picture_count = 0
                self.image_index += 1
        elif self.image_index < self.bomb_picture_num:
            self.screen.blit(self.image, (self.x, self.y)) #显示原图
        if self.hitted == True and not self.bullet_list and self.image_index >= self.bomb_picture_num and self.HP <= 0:
            del_plane(self) #删除被击中敌机的对象
        #敌机飞出window后删除
        if self.y > 860:
            del_plane(self)
        #删除越界子弹
        del_outWindow_bullet(self)

    #创建出爆炸效果的图片的引用
    def crate_images(self, bomb_picture_name):
            for i in range(1, self.bomb_picture_num + 1):
                self.bomb_picture_list.append(pygame.image.load("./feiji/" + bomb_picture_name + str(i) + ".png"))

    #判断是否被击中
    def isHitted(self, plane, width, height):# widht和height表示范围
        if plane.bullet_list and self.HP:
            for bullet in plane.bullet_list:
                if bullet.x > self.x+0.05*width and bullet.x < self.x+0.95*width and bullet.y+0.1*height > self.y and bullet.y < self.y + 0.8*height:
                    self.HP -= bullet.damage_value#hero的HP减去子弹的伤害值
                    if self.plane_type == 3:
                        show_score_HP()
                    plane.bullet_list.remove(bullet) #删除击中的子弹
                    self.hitted = True
            if plane.plane_type == 3 and plane.barrel_2 and plane.barrel_3:
                for bullet in plane.barrel_2:#判断炮管３是否击中
                    if bullet.x > self.x+0.05*width and bullet.x < self.x+0.95*width and bullet.y+0.1*height > self.y and bullet.y < self.y + 0.8*height:
                        self.HP -= bullet.damage_value#hero的HP减去子弹的伤害值
                        plane.barrel_2.remove(bullet) #删除击中的子弹
                        self.hitted = True
                for bullet in plane.barrel_3:#判断炮管３是否击中
                    if bullet.x > self.x+0.05*width and bullet.x < self.x+0.95*width and bullet.y+0.1*height > self.y and bullet.y < self.y + 0.8*height:
                        self.HP -= bullet.damage_value#hero的HP减去子弹的伤害值
                        plane.barrel_3.remove(bullet) #删除击中的子弹
                        self.hitted = True
    #飞机开火
    def fire(self, bullet_maximun):
        if self.HP > 0:
            random_num = random.randint(1, 60)
            if (random_num == 10 or random_num == 45) and len(self.bullet_list) < bullet_maximun:
                self.bullet_list.append(EnemyBullet(self.screen, self.x, self.y, self))
                self.fire_bullet_count += 1

                    
class HeroPlane(BasePlane):
    global supply_size
    def __init__(self, screen_temp):
        BasePlane.__init__(self, 3, screen_temp, 210, 728, "./feiji/hero1.png", 4, HP_list[3]) #super().__init__()
        BasePlane.crate_images(self, "hero_blowup_n")
        self.key_down_list = [] #用来存储键盘上下左右移动键
        self.space_key_list = []#保存space键
        self.is_three_bullet = False
        self.barrel_2 = []#2号炮管(左)
        self.barrel_3 = []#3号炮管(右)
        self.three_bullet_stock = 50#三管齐发子弹初始值为50
    #单键移动方向
    def move_left(self):
        self.x -= 7
    def move_right(self):
        self.x += 7
    def move_up(self):
        self.y -= 6
    def move_down(self):
        self.y += 6
    #双键移动方向
    def move_left_and_up(self):
        self.x -= 5
        self.y -= 6
    def move_right_and_up(self):
        self.x += 5
        self.y -= 6
    def move_lef_and_down(self):
        self.x -= 5
        self.y += 6
    def move_right_and_down(self):
        self.x += 5
        self.y += 6
    #控制飞机左右移动范围s
    def move_limit(self):
        if self.x < 0:
            self.x = -2
        elif self.x + 100 > 480:
            self.x = 380
        if self.y > 728:
            self.y = 728
        elif self.y < 350:
            self.y += 6
    #键盘按下向列表添加按键
    def key_down(self, key):
        self.key_down_list.append(key)
    #键盘松开向列表删除按键
    def key_up(self, key):
        if len(self.key_down_list) != 0: #判断是否为空
            try:
                self.key_down_list.remove(key)
            except Exception:
                pass
    #控制hero的持续移动
    def press_move(self):
        if len(self.key_down_list) != 0:
            if len(self.key_down_list) == 2:#两个键
                if (self.key_down_list[0] == K_LEFT and self.key_down_list[1] == K_UP) or (self.key_down_list[1] == K_LEFT and self.key_down_list[0] == K_UP):#key_down_list列表存在按键为left,up 或 up,left时调用move_left_and_up()方法
                    self.move_left_and_up()
                elif (self.key_down_list[0] == K_RIGHT and self.key_down_list[1] == K_UP) or (self.key_down_list[1] == K_RIGHT and self.key_down_list[0] == K_UP):
                    self.move_right_and_up()
                elif (self.key_down_list[0] == K_LEFT and self.key_down_list[1] == K_DOWN) or (self.key_down_list[1] == K_LEFT and self.key_down_list[0] == K_DOWN):
                    self.move_lef_and_down()
                elif (self.key_down_list[0] == K_RIGHT and self.key_down_list[1] == K_DOWN) or (self.key_down_list[1] == K_RIGHT and self.key_down_list[0] == K_DOWN):
                    self.move_right_and_down()
            else:#一个键
                if self.key_down_list[0] == K_LEFT:
                    self.move_left()
                elif self.key_down_list[0] == K_RIGHT:
                    self.move_right()
                elif self.key_down_list[0] == K_UP:
                    self.move_up()
                elif self.key_down_list[0] == K_DOWN:
                    self.move_down()
    #自爆
    def bomb(self):
        self.hitted = True
        self.HP = 0
    #键盘按下向列表添加space
    def space_key_down(self, key):
        self.space_key_list.append(key)
    #键盘松开向列表删除space
    def space_key_up(self, key):
        if len(self.space_key_list) != 0: #判断是否为空
            try:
                self.space_key_list.pop(0)
            except Exception:
                raise
    #按键space不放,持续开火
    def press_fire(self):
        if len(self.bullet_list) == 0 and len(self.space_key_list):
            self.fire()
        else:
            if len(self.space_key_list) != 0:
                if self.bullet_list[len(self.bullet_list)-1].y < self.y-14-60:
                    self.fire()
    #开火
    def fire(self):
        global plane_maximum_bullet
        hero_fire_music.play()
        if not self.is_three_bullet:
            if len(self.bullet_list) < plane_maximum_bullet[self.plane_type]:#单发炮台子弹限制为8
                self.bullet_list.append(Bullet(self.screen, self.x+40, self.y-14, self))
        else:#没有子弹限制
            #主炮管
            self.bullet_list.append(Bullet(self.screen, self.x+40, self.y-14, self))
            #创建２，３号炮管子弹
            self.barrel_2.append(Bullet(self.screen, self.x+5, self.y+20, self))
            self.barrel_3.append(Bullet(self.screen, self.x+75, self.y+20, self))
            self.three_bullet_stock -= 1#三管炮弹弹药余量-1
            if not self.three_bullet_stock:#三管齐发弹药用完
                self.is_three_bullet = False
    #是否吃到补给
    def supply_hitted(self, supply_temp, width, height):# widht和height表示范围
        if supply_temp and self.HP:
            #更加精确的判断是否吃到补给
            supply_temp_left_x = supply_temp.x + supply_size[supply_temp.supply_type]["width"]*0.15
            supply_temp_right_x = supply_temp.x + supply_size[supply_temp.supply_type]["width"]*0.85
            supply_temp_top_y = supply_temp.y + supply_size[supply_temp.supply_type]["height"]*0.4
            supply_temp_bottom_y = supply_temp.y + supply_size[supply_temp.supply_type]["height"]*0.9
            if supply_temp_left_x > self.x+0.05*width and supply_temp_right_x <self.x+0.95*width and supply_temp_top_y < self.y+0.95*height and supply_temp_bottom_y > self.y+0.1*height:
                if supply_temp.supply_type == 0:#0为血量补给，吃到血量补给
                    self.HP -= supply_temp.supply_HP#血量-(-3)
                    if self.HP > 41:#血量最大值为41
                        self.HP = 41
                    show_score_HP()
                else:#吃到弹药补给
                    self.is_three_bullet = True
                    self.three_bullet_stock += 20#三管炮弹余量+20
                del_supply(supply_temp)


class Enemy0Plane(BasePlane):
    """enemy0的类"""
    def __init__(self, screen_temp):
        random_num_x = random.randint(12, 418)
        random_num_y = random.randint(-50, -40)
        BasePlane.__init__(self, 0, screen_temp, random_num_x, random_num_y, "./feiji/enemy0.png", 4, HP_list[0])
        BasePlane.crate_images(self, "enemy0_down")#第二个参数为飞机的plane_type, 0为enemy0
    def move(self):
        self.y += 4

class Enemy1Plane(BasePlane):
    """enemy1的类"""
    def __init__(self, screen_temp):
        BasePlane.__init__(self, 1, screen_temp, 205, -90, "./feiji/enemy1.png", 4, HP_list[1])
        BasePlane.crate_images(self, "enemy1_down")
        self.direction = "right" #用来存储飞机默认显示方向
        self.num_y = random.randint(15, 400)#出现后左右移动的y值
    #移动
    def move(self):
        if self.direction == "right":
            self.x += 4
        elif self.direction == "left":
            self.x -= 4
        # 方向判断
        if self.x+70 > 480:
            self.direction ="left"
        elif self.x < 0:
            self.direction = "right"
        if self.y < self.num_y:
            self.y += 3
        elif self.fire_bullet_count > 10:#已发射子弹数超过10，即向下移动
            self.y += 4


class Enemy2Plane(BasePlane):
    """enemy2的类"""
    def __init__(self, screen_temp):
        BasePlane.__init__(self, 2, screen_temp, 158, -246, "./feiji/enemy2.png", 5, HP_list[2])
        BasePlane.crate_images(self, "enemy2_down")
        self.direction = "right" #用来存储飞机默认显示方向
    #移动
    def move(self):
        if self.direction == "right":
            self.x += 5
        elif self.direction == "left":
            self.x -= 5
        # 方向判断
        if self.x+165 > 480:
            self.direction ="left"
        elif self.x < 0:
            self.direction = "right"
        if self.y < 0:
            self.y += 4
        elif self.fire_bullet_count > 25:#已发射子弹数超过25，即向下移动
            self.y += 3


class BaseBullet(Base):
    """子弹基类"""
    global bullet_damage_value
    def __init__(self, screen_temp, x, y, image_name, plane):
        Base.__init__(self, screen_temp, x, y, image_name)
        if plane:
            self.damage_value = bullet_damage_value[plane.plane_type]
    #子弹显示
    def display(self):
        self.screen.blit(self.image, (self.x, self.y))


class Bullet(BaseBullet):
    """hero子弹"""
    global bullet_type
    def __init__(self, screen_temp, x, y, plane):
        BaseBullet.__init__(self, screen_temp, x, y, "./feiji/"+bullet_type[plane.plane_type], plane)

    def move(self):
        self.y -= 16

    def judge(self):
        if self.y < 0:
            return True
        else:
            return False


class EnemyBullet(BaseBullet):
    """enemy子弹"""
    global bullet_type
    global plane_size
    def __init__(self, screen_temp, x, y, plane):
        BaseBullet.__init__(self, screen_temp, x+plane_size[plane.plane_type]["width"]/2, y+plane_size[plane.plane_type]["height"]/2, "./feiji/"+bullet_type[plane.plane_type], plane) #x, y 为子弹发射的位置

    def move(self):
        self.y += 7
    #越界判断
    def judge(self):
        if self.y > 852:
            return True
        else:
            return False


class supply_2_hero(BaseBullet):
    """hero补给"""
    def __init__(self, screen_temp, x, y, suppl_type_temp, speed_temp, s_HP):
        BaseBullet.__init__(self, screen_temp, x, y, "./feiji/"+supply_image[suppl_type_temp], None)
        self.speed = speed_temp
        self.supply_HP = s_HP
        self.supply_type = suppl_type_temp

    def move(self):
        self.y += self.speed
    #越界判断
    def judge(self):
        if self.y > 855:
            return True
        else:
            return False

#函数
def del_outWindow_bullet(plane):
    """删除plane的越界子弹"""
    bullet_list_out = []#越界子弹
    for bullet in plane.bullet_list:
        bullet.display()
        bullet.move()
        if bullet.judge(): #判断子弹是否越界
            bullet_list_out.append(bullet)
    #删除越界子弹
    if bullet_list_out:
        for bullet in bullet_list_out: 
            plane.bullet_list.remove(bullet)
    #如果为hero并且为三管齐发则判断炮管２３的子弹是否越界
    if plane.plane_type == 3 and (plane.barrel_2 or plane.barrel_3):
        barrel2_bullet_out = []#越界子弹
        barrel3_bullet_out = []#越界子弹
        #判断炮管２
        for bullet in plane.barrel_2:
            bullet.display()
            bullet.move()
            if bullet.judge(): #判断子弹是否越界
                barrel2_bullet_out.append(bullet)
        #删除越界子弹
        if barrel2_bullet_out:
            for bullet in barrel2_bullet_out: 
                plane.barrel_2.remove(bullet)
        #判断炮管３
        for bullet in plane.barrel_3:
            bullet.display()
            bullet.move()
            if bullet.judge(): #判断子弹是否越界
                barrel3_bullet_out.append(bullet)
        #删除越界子弹
        if barrel3_bullet_out:
            for bullet in barrel3_bullet_out: 
                plane.barrel_3.remove(bullet)

def del_plane(plane):
    """回收被击中的敌机的对象"""
    global hero
    global hit_score
    global enemy0_list
    global enemy1_list
    global enemy2_list
    if plane in enemy0_list: #回收对象为enemy0
        enemy0_list.remove(plane)
    elif plane in enemy1_list:
        enemy1_list.remove(plane)
    elif plane in enemy2_list:
        enemy2_list.remove(plane)
    elif plane == hero:#回收对象为hero
        hit_score = 0
        show_score_HP()
        hero = None

def del_supply(supply):
    """回收补给"""
    global blood_supply
    global bullet_supply
    if supply == blood_supply:#回收对象为血量补给
        blood_supply = None
    elif supply == bullet_supply:
        bullet_supply = None

def reborn():
    """Hero重生"""
    global hero
    global window_screen
    global hit_score
    hero = HeroPlane(window_screen)
    show_score_HP()
    hit_score = 0

#将最高分写入到文件
def max_score_2_file():
    global hit_score
    file = None
    try:
        file = open("./飞机大战得分榜.txt", 'r+')
    except Exception:
        file = open("./飞机大战得分榜.txt", 'w+')
    finally:
        if file.read():#判断文件是否为空
            file.seek(0, 0)#定位到文件开头
            file_score = eval(file.read())
            if hit_score > file_score:
                file.seek(0, 0)#定位到文件开头
                file.truncate()#清空文件内容
                file.write(str(hit_score))
        else:
            file.write(str(hit_score))
        file.close()

def create_enemy_plane():
    """生成敌机"""
    global window_screen
    global hit_score
    global enemy0_list
    global enemy0_maximum
    global enemy1_list
    global enemy1_maximum
    global enemy2_list
    global enemy2_maximum
    global HP_list

    if hit_score < 40:
        random_num = random.randint(1, 70)
        HP_list = [1, 20, 100, 20]
    elif hit_score < 450:
        random_num = random.randint(1, 60)
        HP_list = [1, 20, 120, 20]
    elif hit_score < 650:
        random_num = random.randint(1, 60)
        HP_list = [1, 30, 140, 20]
    elif hit_score < 850:
        random_num = random.randint(1, 55)
        HP_list = [2, 36, 160, 20]
    else:
        random_num = random.randint(1, 50)
        HP_list = [2, 40, 180, 20]
    random_appear_boss1 = random.randint(18, 28)
    random_appear_boss2 = random.randint(80, 100)
    #enemy0
    if (random_num == 20 or random == 40) and len(enemy0_list) < enemy0_maximum:
        enemy0_list.append(Enemy0Plane(window_screen))
    #enemy1
    if (hit_score >= random_appear_boss1 and (hit_score%random_appear_boss1) == 0) and len(enemy1_list) < enemy1_maximum:
        enemy1_list.append(Enemy1Plane(window_screen))
    #enemy2
    if (hit_score >= random_appear_boss2 and (hit_score%random_appear_boss2) == 0) and len(enemy2_list) < enemy2_maximum:
        enemy2_list.append(Enemy2Plane(window_screen))

def create_supply_2_hero(s_type):
    """为hero创建血量和弹药补给"""
    global window_screen
    global blood_supply
    global bullet_supply
    global enemy2_list
    if enemy2_list:#enemy2存在时补给概率更大
        random_limitation = 1201
    else:
        random_limitation = 2080
    random_supply = random.randint(1, random_limitation)
    if (random_supply%690) == 0 and s_type == 0:#血量补给
        blood_supply = supply_2_hero(window_screen, random.randint(0, 480-58), random.randint(-105, -95), s_type, 3, -3)# -补给类型, -速度, -补给血量值(用的是减法)
    elif (random_supply%300) == 0 and s_type == 1:#弹药补给
        bullet_supply = supply_2_hero(window_screen, random.randint(0, 480-60), random.randint(-115, -108), s_type, 3, 0)


def enemy_display_move_fire(enemy):
    """敌机的展示，移动，开火"""
    global window_screen
    global hero
    global plane_maximum_bullet

    enemy.display() #enemy展示
    enemy.move() #控制敌机的移动
    enemy.fire(plane_maximum_bullet[enemy.plane_type]) #敌机开火
    if hero:#飞机击中判断
        hero.isHitted(enemy, plane_size[hero.plane_type]["width"], plane_size[hero.plane_type]["height"]) #是否击中hero
        enemy.isHitted(hero, plane_size[enemy.plane_type]["height"], plane_size[enemy.plane_type]["height"]) #是否击中enemy

def supply_display_move(supply):
    """补给的判断"""
    supply.display()
    supply.move()
    if supply.judge():#越界回收
        del_supply(supply)

#得分, hp,单管,三管,三管子弹余量等显示
def show_score_HP():
    global window_screen
    global hero
    global hit_score
    global number_image
    global score_hp_image
    global one_or_three_barral
    global bullet_3_stock
    global max_score_image
    global boss_HP_image
    global enemy2_list
    #line
    window_screen.blit(line_image, (482, 445))
    if hero:#hero对象存在
        #贴score_hp
        window_screen.blit(score_hp_image, (480, 460))
        if not hero.is_three_bullet:#单管
            window_screen.blit(one_or_three_barral[0], (480, 560))
        else:#三管
            window_screen.blit(one_or_three_barral[1], (480, 560))
        window_screen.blit(bullet_3_stock, (480, 605))#贴三管子弹余量
        #贴得分
        hit_score_temp = cut_number(hit_score)#得到切割后的元组(百，十，个)
        window_screen.blit(number_image[hit_score_temp[0]], (600, 460))
        window_screen.blit(number_image[hit_score_temp[1]], (630, 460))
        window_screen.blit(number_image[hit_score_temp[2]], (660, 460))
        #贴hp
        HP_temp = cut_number(hero.HP)
        window_screen.blit(number_image[HP_temp[0]], (600, 510))
        window_screen.blit(number_image[HP_temp[1]], (630, 510))
        window_screen.blit(number_image[HP_temp[2]], (660, 510))
        #贴三管炮弹子弹数
        three_bullet_stock_temp = cut_number(hero.three_bullet_stock)
        window_screen.blit(number_image[three_bullet_stock_temp[0]], (605, 600))
        window_screen.blit(number_image[three_bullet_stock_temp[1]], (635, 600))
        window_screen.blit(number_image[three_bullet_stock_temp[2]], (665, 600))
    else:#hero对象不存在
        #贴score_hp，单管，三管子弹余量
        window_screen.blit(score_hp_image, (480, 460))
        window_screen.blit(one_or_three_barral[0], (480, 560))
        window_screen.blit(bullet_3_stock, (480, 605))#贴三管子弹余量
        #贴得分
        window_screen.blit(number_image[0], (600, 460))
        window_screen.blit(number_image[0], (630, 460))
        window_screen.blit(number_image[0], (660, 460))
        #贴hp
        window_screen.blit(number_image[0], (600, 510))
        window_screen.blit(number_image[0], (630, 510))
        window_screen.blit(number_image[0], (660, 510))
        #贴三管炮弹子弹数
        window_screen.blit(number_image[0], (605, 600))
        window_screen.blit(number_image[0], (635, 600))
        window_screen.blit(number_image[0], (665, 600))
    if enemy2_list:#贴enemy2的Hp
        #boss_hp
        window_screen.blit(boss_HP_image, (480, 640))
        enemy2_hp_temp = (0, 0, 0)
        if enemy2_list[0].HP > 0:#避免enemy2处于爆炸效果时血量为负值
            enemy2_hp_temp = cut_number(enemy2_list[0].HP)
            #贴enemy2_hp
            window_screen.blit(number_image[enemy2_hp_temp[0]], (590, 640))
            window_screen.blit(number_image[enemy2_hp_temp[1]], (620, 640))
            window_screen.blit(number_image[enemy2_hp_temp[2]], (650, 640))
    #line
    window_screen.blit(line_image, (482, 690))

#展示最大得分
def show_max_score():
    global number_image
    global window_screen
    file = None
    max_score = 0
    try:
        file = open("./飞机大战得分榜.txt", "r")
        max_score = eval(file.read())
    except Exception as e:
        raise
    finally:#贴最高得分
        max_score_temp = cut_number(max_score)
        window_screen.blit(number_image[max_score_temp[0]], (590, 700))
        window_screen.blit(number_image[max_score_temp[1]], (620, 700))
        window_screen.blit(number_image[max_score_temp[2]], (650, 700)) 

#切割数字成百十个位
def cut_number(number):
    if number > 999:
        number = 999
    hundred_num = round(number//100)#向下取整
    number %= 100
    ten_num = round(number//10)
    number %= 10
    single_num = round(number//1)
    return (hundred_num, ten_num, single_num)


#是否暂停
def pause():
    global is_pause
    global window_screen
    global pause_image
    global is_play_music
    while is_pause:
        pygame.mixer.music.pause()#暂停音乐
        #显示暂停图片
        window_screen.blit(pause_image, (170,402))#背景
        #更新图片
        pygame.display.update()
        time.sleep(0.1)#休眠0.1秒
        key_control()

#导入数字图片
def image_load():
    global number_image
    global score_hp_image
    global one_or_three_barral
    global bullet_3_stock
    global max_score_image
    global boss_HP_image
    global line_image
    global background
    global restart
    global exit_game
    global description
    global pause_image
    try:
        #暂停图片
        pause_image = pygame.image.load("./feiji/btn_finish.png")
        #右侧图片导入
        background = pygame.image.load("./feiji/background.png")
        restart = pygame.image.load("./feiji/restart_nor.png")
        exit_game = pygame.image.load("./feiji/quit_nor.png")
        description = pygame.image.load("./feiji/description.png")
        #数字图片导入
        for i in range(10):
            number_image.append(pygame.image.load("./feiji/number_"+str(i)+".png"))
        #score_hp导入
        score_hp_image = pygame.image.load("./feiji/score_hp.png")
        #单三管炮弹照片
        one_or_three_barral.append(pygame.image.load("./feiji/bullet_temp1.png"))#单管
        one_or_three_barral.append(pygame.image.load("./feiji/bullet_temp3.png"))#三管
        #三管炮弹子弹余量照片
        bullet_3_stock = pygame.image.load("./feiji/bullet_3_stock.png")
        #最高分
        max_score_image = pygame.image.load("./feiji/max_score.png")
        #boss_hp
        boss_HP_image = pygame.image.load("./feiji/boss_HP.png")
        #line_image
        line_image = pygame.image.load("./feiji/line.png")
    except Exception as e:
        raise

    
#显示背景图及右侧图片
def show_background_right_image():
    global background
    global restart
    global exit_game
    global description
    global max_score_image
    window_screen.blit(background, (0,0))#背景
    window_screen.blit(description, (482, 10))#操作说明图片
    window_screen.blit(max_score_image, (480, 705))#最大得分
    max_score_2_file()#可以同步写入破记录时的得分
    show_max_score()#可以同步展示破记录时的得分
    window_screen.blit(restart, (530, 760))#重新开始游戏图片
    window_screen.blit(exit_game, (532, 810))#退出游戏图片


#导入音乐
pygame.mixer.init()
def background_music_load():
    try:
        global hero_fire_music
        pygame.mixer.music.load("./music/PlaneWarsBackgroundMusic.mp3")#游戏背景音乐
        pygame.mixer.music.set_volume(0.3)#设置音量(0-1)
        pygame.mixer.music.play(-1)#循环播放
        hero_fire_music = pygame.mixer.Sound("./music/hero_fire.wav")#hero开火音乐
        hero_fire_music.set_volume(0.2)
    except Exception as e:
        raise
    

#键盘控制
def key_control():
    global hero
    global is_pause
    global hero_fire_music
    global plane_maximum_bullet
    global enemy0_list
    global enemy1_list
    global enemy2_list
    global blood_supply
    global bullet_supply
    global hit_score
    #获取事件，比如按键等
    for event in pygame.event.get():
        #判断是否是点击了退出按钮
        if event.type == QUIT:
            # print("exit")
            exit()
        #判断是否是按下了键
        elif event.type == KEYDOWN:
            #检测按键是否是left
            if hero:
                if event.key == K_LEFT:
                    hero.key_down(K_LEFT)
                #检测按键是否是right
                elif event.key == K_RIGHT:
                    hero.key_down(K_RIGHT)
                elif event.key == K_UP:
                    hero.key_down(K_UP)
                #检测按键是否是right
                elif event.key == K_DOWN:
                    hero.key_down(K_DOWN)
                #检测按键是否是s
                elif event.key == K_s:#保存或启用三管齐发子弹数
                    if hero.three_bullet_stock > 0:
                        if hero.is_three_bullet:#真变为假
                            hero.is_three_bullet = False
                        else:#假变为真
                            hero.is_three_bullet = True
                #检测按键是否是空格键
                elif event.key == K_SPACE and hero.HP:
                    hero.space_key_down(K_SPACE) #想space列表添加k_space
                #检测按键是否是b
                elif event.key == K_b:#自爆
                    hero.bomb()
            #检测按键是否是q
            if event.key == K_q:
                if is_pause:#真变为假
                    is_pause = False
                    pygame.mixer.music.unpause()#继续播放
                else:#假变为真
                    is_pause = True
            if event.key == K_r:
                reborn()
        #判断是否是松开了键
        elif event.type == KEYUP and hero:
            #检测松键是否是left
            if event.key == K_LEFT:
                hero.key_up(K_LEFT)
            #检测按键是否是right
            elif event.key == K_RIGHT:
                hero.key_up(K_RIGHT)
            #检测按键是否是up
            elif event.key == K_UP:
                hero.key_up(K_UP)
            #检测按键是否是down
            elif event.key == K_DOWN:
                hero.key_up(K_DOWN)
            #检测按键是否是space
            elif event.key == K_SPACE:
                hero.space_key_up(K_SPACE)
        #判断点击鼠标
        elif event.type == MOUSEBUTTONDOWN:#鼠标按下
            pressed_array = pygame.mouse.get_pressed()#获得鼠标点击类型[0,1,2] 左键,滑轮,邮件
            for index in range(len(pressed_array)):
                if pressed_array[index]:
                    if index == 0:#点击了鼠标左键
                        pos = pygame.mouse.get_pos()#得到鼠标的点击坐标
                        mouse_x = pos[0]
                        mouse_y = pos[1]
                        #通过鼠标点击坐标确定触发的事件类型
                        if mouse_x >170 and mouse_x < 310 and mouse_y > 402 and mouse_y < 450 and is_pause == True:#返回游戏事件
                            pygame.mixer.music.unpause()#继续播放
                            is_pause = False#不暂停
                        elif mouse_x >530 and mouse_x < 642 and mouse_y > 760 and mouse_y < 808:#重新开始游戏事件
                            #回收所有对对象
                            reborn()
                            enemy0_list = []
                            enemy1_list = []
                            enemy2_list = []
                            blood_supply = None
                            bullet_supply = None
                            # hit_score = 0
                            # main()
                        elif mouse_x >532 and mouse_x < 642 and mouse_y > 810 and mouse_y < 834:#退出游戏事件
                            exit()


def main():
    global window_screen
    global hero
    global hit_score
    global HP_list
    global blood_supply
    global bullet_supply
    global enemy0_list
    global enemy1_list
    global enemy2_list
    global number_image
    global score_hp_image
    global one_or_three_barral
    global bullet_3_stock
    global background
    global restart
    global exit_game
    global description
    global is_play_music

    print("Author: GuYongtao, E-mail: guyongtao@qq.com, Time: 2018/04/21")
    #得分过渡
    hit_score_temp = hit_score
    #背景色
    bg_color = (205, 205, 205)
    #1. 创建窗口
    window_screen = pygame.display.set_mode((695,852),0,32)
    #2. 创建一个背景图片
    try:
        image_load()#数字图片等导入
    except Exception:
        raise
    
    #3. 创建一个飞机对象
    hero = HeroPlane(window_screen)
    #4. 导入背景音乐
    background_music_load()
    #标题
    pygame.display.set_caption('飞机大战')
    while True:
        #背景色填充
        window_screen.fill(bg_color)
        #得分更新
        if hit_score >= 999:
            hit_score = 999
        if hit_score > hit_score_temp and hero:
            hit_score_temp = hit_score
            show_score_HP()
        elif hit_score < hit_score_temp:
            hit_score_temp = 0
        #创建敌机
        create_enemy_plane()
        #创建补给
        #血量补给, 0-补给类型, 3-补给速度, -3-补给HP
        if not blood_supply:
            create_supply_2_hero(0)
        #弹药补给
        if not bullet_supply:
            create_supply_2_hero(1)
        #显示背景及右侧图片
        show_background_right_image()

        #hero
        if hero:
            hero.display() #hero展示
            if hero:
                hero.press_move()#持续移动
                hero.press_fire()#持续开火
                hero.move_limit() #hero移动范围判断
        #blood_supply
        if blood_supply:
            supply_display_move(blood_supply)
        #bullet_supply
        if bullet_supply:
            supply_display_move(bullet_supply)
        #是否吃到补给
        if hero and blood_supply:
            hero.supply_hitted(blood_supply, plane_size[hero.plane_type]["width"], plane_size[hero.plane_type]["height"])
        if hero and bullet_supply:
            hero.supply_hitted(bullet_supply, plane_size[hero.plane_type]["width"], plane_size[hero.plane_type]["height"])
        #enemy0
        if enemy0_list:
            for enemy0 in enemy0_list:
                enemy_display_move_fire(enemy0)
        #enemy1
        if enemy1_list:
            for enemy1 in enemy1_list:
                enemy_display_move_fire(enemy1)
        #enemy2
        if enemy2_list:
            for enemy2 in enemy2_list:
                enemy_display_move_fire(enemy2)
        #得分, HP显示
        show_score_HP()
        #是否暂停
        pause()
        #更新图片
        pygame.display.update()
        #调用键盘控制
        key_control()
        #系统睡眠时间(电脑配置不同，影响游戏流畅运行度)
        time.sleep(0.04)

if __name__ == "__main__":
    main()
