# Interface Homem Máquina para braço robótico de reabilitação 
O objetivo do projeto é desenvolver uma IHM para o braço robo MOREA - reabilitação de braço. Para isso, decidimos usar a biblioteca tkinter do python, que traz ferramentas básicas para a criação de uma interface gráfica, além de ser bem documentada. 
Para a comunicação da interface com a VIOLA + VF toradex decidimos por usar a comunicação serial UART, com isso basta um FTDI para termos uma comunicação bidirecional com a toradex. Para desenvolver a parte de comunicação serial usamos a biblioteca Pyserial.

## Interface
![image](https://user-images.githubusercontent.com/48367584/127949050-b031c211-7965-47d7-a27e-602598497b58.png)
### Canvas
Decidimos criar um braço virtual com 3 graus de liberdade para representar o robô MOREA. 
No canvas branco temos podemos ver duas das juntas do robô representada pelos círculos pretos, o último grau de liberdade é de rotação sobre a base azul.
O lugar que você clicar e arrastar com o botão esquerdo do mouse vira o TARGET do robô, portanto ele tentará colocar sua ponta na posição do mouse.
Caso você clique e arraste com o botão direito do mouse é possível rotacionar o braço sobre a base azul.

### Sliders
Abaixo do canvas estão os sliders permitem controlar de maneira independente cada grau de liberdade.

### Porta Serial
Na parte inferior da direita, temos uma interface simples para a seleção da porta serial.
Elas nos apresenta todas as portas COM disponíveis, além de permitir selecionar o baudrate.

### Botão de emergência
Envia pela serial uma mensagem para parada do braço em caso de emergências.



## Comunicação Serial
Sempre que o robo virtual atualiza sua posição ele envia pela porta serial seus novos ângulos para que o robô real possa seguí-lo.
Os Ângulos são enviados no formato:
  RAD_rotação;RAD_junta1;RAD_junta2;
Sendo a junta1 a mais próxima mda base azul.



## Código
O código é divido em 2 arquivos: main.py e robot.py.
Na main.py temos a criação dos objetos da interface gráfica, a definição das rotinas de funcionamento de botões da interface e a criação do objeto da clase robot.
Na robot.py temos 3 classes, a Vector2d, que serve apenas para ajudar em algumas contas com vetores 2D. A Arm, que cuida das propriedades de cada segmento do robô, sendo que ela pode ser o segmento principal ou ter "pais" associados. O pais são os segmentos no qual esse segmento está ligado.
Por fim, temos a classe Robot, que possui um array de Arms e possui as funções de plot do robô no canvas. A principal função da da classe Robot é a inverseKinematics(), que permite calcular os ângulos das juntas do robô com base no TARGET.
Para desenvolver essa função nos baseamos nesse vídeo https://www.youtube.com/watch?v=inSzWXAbM8Q&ab_channel=ReginaldoJSantos, onde o professor Reginaldo deriva as fórmulas que descrevem os ângulos.
