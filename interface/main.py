import math
from os import close, stat
from tkinter import *
from robot import Robot
from tkinter import ttk
import serial
import serial.tools.list_ports

# Iniciando a serial com parametros inciais
ser = serial.Serial(timeout = None)
ser.baudrate = 115200
ser.port = 'COM25'


# Variável global usada para saber a posição do mouse 
# quando o botão direito do mouse foi clicado
initial_x = 0

# Variável global usada para saber quando o botão 
# esquerdo do mouse está sendo clicado
clicking = False


# Rotina de quando o botão esquerdo do mouse é clicado
#  sobre o canvas do robo
def left_click(event):
  global clicking
  clicking = True


# Rotina de quando o botão esquerdo do mouse é solto
#  sobre o canvas do robo
def left_release(event):
  global clicking
  clicking = False


# Rotina chamada quando o mouse se mexe com o botão esquerdo 
# acionado sobre o canvas do robo
def left_motion(event):
  # A variavel que descreve o angulo de rotação do robo é zerada
  # para que o braço possa atingir o target com mais facilidade
  robot.angle = 0


  # Chama-se a função que atualiza o target do braço para a posição
  # atual do mouse e também atualiza os ângulos das juntas do robo 
  # com base na cinemática inversa.
  robot.updateTarget(event.x, event.y)

  # Atualiza-se os slider com base nos novos ângulos da juntas
  sliders['rotate'].set(0)
  sliders['arm1'].set(robot.arms[0].angle + math.pi/2)
  sliders['arm2'].set(robot.arms[1].angle - robot.arms[0].angle)


  # Tenta escrever na serial os novos angulos, caso ela esteja ligada
  try:
    serial_msg = str(robot.angle) + ';' + str(robot.arms[0].angle) + ';' + str(robot.arms[1].angle) + ';'
    ser.write(serial_msg.encode())
  except:
    pass


# Rotina de quando o botão direito do mouse é clicado
# sobre o canvas do robo 
def right_click(event):
  global initial_x, clicking
  # salva a o posição de onde começou o click
  initial_x = event.x
  clicking = True

# Rotina de quando o botão direito do mouse é solto
# sobre o canvas do robo
def right_release(event):
  global clicking
  clicking = False

# Rotina de quando o botão esquerdo do mouse é movido
# sobre o canvas do robo
def right_motion(event):
  global initial_x

  # Chama-se a funciona que rotaciona o robo com base 
  # na posição inicial do mouse e na atual
  robot.rotate(event.x - initial_x)

  # Tenta escrever na serial os novos angulos, caso ela esteja ligada
  try:
    serial_msg = str(robot.angle) + ';' + str(robot.arms[0].angle) + ';' + str(robot.arms[1].angle) + ';'
    ser.write(serial_msg.encode())
  except:
    pass


# Rotina chamada quando se movimenta o slider de rotação do robo
def slide_rotate(var):
  # aqui a logica da booleana "clicking" se faz necessária, 
  # pois quando o evento left_motion() modifica o valor do 
  # slider essa funcão era chamada, fazendo com que o 
  # programa não funcionasse corretamente.
  if not clicking:

    # Chama-se a funciona que rotaciona o robo com base 
    # na posição inicial do mouse e na atual
    robot.updateAngle(sliders['rotate'].get())
    try:
      # Tenta escrever na serial os novos angulos, caso ela esteja ligada
      serial_msg = str(robot.angle) + ';' + str(robot.arms[0].angle) + ';' + str(robot.arms[1].angle) + ';'
      ser.write(serial_msg.encode())
    except:
      pass

# Rotina chamada quando se movimenta o slider de rotação da primeira junta do robo
def slide_arm1(var):
  if not clicking:
    # Chama-se a funciona que rotaciona a primeira junta do robo 
    # o pi/2 da conta é apenas um offset para ajustar o slider e o braço
    robot.updateArm1(sliders['arm1'].get() - math.pi/2);

    try:
      # Tenta escrever na serial os novos angulos, caso ela esteja ligada
      serial_msg = str(robot.angle) + ';' + str(robot.arms[0].angle) + ';' + str(robot.arms[1].angle) + ';'
      ser.write(serial_msg.encode())
    except:
      pass

# Rotina chamada quando se movimenta o slider de rotação da segunda junta do robo
def slide_arm2(var):
  if not clicking:
    # Chama-se a funciona que rotaciona a segunda junta do robo 
    # o pi/2 da conta é apenas um offset para ajustar o slider e o braço
    robot.updateArm2(sliders['arm2'].get());
    try:
      # Tenta escrever na serial os novos angulos, caso ela esteja ligada
      serial_msg = str(robot.angle) + ';' + str(robot.arms[0].angle) + ';' + str(robot.arms[1].angle) + ';'
      ser.write(serial_msg.encode())
    except:
      pass

