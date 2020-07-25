#include <iostream>
#include <netdb.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <cstdlib>
#include <stdio.h>
#include <errno.h>
#include <string.h> 
#include <cstring>
#include <cstdlib>
#include <string>
#include <pthread.h>
#include <stdlib.h>
#include <typeinfo>
#include <errno.h>
#include <inttypes.h>


#include "mensaje.pb.h"
using namespace chat;
using namespace std;

using std::cout;
using std::endl;
using std::string;
using std::cin;
using std::strcpy;
using namespace std;
#define MAX_ 16384
//#define PORT 7070
#define HOSTNAME "192.168.1.6"
#define SA struct sockaddr
#define bzero(b,len) (memset((b), '\0', (len)), (void) 0)
#define USER "oliversinn"


int connected;
int code;
int32_t opcion;
int clientON = 1;
int fd;

// Funcion para errores
static void err(const char* s) {
    perror(s);
    exit(EXIT_FAILURE);
}

void parserFromServer(string buffer)
{	
	ServerMessage s;
	s.ParseFromString(buffer);
	cout << "\n" << endl;
	switch(s.option()){
		case 1: // broadcast
			cout << " ------------------- Mensaje entrante ----------------- \t" << endl;
			cout << "Mensaje de grupo enviado por: \t" << endl;
			cout << "ID: \t"  << s.broadcast().userid() << endl;
			if (s.broadcast().has_username()){
				cout << "Username:\t" << s.broadcast().username() << endl;
			}
			cout << "Mensaje: \t" << s.broadcast().message() << endl;
			cout << "\n" << endl;
			// return 1;
			break;
		case 2: // directmessage
			cout << " ------------------- Mensaje entrante ----------------- \t" << endl;
			cout << "Mensaje Privado enviado por: \t"  << endl;
			cout << "ID: \t" << s.message().userid() << endl;
			if (s.message().has_username()){
				cout << "Username:\t" << s.message().username() << endl;				
			}
			cout << "Mensaje: \t" << s.message().message() << endl;
			cout << "\n" << endl;
			// return 1;
			break;
		case 3: // error
			cout << "Recibiendo Error" << endl;
			cout << "ERROR: \t" << s.error().errormessage() <<"\n"<< endl;
			if(s.error().errormessage().compare("error1")==0)
			{
				cout << "SERVIDOR LLENO\n"<<endl;
				cout << "cerrando cliente\n"<<endl;
				clientON = 0;
				exit(0);
			}else if (s.error().errormessage().compare("error2")==0)
			{
				cout << "USUARIO YA EXISTE\n"<<endl;
				cout << "cerrando cliente\n"<<endl;
				clientON = 0;
				exit(0);
			}else if (s.error().errormessage().compare("error3")==0)
			{
				cout << "NO SE ESPECIFICA USUARIO AL CUAL SE DESEA CONOCER INFORMACION\n"<<endl;
			}else if (s.error().errormessage().compare("error4")==0)
			{
				cout << "ID NO PERTENECE A NINGUN USUARIO\n"<<endl;
			}
			// return 50
			break;
		case 4: // myInfoResponse
			cout << "MY INFO RESPONSE RECIVIDO" << endl;
			cout << "ID: \t" << s.myinforesponse().userid() << endl;
			cout << "\n" << endl;
			// return 0;
			break;
		case 5: // connectedUserResponse
			cout << "Recibiendo connectedUserResponse" << endl;
			cout << "Cantidad de usuarios:\t" << s.connecteduserresponse().connectedusers_size() << endl;
			for (int j = 0; j < s.connecteduserresponse().connectedusers_size(); j++){
				ConnectedUser usuario = s.connecteduserresponse().connectedusers(j);
				if (usuario.has_userid()){
					cout << "UserID: " << usuario.userid() << endl;
				}
				cout << "Username: " << usuario.username() << endl;
				if (usuario.has_status()){
					cout << "Status: " << usuario.status() << endl;
				}
				if (usuario.has_ip()){
					cout << "IP: " << usuario.ip() << endl;
				}
			}
			cout << "\n" << endl;
			// return 0;
			break;
		case 6: // changeSatatusResponse
			cout << "Recibiendo ChangeStatusResponse: \t" << endl;
			cout << "ID: \t" << s.changestatusresponse().userid() << endl;
			cout << "Status: \t "<< s.changestatusresponse().status() << "\n" <<endl;
			// return 0;
			break;
		case 7: // broadcastRespnse (sent message status)
			cout << "Recibiendo BroadcastResponse \t" << endl;
			cout << "Mesage Status: \t" << s.broadcastresponse().messagestatus();
			cout << "\n" << endl;

			// return 0;
			break;
		case 8: // directMessageResponse (sent message status)
			cout << "Recibiendo DirectMessageResponse \t" << endl;
			cout << "Mesage Status: \t" << s.directmessageresponse().messagestatus() << endl;
			cout << "\n" << endl;
			// return 0;
			break;
	}
	
}

