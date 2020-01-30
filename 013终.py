import gc
import random

import pygame

import Constants


# 玩家飞机精灵类
class HeroPlane(pygame.sprite.Sprite):
    def __init__(self, screen):
        # 调用父类初始化方法
        # pygame.sprite.Sprite.__init__(self)
        super().__init__()
        # 窗口
        self.screen = screen
        # 一个玩家飞机图片
        self.image = pygame.image.load('./feiji/hero2.png')
        # 飞机矩形区域对象
        self.rect = self.image.get_rect()
        # 左上角坐标
        self.rect.topleft = [512 / 2 - 116 / 2, 600]
        # 飞机的速度
        self.speed = 15
        # 一个精灵组 存放所有的子弹精灵
        self.bullets = pygame.sprite.Group()
        # 血量 初始100
        self.blood_value = 100

        # 标记玩家飞机是否over
        self.is_remove = False

        # 显示爆炸图片的 索引 从0开始
        self.mIndex = 0

        # 存放爆炸图片 的列表
        self.bomb_mImages = []

        for v in range(1, 15):
            # 把所有图片 存到列表里 每个图片 存2次
            self.bomb_mImages.append(pygame.image.load('./feiji/image ' + str(v) + '.png'))
            self.bomb_mImages.append(pygame.image.load('./feiji/image ' + str(v) + '.png'))

    def kill_blood(self, kill_value=10):
        """血量减少"""
        self.blood_value -= kill_value
        print('被打中了，血量还剩%s' % self.blood_value)
        if self.blood_value <= 0:
            # 避免血量负值
            self.blood_value = 0
            # 血量<=0 设置is_remove 为True
            self.is_remove = True

    def key_control(self):
        """按键监听 操作飞机上下左右和发子弹"""
        # 监听键盘事件
        key_pressed = pygame.key.get_pressed()  # 注意这种方式是能够检测到一直按下不松开的键盘

        if key_pressed[pygame.K_w] or key_pressed[pygame.K_UP]:
            # top值如果小于0 就到了最顶部 不要再移动了
            if self.rect.top > 3:
                self.rect.top -= self.speed
        if key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]:
            if self.rect.bottom <= 768:
                self.rect.bottom += self.speed
        if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
            if self.rect.left > 0:
                self.rect.left -= self.speed
        if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
            if self.rect.right < 520:
                self.rect.right += self.speed
        if key_pressed[pygame.K_SPACE]:
            # print("space")
            # 创建3个子弹
            bullet1 = Bullet(self.screen, self.rect.left, self.rect.top, 1)
            bullet2 = Bullet(self.screen, self.rect.left, self.rect.top, 2)
            bullet3 = Bullet(self.screen, self.rect.left, self.rect.top, 3)
            # 添加到精灵组
            self.bullets.add(bullet1, bullet2, bullet3)

    def bomb(self):
        print('玩家飞机爆炸中')
        """显示爆炸图片"""
        self.screen.blit(self.bomb_mImages[self.mIndex], self.rect)
        self.mIndex += 1
        print('mIndex', self.mIndex)
        if self.mIndex >= len(self.bomb_mImages):
            # 播放到了最后 爆炸结束 返回True
            return True

    def update(self):
        if self.is_remove:
            print('玩家飞机挂掉')
            # 如果玩家飞机挂掉
            if self.bomb():
                # 爆炸结束
                print('爆炸结束')
                self.rect.topleft = [-200, -200]
                # 开启倒计时
                pygame.time.set_timer(Constants.game_over_id, 1000)
                # 把玩家飞机指向None 停止update
                manager.hero = None
        else:
            self.key_control()
            self.display()

    def display(self):
        # if self.blood_value <= 0:
        #     # 如果血量小于0 移出窗口
        #     self.rect.topleft = [-200, -200]

        # 把飞机显示到窗口上  飞机 116*100
        self.screen.blit(self.image, self.rect)
        # 更新精灵组里的子弹位置
        self.bullets.update()
        # 精灵组所有子弹显示到窗口
        self.bullets.draw(self.screen)