# Rotina chamada quando clica no botão vermelho na tela
def emergency_stop():
  try:
    # Tenta escrever na serial o comando de stop, caso ela esteja ligada
    ser.write(b'STOP')
  except:
    pass
  
# Rotina chamada quando clica-se no botão de set baudrate
def set_baud():
  global ser
  try:
    # passa o valor escrito no texto para o a variavel ser.baudrate
    ser.baudrate = int(baudrate_text.get())
  except:
    print('error setting baud')

# Rotina chamada quando se clica no botão close serial
def close_serial():
  global ser
  # ativa todos os botões novamente, desativando o botão de close
  ser.close()
  open_serial_button.config(state = NORMAL)
  baudrate_button.config(state = NORMAL)
  baudrate_text.config(state = NORMAL)
  com_combobox.config(state = NORMAL)
  close_serial_button.config(state = DISABLED)

# Rotina chamada quando se clica no botão open serial
def open_serial():
  # desativa todos os botões de condiguração, ativando o botão de close
  global ser
  ser.open()
  open_serial_button.config(state = DISABLED)
  baudrate_button.config(state = DISABLED)
  baudrate_text.config(state = DISABLED)
  com_combobox.config(state = DISABLED)
  close_serial_button.config(state = NORMAL)

# Rotina chamada quando se clica para abrir a opções de portas COM
def choosing_com():
  # Pesquisa todas as portas COM disponiveis no computador e 
  # mostra elas ao usuário
  com_combobox["values"] =list(serial.tools.list_ports.comports())

# Rotina chamada quando se seleciona uma porta COM
def selected_com(event):
  # Seta a porta COM
  com = com_combobox.get().split(' ')
  ser.port = com[0]

# Variáveis

# Iniciando a página
root = Tk()

# tamanho e largura da página
w = 600
h = 500

# criando o canvas do robo
canvas =  Canvas(root, width=w, heigh=h, bg='white')

# criando o robo
robot = Robot(canvas, 150, w/2, 3*h/4)

# criando os sliders
sliders = {
  'rotate' : Scale(root, from_= - math.pi, to= math.pi, orient=HORIZONTAL, command = slide_rotate, length = 300, resolution = 0.01),
  'arm1' : Scale(root, from_= - math.pi, to= math.pi, orient=HORIZONTAL, command = slide_arm1, length = 300, resolution = 0.01),
  'arm2': Scale(root, from_= - math.pi, to= math.pi, orient=HORIZONTAL, command = slide_arm2, length = 300, resolution = 0.01)
}

# criando os as labels
labels = {
  'rotate' : Label(root, text = 'Ângulo de Rotação'),
  'arm1' : Label(root, text = 'Ângulo da Base'),
  'arm2': Label(root, text = 'Ângulo da Ponta')
}
# Criando os botoa da interface
emergency_button = Button(root, text = "Stop", command = emergency_stop, anchor = W, bg = 'red')
emergency_button.configure(width = 5, activebackground = "red")
emergency_window = canvas.create_window(10, 10, anchor=NW, window=emergency_button)
open_serial_button = Button(root, text = 'Open Serial', command = open_serial)
close_serial_button = Button(root, text = 'Close Serial', command = close_serial, state = DISABLED)
com_combobox = ttk.Combobox(root, text = '', postcommand = choosing_com, )
baudrate_text = Entry(root)
baudrate_text.insert(INSERT, '115200')
baudrate_button = Button(root, text = 'Set Baudrate', command = set_baud)

# Linkando os eventos de click no canvas com as rotinas descritas anteriormente
canvas.bind('<Button-1>', left_click)
canvas.bind('<ButtonRelease-1>', left_release)
canvas.bind('<B1-Motion>', left_motion)
canvas.bind('<Button-3>', right_click)
canvas.bind('<ButtonRelease-3>', right_release)
canvas.bind('<B3-Motion>', right_motion)
com_combobox.bind("<<ComboboxSelected>>", selected_com)


# Posicionando tudo na Tela
canvas.grid(row = 1, column = 1)
canvas.update()

sliders['rotate'].grid(row = 2, column = 1)
labels['rotate'].grid(row = 3, column = 1)
sliders['arm1'].grid(row = 4, column = 1)
labels['arm1'].grid(row = 5, column = 1)
sliders['arm2'].grid(row = 6, column = 1)
labels['arm2'].grid(row = 7, column = 1)
open_serial_button.grid(row = 2, column = 2)
close_serial_button.grid(row = 3, column = 2)
com_combobox.grid(row = 4, column = 2)
baudrate_text.grid(row = 5, column = 2)
baudrate_button.grid(row = 6, column = 2)

# Loop
root.mainloop()