void *listenServer(void *filedescriptor) {
	//long fd = (long) filedescriptor;
	int numbytes;
	string data;
	char buf[MAX_];
	while(clientON){
		numbytes = recv(fd, buf, MAX_, MSG_WAITALL);
		if (buf != "\0") {
			if (numbytes > 0) {
				buf[numbytes] = '\0';
				data = buf;
				parserFromServer(data);
			} else {
				cout << "SE DESCONECTO DEL SERVER!" << endl;
				cout << "SALIENDO" << endl;
				clientON = 0;
				exit(0);
			}
		} 
		
	}
}

void getuser(int filedescriptor, int userid){
	int fd = filedescriptor;
	char buf[MAX_];
	ClientMessage m;
	connectedUserRequest * myUsersRequest(new connectedUserRequest);
	myUsersRequest->set_userid(userid);
	m.Clear();
	m.set_option(2);
	m.set_allocated_connectedusers(myUsersRequest);
	string msg;
	m.SerializeToString(&msg);
	sprintf(buf,"%s",msg.c_str());
	send(fd, buf, sizeof(buf), 0);
	cout << "Se envio el connectedUserRequest" << endl;
	cout << "Esperando respuesta del servidor \n" << endl;
	usleep(100000);
}

void changestatus(int filedescriptor, string status){
	int fd = filedescriptor;
	char buf[MAX_];
	ClientMessage m;
	ChangeStatusRequest * myChangeStatus(new ChangeStatusRequest);
	myChangeStatus->set_status(status);
	m.set_option(3);
	m.set_allocated_changestatus(myChangeStatus);
	string msg;
	m.SerializeToString(&msg);
	sprintf(buf,"%s",msg.c_str());
	send(fd, buf, sizeof(buf), 0);
	cout << "Se envio el ChangeStatusRequest" << endl;
	cout << "Esperando respuesta del servidor \n" << endl;
	usleep(100000);
}

void sendbroadcast(int filedescriptor, string message){
	int fd = filedescriptor;
	char buf[MAX_];
	ClientMessage m;
	BroadcastRequest * myBroadcast(new BroadcastRequest);
	myBroadcast->set_message(message);
	m.Clear();
	m.set_option(4);
	m.set_allocated_broadcast(myBroadcast);
	string msg;
	m.SerializeToString(&msg);
	sprintf(buf,"%s",msg.c_str());
	send(fd, buf, sizeof(buf), 0);
	cout << "Se envio el BroadcastRequest" << endl;
	cout << "Esperando respuesta del servidor \n" << endl;
	usleep(100000);
}

void sendmessage(int filedescriptor, int id, string message){
	int fd = filedescriptor;
	char buf[MAX_];
	ClientMessage m;
	DirectMessageRequest * myMessage(new DirectMessageRequest);
	myMessage->set_message(message);
	myMessage->set_userid(id);
	m.Clear();
	m.set_option(5);
	m.set_allocated_directmessage(myMessage);
	string msg;
	m.SerializeToString(&msg);
	sprintf(buf,"%s",msg.c_str());
	send(fd, buf, sizeof(buf), 0);
	cout << "Se envio el DirectMessageRequest" << endl;
	cout << "Esperando respuesta del servidor \n" << endl;
	usleep(100000);
}

