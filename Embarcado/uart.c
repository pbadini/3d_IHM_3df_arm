#include <termios.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int SerialOpen(int speed, int parity, char * error);
 
int main(){
  
  // Srting que carrega o erro que correu caso de errado a inicialização da serial
  char error[20];

  // variavel que carrega as informações da serial que estamos usando
  int serial;

  // Inicializando a serial com 115200 de baudrate e sem bit de paridade
  // igual na interface
  serial = SerialOpen(B115200, 0, error);

  if(serial == -1){
    // houve um erro ao tentar iniciar a serial, podemos tratá-lo aqui
    // para descobrir qual error foi podemos usar a string error
    printf(error);
    return -1;
  }

  // buffer que armazena o que foi lido na serial
  char buf [30];
  
  // loop principal do programa
  // para esse programa fizemos apenas um echo do que foi lido pela placa na serial
  // mas é apartir do angulos enviados pela interface e recebidos pela serial que
  // a placa iria controlar o braço
  while(1){
    // le a serial, como nao tem blocking mesmo que tenhamos apenas um byte na serial
    // esse um byte sera escrito na variavel 'buf'
    int n = read (fd, buf, sizeof(buf));

    if(strcmp(buf, "STOP") == 0){
      // parada de emergencia solicitada pela interface
      return -1;
    }

    // printa pela serial o que foi lido na serial (echo)
    if (n > 0)
      write (fd, buf, n);

  }
  return 0;
}


int SerialOpen(int speed, int parity, char * error){

  struct termios tty;

  int flags = O_RDWR | O_NOCTTY | O_NONBLOCK;
  
  // Abrindo a UART_A da placa Colibri VF50
  int fd = open("/dev/colibri-uarta", flags);
  

  // Copia os paramatros da serial na struct tty
  if (tcgetattr(fd, &tty) != 0)
  {  
    //Caso de errado copia o erro para a string error
    sprintf (error, "Error getting serial parameters");
    return -1;
  }

  //setando a porta serial para chars de tamanho 8 bits 
  tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;

  //Setando o baudrate para 'speed', igual da interface gráfica
  tty.c_cflag |= speed;

  tty.c_cflag &= ~(PARENB | PARODD); // limpa as paridades pre setadas
  tty.c_cflag |= parity;             // seta a nova paridade


  // Vamos setar a serial para nao ter blocking, ou seja, podemos ler
  // quanto bytes quisermos da serial sem a necessidade de esperar que
  // cheguem X bytes juntos, além disso também precisamos setar um timeout
  // para as leituras.

  tty.c_cc[VMIN]  = 0;  // sem blocking           
  tty.c_cc[VTIME] = 5;  // timeout de 0.5 s
  

  // Copia os paramatros da struct tty para a serial
  if (tcsetattr (fd, TCSANOW, &tty) != 0)
  {
    //Caso de errado copia o erro para a string error
    sprintf (error, "Error setting serial parameters");
    return -1;
  }

  return fd;
}