# 玩家子弹类
class Bullet(pygame.sprite.Sprite):
    # path_num表示散弹中 子弹是哪一个
    def __init__(self, screen, planex, planey, path_num):
        # 调用父类初始化方法
        # pygame.sprite.Sprite.__init__(self)
        super().__init__()
        # 窗口
        self.screen = screen
        # 一个子弹图片
        self.image = pygame.image.load('./feiji/bullet_10.png')
        # 子弹矩形区域对象
        self.rect = self.image.get_rect()
        # 子弹左上角坐标
        self.rect.topleft = [planex + 48, planey - 20]
        # 子弹的速度
        self.speed = 15
        # path_num表示散弹中 子弹是哪一个
        self.path_num = path_num

    def update(self):
        """修改子弹坐标"""
        self.rect.top -= self.speed
        if self.rect.bottom < 0:
            # 子弹已经移出了屏幕上方 这时把子弹从精灵组删除
            self.kill()
        if self.path_num == 1:
            pass
        elif self.path_num == 2:
            # 如果等于2 就是左侧的散弹
            self.rect.left -= 10
        elif self.path_num == 3:
            # 如果等于3 就是右侧的散弹
            self.rect.right += 10


# 敌机精灵类
class EnemyPlane(pygame.sprite.Sprite):
    # 创建类属性 存放所有飞机的所有的子弹
    all_bullets = pygame.sprite.Group()

    def __init__(self, screen):
        # 调用父类初始化方法
        # pygame.sprite.Sprite.__init__(self)
        super().__init__()
        # 窗口
        self.screen = screen
        # 来一个随机数
        self.num = random.randint(1, 7)
        # 一个玩家飞机图片
        self.image = pygame.image.load('./feiji/img-plane_' + str(self.num) + '.png')
        # 飞机矩形区域对象
        self.rect = self.image.get_rect()
        # 左上角坐标 x坐标随机
        self.rect.topleft = [random.randint(0, 412), 0]
        # 飞机的速度
        self.speed = 3
        # 一个精灵组 存放所有的子弹精灵
        self.bullets = pygame.sprite.Group()
        # 敌机的左右方向 默认一开始向右
        self.direction = 'right'
        # 子弹的精灵组
        self.bullets = pygame.sprite.Group()
        # 标记敌机是否被击中 是否要删除
        self.is_remove = False

        # 显示爆炸图片的 索引 从0开始
        self.mIndex = 0

        # 存放爆炸图片 的列表
        self.bomb_mImages = []

        for v in range(1, 14):
            # 把所有图片 存到列表里 每个图片 存2次
            self.bomb_mImages.append(pygame.image.load('./feiji/image ' + str(v) + '.png'))
            self.bomb_mImages.append(pygame.image.load('./feiji/image ' + str(v) + '.png'))

        # 记录爆炸位置
        self.x = 0
        self.y = 0

    def auto_move(self):
        """自动移动"""
        # 向下移动
        self.rect.bottom += self.speed
        # 如果飞机向下移出边界 删除它
        if self.rect.top > Manager.height:
            self.kill()

        # 按不同方向左右移动
        if self.direction == 'right':
            self.rect.right += 6
        elif self.direction == 'left':
            self.rect.right -= 6

        # 超出左右边界 更改移动方向
        if self.rect.right >= Manager.width:
            self.direction = 'left'
        if self.rect.left <= 0:
            self.direction = 'right'

    def auto_fire(self):
        # 用一个随机数
        num = random.randint(1, 40)
        # 判断如果等于1就发射一个子弹 ，降低了概率
        if num == 5:
            # 生成敌机子弹
            bullet = EnemyBullet(self.screen, self.rect.left, self.rect.top)
            # 添加到精灵组
            self.bullets.add(bullet)
            # 把子弹添加到类的all_bullets里 用来碰撞检测
            EnemyPlane.all_bullets.add(bullet)

    def bomb(self):
        """显示爆炸图片"""
        if self.mIndex >= len(self.bomb_mImages):
            # 播放到了最后 爆炸结束 返回True
            return True
        self.screen.blit(self.bomb_mImages[self.mIndex], (self.x, self.y))
        self.mIndex += 1

    def update(self):
        if self.is_remove:
            if self.rect.left != -200:
                # 记录爆炸时的位置
                self.x = self.rect.left
                self.y = self.rect.top
            # 如果已经被击中 把飞机移除窗口 防止继续碰撞检测
            self.rect.left = -200
            self.rect.top = -200
            # 显示爆炸效果
            if self.bomb() and not self.bullets:
                # 如果爆炸结束  把自己从精灵组删除
                self.kill()
        else:
            # 移动
            self.auto_move()
            # 开火
            self.auto_fire()
            # 显示
            self.display()

        self.bullet_show()

    def display(self):
        # 把飞机显示到窗口上  飞机 116*100
        self.screen.blit(self.image, self.rect)

    def bullet_show(self):
        if self.bullets:
            # 敌机子弹更新
            self.bullets.update()
            # 敌机子弹显示
            self.bullets.draw(self.screen)


