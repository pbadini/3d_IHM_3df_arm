import math
from tkinter import *


# classe criada apenas para ajudar em algumas contas de vetores 2d
class Vector2d():
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __sub__(self, other):
        return Vector2d(self.x - other.x, self.y - other.y)  

    def __add__(self, other):
        return Vector2d(self.x + other.x, self.y + other.y)   
        

# clase que garda as caracteristicas de cada segmento do robo
# tais como: tamanho, os pontos de inicio e de fim.
class Arm():
    def __init__(self, length, **kwargs):
        self.length = length
        self.begin = Vector2d(0,0)
        self.end = Vector2d(0,0)
        self.base = Vector2d(0,0)
        self.angle = 0
        self.angle2 = 0
        self.parent = None

        if 'angle' in kwargs:
            self.angle = kwargs['angle']
            
        if 'base_x' in kwargs and 'base_y' in kwargs:
            self.base = Vector2d(kwargs['base_x'], kwargs['base_y'])
            self.begin = Vector2d(kwargs['base_x'], kwargs['base_y'])
        
        # Ter um pai significa que  o segmento nao está ligado diretamente ao chao
        # e sim ligado a outro segmento. Esse segmento no qual ele está ligado é o seu pai
        if 'parent' in kwargs:
            self.parent = kwargs['parent']
            self.base = self.parent.base
            self.begin = self.parent.end
        
        self.findEnd()


    def findEnd(self):
        #calcula o ponto x e y do final do segmento do robo com base na posição inicial, tamanho e angulo do segmento.
        self.end.x = self.begin.x + self.length * math.cos(self.angle) * math.cos(self.angle2)
        self.end.y = self.begin.y + self.length * math.sin(self.angle)
        



    def update(self, teta, angle2):
        if self.parent:
            self.angle = teta + self.parent.angle
            self.begin.x = self.parent.end.x
            self.begin.y = self.parent.end.y
        else:
            self.angle = teta

        self.angle2 = angle2
        self.findEnd()

    def updateWithoutAngle(self, theta):
        if self.parent:
            self.angle += theta
            self.begin.x = self.parent.end.x
            self.begin.y = self.parent.end.y
        else:
            self.angle = theta
        
        self.findEnd()
        
# o Robo é a clase que contém um grupo de segmentos e se encarrega de plota-los no canvas.       
class Robot():
    def __init__(self, canvas, arm_size, base_x, base_y, **kwargs):
        self.canvas = canvas
        self.base = Vector2d(base_x, base_y)
        self.target = Vector2d(0,0)
        self.length = arm_size * 2
        self.angle = 0
        if 'color' in kwargs:
            color = kwargs['color']
        else:
            color = 'black'

        if 'width' in kwargs:
            width = kwargs['width']
        else:
            width = 5


        # Vetor de "Arms", a classe descrita anterioramente
        self.arms = []
        self.arms.append(Arm(arm_size, base_x = base_x, base_y = base_y))
        self.arms.append(Arm(arm_size, parent = self.arms[0]))

        self.segments = []
        self.bearings = []

        # Vetor de linas e circulos, que serão usados para plotas o robo na tela
        for i in range(2):
            self.segments.append(self.canvas.create_line(self.arms[i].begin.x, self.arms[i].begin.y,
                                                        self.arms[i].end.x, self.arms[i].end.y, fill = color, width = width))
            self.bearings.append(self.canvas.create_oval(self.arms[i].begin.x + 10, self.arms[i].begin.y + 10,
                                                        self.arms[i].begin.x - 10, self.arms[i].begin.y - 10, fill = color, width = width))

        size = 60
        # Plot da Base do robo
        self.support = self.canvas.create_rectangle(self.base.x + size/2, self.base.y + size, self.base.x - size/2, self.base.y, fill = 'blue')

    # A função que atualização a posição target do robo e atualiza o plot dele na tela
    def updateTarget(self, x, y):
        angle = self.inverseKinematics(x, y) #Função que calcula os ângulos do robo com base na posição x e y 
        self.target.x = x
        self.target.y = y
        
        # atualiza o plot na tela
        for i in range(len(self.arms)):
            self.arms[i].update(angle[i], self.angle)
            self.canvas.coords(self.segments[i], self.arms[i].begin.x, self.arms[i].begin.y, self.arms[i].end.x, self.arms[i].end.y)
            self.canvas.coords(self.bearings[i], self.arms[i].begin.x + 10, self.arms[i].begin.y + 10, self.arms[i].begin.x - 10, self.arms[i].begin.y - 10)

    #Função que faz a cinemática inversa do robo, calculando os ângulos de suas juntas com base na posição x e y 
    def inverseKinematics(self, x, y):
        target = Vector2d(x, y)
        target_to_base = target - self.base
        
        target_distance = abs(target_to_base)



        if target_distance > self.length:
            target_distance = self.length**2
        else:
            target_distance = target_distance**2

        cos_teta_2 = (target_distance - self.arms[0].length**2 - self.arms[1].length**2)/(2*self.arms[0].length*self.arms[1].length)

        beta = math.atan2(target_to_base.y, target_to_base.x)
        if x > 0:
            teta_2 = - math.atan2(-math.sqrt(1 - cos_teta_2**2), cos_teta_2)
            cos_phi = (target_distance + self.arms[0].length**2 - self.arms[1].length**2)/(2*math.sqrt(target_distance)*self.arms[0].length)
            phi = math.atan2(math.sqrt(1 - cos_phi**2), cos_phi)
            teta_1 = beta - phi
        else:
            teta_2 = math.atan2(-math.sqrt(1 - cos_teta_2**2), cos_teta_2)
            cos_phi = (target_distance + self.arms[0].length**2 - self.arms[1].length**2)/(2*math.sqrt(target_distance)*self.arms[0].length)
            phi = math.atan2(math.sqrt(1 - cos_phi**2), cos_phi)
            teta_1 = beta + phi

        return [teta_1, teta_2]


    
    # função que rotacionando o robo na tela.
    def rotate(self, size):
        angle = math.pi * size / (self.length * 50)
        self.angle += angle
        self.updateTarget(self.target.x, self.target.y)


    def updateAngle(self, angle):
        self.angle = angle
        self.updateTarget(self.target.x, self.target.y)

    # função que atualiza apenas o angulo da primeira junta do robo
    def updateArm1(self, angle):
        aux = angle - self.arms[0].angle
        self.arms[0].update(angle, self.angle)
        self.arms[1].updateWithoutAngle(aux)
        self.target.x = self.arms[1].end.x
        self.target.y = self.arms[1].end.y
        for i in range(len(self.arms)):
            self.canvas.coords(self.segments[i], self.arms[i].begin.x, self.arms[i].begin.y, self.arms[i].end.x, self.arms[i].end.y)
            self.canvas.coords(self.bearings[i], self.arms[i].begin.x + 10, self.arms[i].begin.y + 10, self.arms[i].begin.x - 10, self.arms[i].begin.y - 10)

    # função que atualiza apenas o angulo da segunda junta do robo
    def updateArm2(self, angle):
        self.arms[1].update(angle, self.angle)
        self.target.x = self.arms[1].end.x
        self.target.y = self.arms[1].end.y
        self.canvas.coords(self.segments[1], self.arms[1].begin.x, self.arms[1].begin.y, self.arms[1].end.x, self.arms[1].end.y)