void *menu(void *args){
	// long fd = (long) filedescriptor;
	char charInput;
	string stringInput;
	int intInput;
	int opcion;
	int esResponse;
	while(clientON){
		cout << "\nQue quieres hacer?" << endl;
		cout << "(1) Obtener usuarios conectados" << endl;
		cout << "(2) Cambiar estado de conexion" << endl;
		cout << "(3) Transmitir un mensaje a todos los usuarios" << endl;
		cout << "(4) Enviar un mensaje directo" << endl;
		cout << "(5) Salir\t" << endl;
		cout << "Escriba opción" << endl;
		fflush( stdin );
		while(true)
		{
			cin >> opcion;
			if(!cin)
			{
				cout << "Debes ingresar un numero"<<endl;
				cin.clear();
				cin.ignore(numeric_limits<streamsize>::max(),'\n');
				continue;
			}else break;
		}
		
		if (opcion == 1 ){ // connectedUserRequest
			cout << "Ingrese el id del usuario que quiere informacion o ingrese 0 para obtener todos los usuarios." << endl;
			fflush( stdin );
			while(true)
			{
				cin >> intInput;
				if(!cin)
				{
					cout << "Debes ingresar un numero"<<endl;
					cin.clear();
					cin.ignore(numeric_limits<streamsize>::max(),'\n');
					continue;
				}else break;
			}
			getuser(fd,intInput);
			continue;
		} else if (opcion == 2 ){ // changeStatus
			cout << "Ingrese su nuevo estado." << endl;
			fflush( stdin );
			cin >> stringInput;
			changestatus(fd, stringInput);
			continue;
		} else if (opcion == 3 ){ //broadcast
			cout << "Ingrese el mensaje que desea enviar" << endl;
			fflush( stdin );
            cin.ignore();
            getline(cin,stringInput);
			sendbroadcast(fd,stringInput);
			continue;
		} else if (opcion == 4 ){ //directmessage
			cout << "Ingrese el id del usuario al que le quiere enviar un mensaje" << endl;
			fflush( stdin );
			while(true)
			{
				cin >> intInput;
				if(!cin)
				{
					cout << "Debes ingresar un numero"<<endl;
					cin.clear();
					cin.ignore(numeric_limits<streamsize>::max(),'\n');
					continue;
				}else break;
			}
			cout << "Ingrese el mensaje que desea enviar" << endl;
			fflush( stdin );
			cin.ignore();
            getline(cin,stringInput);
			sendmessage(fd,intInput,stringInput);
			continue;
		} else if (opcion == 5 ){
			cout << "HASTA LA VISTA BBY" << endl;
			clientON = 0;
			exit(0);
			continue;
		} else if (opcion < 0 || opcion >5){
			cout << "Opcion incorrecta, prueba de nuevo." << endl;
			continue;
		}
	}
}

int main(int argc, char *argv[])
{
	int numbytes,finalizacion;
	char buf[MAX_];
	struct hostent *he;
	struct sockaddr_in server;
	
	if ((he = gethostbyname(argv[2])) == NULL) {
		err("gethostbyname");
	}

	if ((fd = socket(AF_INET, SOCK_STREAM,0)) == -1) {
		err("socket creation failed");
	}

	bzero(&server,sizeof(server));
	server.sin_family = AF_INET;
	char *end;
	intmax_t puerto_ = strtoimax(argv[3],&end,10);
	uint16_t puerto;
	puerto = (uint16_t) puerto_;
	server.sin_port = htons(puerto);
	server.sin_addr = *((struct in_addr *)he->h_addr);

	if (connect(fd, (struct sockaddr *)&server, sizeof(struct sockaddr)) == -1) {
        err("connection with the server failed...");
    }
    
	// Inicia el three way handshake
	cout << "\nINICIA THREE WAY HANDSHAKE" << endl;
	// MY INFO REQ
	// Se crea instacia tipo MyInfoSynchronize y se setean los valores deseables
    MyInfoSynchronize * mySinc(new MyInfoSynchronize);
    mySinc->set_username(argv[1]);
    mySinc->set_ip("127.0.0.1");
	// Para enviar un mensaje
    // Se crea instancia de Mensaje, se setea los valores deseados
    ClientMessage m;
    m.set_option(1);
    m.set_allocated_synchronize(mySinc);
    string msg;
	if(m.has_option()){
		m.SerializeToString(&msg);
		sprintf(buf,"%s",msg.c_str());
		// Se envia el mensaje
		send(fd , buf , sizeof(buf) , 0 );
		cout << "Se envio el MY INFO REQ." << endl;
	}
    
	string data;
	numbytes = -1;
	// Para recibir un mensaje
	cout << "Esperando MY INFO RESPONSE DEL SERVIDOR" << endl;
	while(numbytes==-1){
		numbytes = recv(fd, buf, MAX_, MSG_WAITALL);
		buf[numbytes] = '\0';
		data = buf;
	}
	
	// Se parcea la respuesta esperando que sea el MyInfoResponse
	parserFromServer(data);
	// Se manda el MY INFO ACK.
	MyInfoAcknowledge * myAck(new MyInfoAcknowledge);
	m.set_option(6);
	m.set_allocated_acknowledge(myAck);
	msg = "";
	m.SerializeToString(&msg);
	sprintf(buf,"%s",msg.c_str());
	// Se envia el mensaje
	send(fd , buf , sizeof(buf) , 0 );
	cout << "Se envio el MY INFO ACK." << endl;
	cout << "TERMINA THREE WAY HANDSHAKE.\n" << endl;
	// Finaliza el 3w handshake}


	pthread_t menu_thread;
	pthread_t parser_thread;

	pthread_create(&menu_thread,NULL,menu,NULL);
	pthread_create(&parser_thread,NULL,listenServer,(void *)(&fd));

	pthread_join(menu_thread,NULL);
	pthread_join(parser_thread,NULL);


	// finalizacion del cliente
	google::protobuf::ShutdownProtobufLibrary();
    return 1;
	

}