# 敌机子弹类
class EnemyBullet(pygame.sprite.Sprite):
    # path_num表示散弹中 子弹是哪一个
    def __init__(self, screen, x, y):
        # 调用父类初始化方法
        # pygame.sprite.Sprite.__init__(self)
        super().__init__()
        # 窗口
        self.screen = screen
        # 来一个随机数
        self.num = random.randint(1, 7)
        # 一个子弹图片
        self.image = pygame.image.load('./feiji/bullet_' + str(self.num) + '.png')
        # 子弹矩形区域对象
        self.rect = self.image.get_rect()
        # 子弹左上角坐标
        self.rect.topleft = [x + 40, y + 60]
        # 子弹的速度
        self.speed = 10

    def update(self):
        """修改子弹坐标"""
        self.rect.bottom += self.speed
        # 如果子弹向下移出边界 删除它
        if self.rect.top > Manager.height:
            self.kill()


# 游戏音乐
class GameSound(object):
    def __init__(self):
        pygame.mixer.init()  # 音乐模块初始化
        pygame.mixer.music.load("./feiji/Jamesketed.mp3")
        pygame.mixer.music.set_volume(0.5)  # 声音大小 一半

        self.__bomb = pygame.mixer.Sound("./feiji/bomb.wav")

    def playBackgroundMusic(self):
        # 开始播放背景音乐 -1表示一直重复播放
        pygame.mixer.music.play(-1)

    def playBombSound(self):
        pygame.mixer.Sound.play(self.__bomb)  # 爆炸音乐


# 背景图
class GameBackground(object):
    # 初始化地图
    def __init__(self, screen):
        self.mImage1 = pygame.image.load("./feiji/img_bg_level_2.jpg")
        self.mImage2 = pygame.image.load("./feiji/img_bg_level_2.jpg")
        # 窗口
        self.screen = screen
        # 辅助移动地图
        self.y1 = 0
        self.y2 = -Manager.height  # -768

    def update(self):
        self.move()
        self.draw()

    # 移动地图
    def move(self):
        self.y1 += 2
        self.y2 += 2
        if self.y1 >= Manager.height:
            self.y1 = 0
        if self.y2 >= 0:
            self.y2 = -Manager.height

    # 绘制地图
    def draw(self):
        self.screen.blit(self.mImage1, (0, self.y1))
        self.screen.blit(self.mImage2, (0, self.y2))


# 管理类
class Manager:
    hero: HeroPlane
    # 创建宽高
    width = 512
    height = 768

    def __init__(self):
        # pygame初始化  否则找不到字体文件
        pygame.init()

        # 1 创建一个窗口 参数1是宽高，参数2 附加参数 参3是颜色深度
        self.screen = pygame.display.set_mode((self.width, self.height), 0, 32)

        # 2创建背景图的对象
        # self.background = pygame.image.load('./feiji/img_bg_level_5.jpg')
        self.background = GameBackground(self.screen)

        # 创建飞机对象
        self.hero = HeroPlane(self.screen)

        # 创建时钟对象
        self.clock = pygame.time.Clock()

        # 敌机的精灵组
        self.enemys = pygame.sprite.Group()

        # 初始化音效对象
        self.sound = GameSound()
        # 定义分数属性
        self.score = 0
        # 倒计时时间
        self.over_time = 3

    def exit(self):
        # 执行退出代码
        pygame.quit()
        # 程序的退出
        exit()

    def new_enemy(self):
        # 创建敌机对象
        enemy = EnemyPlane(self.screen)
        # 添加到精灵组
        self.enemys.add(enemy)

    def drawText(self, text, x, y, textHeight=30, fontColor=(255, 255, 255), backgroudColor=None):

        # 通过字体文件获得字体对象  参数1 字体文件 参数2 字体大小
        font_obj = pygame.font.Font('./feiji/baddf.ttf', textHeight)
        # 1文字  2是否抗锯齿 3文字颜色 4背景颜色
        text_obj = font_obj.render(text, True, fontColor, backgroudColor)  # 配置要显示的文字
        # 获得要显示的对象的rect
        text_rect = text_obj.get_rect()
        # 设置显示对象的坐标
        text_rect.topleft = (x, y)
        # 绘制字 到指定区域  参1是文字对象 参2 矩形对象
        self.screen.blit(text_obj, text_rect)

    def game_over_timer(self):
        """执行倒计时"""
        self.over_time -= 1
        if self.over_time == 0:
            # 停止倒计时
            pygame.time.set_timer(Constants.game_over_id, 0)
            # 重新开始游戏
            self.start_game()

    def show_over_text(self):
        print('self.over_time', self.over_time)
        # 游戏结束 显示倒计时时间
        self.drawText('gameover %d' % self.over_time, 0, Manager.height / 2, textHeight=50,
                      fontColor=[0, 0, 0])

    def start_game(self):
        global manager
        # 情况敌机子弹的精灵组
        EnemyPlane.all_bullets.empty()
        manager = Manager()
        # 垃圾回收 提示python解释器 要回收了
        gc.collect()
        manager.main()

    def main(self):
        # 播放背景音乐
        self.sound.playBackgroundMusic()

        # 参1eventid是事件id，自己定义（0 - 32之间）不要和已用的pygame的其它事件id冲突，
        # 参2是定时事件的间隔时间，单位是毫秒
        pygame.time.set_timer(Constants.new_enemy, 500)

        while True:
            # 控制每s执行的次数
            self.clock.tick(60)
            # 获取事件 并且处理
            for event in pygame.event.get():
                # 判断事件的类型是否是退出
                if event.type == pygame.QUIT:
                    # 退出
                    self.exit()
                elif event.type == Constants.new_enemy:
                    # 等于20 说明定时器生效 添加一个敌机
                    # print('添加一个敌机')
                    self.new_enemy()
                elif event.type == Constants.game_over_id:
                    print('倒计时 33333')
                    # 显示倒计时时间
                    self.game_over_timer()

            # 3把背景图显示到窗口上
            # self.screen.blit(self.background, (0, 0))
            self.background.update()

            self.drawText('分数：%s' % self.score, 0, 0)

            if self.hero:
                self.drawText('血量：%s' % self.hero.blood_value, 0, 30)
                # 更新飞机
                self.hero.update()
                # if self.hero.blood_value <= 0 and not self.hero.bullets.sprites():
                #     # 把玩家飞机引用指向None 尽快释放
                #     self.hero = None
            else:
                self.drawText('血量：0', 0, 30)

            # 更新 敌机
            self.enemys.update()

            # 如果飞机已经挂掉 就一直显示倒计时
            if not self.hero:
                # 显示倒计时
                self.show_over_text()

            # 判断 玩家飞机 和敌机是否都存在  self.enemys.sprites()返回精灵组对应的精灵列表
            if self.hero and self.enemys.sprites():
                # 碰撞检测 返回的碰撞到的 敌机列表
                collide_enemys = pygame.sprite.spritecollide(self.hero, self.enemys, False, pygame.sprite.collide_mask)
                if collide_enemys:
                    # 如果列表不为空 说明碰到了敌机
                    print('碰到了敌机')
                    # 爆炸声音
                    self.sound.playBombSound()
                    self.hero.kill_blood(100)
                    for enemy_item in collide_enemys:
                        # 标记敌机已经被撞到
                        enemy_item.is_remove = True

            # 判断 玩家飞机 和 玩家飞机的子弹 和 敌机是否都存在
            if self.hero and self.hero.bullets and self.enemys:
                # 检测玩家飞机的子弹 和敌机的碰撞
                # 返回是个字典 格式{<Bullet sprite(in 0 groups)>: [<EnemyPlane sprite(in 0 groups)>]}
                # {碰撞的子弹1:[打中的敌机1，打中的敌机2]，碰撞的子弹2:[打中的敌机1，打中的敌机5]}
                collode_dict = pygame.sprite.groupcollide(self.hero.bullets, self.enemys, True, False,
                                                          pygame.sprite.collide_mask)

                # 1多个子弹打中同一个飞机  # 2不同子弹 打中不同飞机 # 所有加分值时 要去除重复的敌机

                # print(collode_dict)
                if collode_dict:
                    # 爆炸声音
                    self.sound.playBombSound()

                    print(self.score)
                    # 用一个集合 添加敌机 去除重复的
                    enemyset = set()
                    # 获取所有打中的敌机列表，然后遍历
                    for v_enemys in collode_dict.values():
                        # 遍历敌机列表
                        for enemy_item in v_enemys:
                            # print(id(enemy_item))
                            enemyset.add(enemy_item)
                            # 标记敌机已经被击中
                            enemy_item.is_remove = True

                    # 碰撞后 +10分*集合里敌机的数量
                    self.score += 10 * len(enemyset)

            # 判断 玩家飞机 和 和 敌机子弹
            if self.hero and EnemyPlane.all_bullets:
                # 检测玩家 和敌机子弹的碰撞
                collide_bullets = pygame.sprite.spritecollide(self.hero, EnemyPlane.all_bullets, True,
                                                              pygame.sprite.collide_mask)
                if collide_bullets:
                    # 如果碰到了 就减少10*子弹数量的血量
                    self.hero.kill_blood(10 * len(collide_bullets))

            # 2 显示窗口
            pygame.display.update()


if __name__ == '__main__':
    manager = Manager()
    manager.main()
