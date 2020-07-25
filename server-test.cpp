/*
Universidad del Valle de Guateala 
Sistemas operativos
Pablo Viana 
Oliver Mazariegos
 */


#include <stdio.h>
#include <stdlib.h>
#include <strings.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#include <signal.h>
#include <string>
#include <iostream>
#include <string.h> 
#include <sstream>
#include <cstring>
#include <cstdlib>
#include <inttypes.h>


#include "mensaje.pb.h"

//#define PORT 7070           // the port users will be connecting to
#define MAXDATASIZE 16384    // max number of bytes we can send at once
#define BACKLOG 10          // how many pending connections queue will hold
#define MAX_CLIENTS 20

using std::cout;
using std::endl;
using std::string;
using namespace chat;


void sigchld_handler(int s) {
    while (waitpid(-1, NULL, WNOHANG) > 0);
}

int clientnum = 0;
bool serverON = 1;

//definimios una estructura para almacenar los clientes en el servidor
struct ClientInformation
{ 
    int id;
    int fd;
    string status; //0 activo, 1 ocupado, 2 desconectado
    string ip;
    string username;
    int time_connection;
    ClientInformation():id(-1),fd(-1),status("disponible"),ip("localhost"),time_connection(1000){}
}current_clients[MAX_CLIENTS];

//Sctruct para multiples argumentos a pthread_create
struct pthread_args
{
    long connectfd;
    string ip_address;
};

//struct para change status
struct change_status
{
    string status;
    int id;
};

/*
CODIGO PARA ERRORES

error1 - servidor lleno 
error2 - usuario ya existe
error3 - no se especifica el usuario al que se le quiere conocer la informacion
error4 - id no pertenece a ningun usuario

*/

void getUsers(int fd, int userid, string username){
    ServerMessage * sm(new ServerMessage);
    char buffer[MAXDATASIZE];
    ConnectedUserResponse * cur(new ConnectedUserResponse);
    int i, bandera = 0;
    if(userid == 0)
    {    
        for(i=0;i<MAX_CLIENTS;i++){
            //cout << "fd: " << current_clients[i].fd <<"\n";
            if (current_clients[i].fd != -1  && current_clients[i].fd != fd){
                ConnectedUser * conuser;
                conuser = cur->add_connectedusers();
                ClientInformation tempClient = current_clients[i];

                conuser->set_username(tempClient.username);
                conuser->set_userid(tempClient.id);
                conuser->set_status(tempClient.status);
            }
        }
        bandera = 1;
    }else{
        for(i=0;i<MAX_CLIENTS;i++)
        {
            ClientInformation tempClient = current_clients[i];
            if (tempClient.fd != -1)
            {
                if(tempClient.id == userid || tempClient.username.compare(username)==0)
                {
                    ConnectedUser * conuser;
                    conuser = cur->add_connectedusers();
                    conuser->set_username(tempClient.username);
                    conuser->set_userid(tempClient.id);
                    conuser->set_status(tempClient.status);
                    bandera = 1;
                    break;
                }
            }
        }
    }
    
    if(bandera == 1)
    {
        sm->set_option(5);
        sm->set_allocated_connecteduserresponse(cur);
        if(sm->has_option()){
            string msg;
            sm->SerializeToString(&msg);
            sprintf(buffer,"%s",msg.c_str());
            send(fd, buffer, sizeof(buffer), 0);
            cout << "\nSe envio GET USERS\n" << endl;}
    }else{
        ErrorResponse * MyError(new ErrorResponse);
        MyError -> set_errormessage("error4");
        sm->set_option(3);
        sm->set_allocated_error(MyError);
        string msg;
        sm->SerializeToString(&msg);
        sprintf(buffer,"%s",msg.c_str());
        send(fd , buffer , sizeof(buffer) , 0 );
        bandera = -1;
        cout << "\nSe envio ERROR RESPONSE\n" << endl;
    }
}

void messageToSomeone(int fd, string mensaje,int userid){
    int id_remitente;
    string username_remitente;
    for(int j=0;j<MAX_CLIENTS;j++)
    {
        if(current_clients[j].fd == fd)
        {
            id_remitente = current_clients[j].id;
            username_remitente = current_clients[j].username;
        }
    }
    int bandera = 0;
    cout << "mensaje: " << mensaje <<endl;
    char buffer[MAXDATASIZE];
    DirectMessageResponse * DirMes(new DirectMessageResponse);
    DirMes -> set_messagestatus("Mensaje recibido");

    ServerMessage sm;
    sm.set_option(8);
    sm.set_allocated_directmessageresponse(DirMes);
    string msg;
    sm.SerializeToString(&msg);
    sprintf(buffer,"%s",msg.c_str());
    send(fd, buffer, sizeof(buffer), 0);
    cout << "\nSe envio Direct message response\n" << endl;

    for(int i=0;i<MAX_CLIENTS;i++){
        if(current_clients[i].id == userid){ // no esta asignado
            DirectMessage * DM(new DirectMessage);
            DM -> set_message(mensaje);
            DM -> set_userid(id_remitente);
            DM -> set_username(username_remitente);
            sm.Clear();
            sm.set_option(2);
            sm.set_allocated_message(DM);
            string msg;
            sm.SerializeToString(&msg);
            sprintf(buffer,"%s",msg.c_str());
            send(current_clients[i].fd, buffer, sizeof(buffer), 0);
            cout << "\nSe envio Direct message\n" << endl;
            bandera = 1;
        }
    }
    if(bandera == 0)
    {
        ErrorResponse * MyError(new ErrorResponse);
        MyError -> set_errormessage("error4");
        sm.set_option(3);
        sm.set_allocated_error(MyError);
        string msg;
        sm.SerializeToString(&msg);
        sprintf(buffer,"%s",msg.c_str());
        send(fd , buffer , sizeof(buffer) , 0 );
        cout << "\nSe envio ERROR RESPONSE\n" << endl;

    return;
    }
}

void messageToAll(int fd, string mensaje){
    int id_remitente;
    string username_remitente;
    for (int j = 0;j<MAX_CLIENTS;j++)
    {
        if(current_clients[j].fd == fd){
            id_remitente = current_clients[j].id;
            username_remitente = current_clients[j].username;
        }
    }
    cout <<"\n\n------------ Recibiendo Broadcast Request ------------\n\n"<<endl;
    cout << "mensaje: " << mensaje <<endl;
    ServerMessage sm;
    char buffer[MAXDATASIZE];
    BroadcastResponse * brodmsgr(new BroadcastResponse);
    brodmsgr -> set_messagestatus("Mensaje recibido");
    sm.set_option(7);
    sm.set_allocated_broadcastresponse(brodmsgr);
    if(sm.has_option()){
        string msg;
        sm.SerializeToString(&msg);
        sprintf(buffer,"%s",msg.c_str());
        send(fd, buffer, sizeof(buffer), 0);
        cout << "\nSe envio Broadcast response\n" << endl;}

    cout <<"\n\n------------ Enviando mensaje a todos los usuarios ------------\n\n"<<endl;
    for(int i=0;i<MAX_CLIENTS;i++){
        if(current_clients[i].fd == fd){ // si es la persona que lo envio
            //serverResponse(current_clients[i].fd,"mensaje enviado",205);
        }else if(current_clients[i].fd != -1){ // si no esta asignado
            BroadcastMessage * brodmsg(new BroadcastMessage);
            brodmsg -> set_message(mensaje);
            brodmsg -> set_userid(id_remitente);
            brodmsg -> set_username(username_remitente);
            sm.set_option(1);
            sm.set_allocated_broadcast(brodmsg);
            if(sm.has_option()){
                string msg;
                sm.SerializeToString(&msg);
                sprintf(buffer,"%s",msg.c_str());
                send(current_clients[i].fd, buffer, sizeof(buffer), 0);
                cout << "Se envio Broadcast Message" << endl;}    

        }
    }
}
change_status changeStatus(int fd, string status){
    change_status cs;
    cout <<"\n\n------------ Recibiendo Change Status Request ------------\n\n"<<endl;
    cout << "status: " << status <<endl;
    int i;
    for(i=0;i<MAX_CLIENTS;i++){
        if(fd == current_clients[i].fd)
        {
            current_clients[i].status=status;
            cout<< "current_clients[i].status: " << current_clients[i].status << "\n\n"<<endl;
            cs.status = current_clients[i].status;
            cs.id = current_clients[i].id;
            return cs; 
        }
    }
}


int checkUser(int fd, string username, string ip)
{
    char buffer[MAXDATASIZE];
    int i;
    int bandera = 0;
    if (clientnum > MAX_CLIENTS){ // si aun hay espacio
        ErrorResponse * MyError(new ErrorResponse);
        MyError -> set_errormessage("error1");

        ServerMessage sm;
        sm.set_option(3);
        sm.set_allocated_error(MyError);
        string msg;
        sm.SerializeToString(&msg);
        sprintf(buffer,"%s",msg.c_str());
        send(fd , buffer , sizeof(buffer) , 0 );
        cout << "Se envio ERROR RESPONSE" << endl;
        //er.set_option(1);
        bandera = 1;
        return 500;
    }

    for(i=0;i<MAX_CLIENTS;i++){
        if (current_clients[i].fd != -1 &&
            username.compare(current_clients[i].username) == 0
        ){
            ErrorResponse * MyError(new ErrorResponse);
            MyError -> set_errormessage("error2");

            ServerMessage sm;
            sm.set_option(3);
            sm.set_allocated_error(MyError);
            string msg;
            sm.SerializeToString(&msg);
            sprintf(buffer,"%s",msg.c_str());
            send(fd , buffer , sizeof(buffer) , 0 );
            cout << "Se envio ERROR RESPONSE" << endl;
            bandera = 1;
            return 500;
        }
    }

    for(i=0;i<MAX_CLIENTS;i++){
        if(current_clients[i].fd == -1 && bandera != 1){
            cout <<"-------- Registrando usuario en servidor --------"<<endl;
            current_clients[i].id =i+1;
            current_clients[i].fd=fd;
            current_clients[i].username=username;
            current_clients[i].status = "disponible";
            current_clients[i].ip = ip;
            current_clients[i].time_connection = 0;
            
            cout <<"------------ Registro completado ------------\n\n"<<endl;
              
            cout <<"------------ Chequeo de usuarios en servidor ------------"<<endl;
            cout <<"----------------- cliente numero: 0 -----------------"<<endl;
            cout<<"username:"<<current_clients[0].username<<endl;
            cout<<"file descriptor:"<<current_clients[0].fd<<endl;
            cout<<"id:"<<current_clients[0].id<<endl;
            cout<<"status:"<<current_clients[0].status<<endl;
            cout<<"ip:"<<current_clients[0].ip<<endl;
            cout<<"time connection:"<<current_clients[0].time_connection<<endl;

            cout <<"----------------- cliente numero: 1 -----------------"<<endl;
            cout<<"username:"<<current_clients[1].username<<endl;
            cout<<"file descriptor:"<<current_clients[1].fd<<endl;
            cout<<"id:"<<current_clients[1].id<<endl;
            cout<<"status:"<<current_clients[1].status<<endl;
            cout<<"ip:"<<current_clients[1].ip<<endl;
            cout<<"time connection:"<<current_clients[1].time_connection<<endl;

            cout <<"----------------- cliente numero: 2 -----------------"<<endl;
            cout<<"username:"<<current_clients[2].username<<endl;
            cout<<"file descriptor:"<<current_clients[2].fd<<endl;
            cout<<"id:"<<current_clients[2].id<<endl;
            cout<<"status:"<<current_clients[2].status<<endl;
            cout<<"ip:"<<current_clients[2].ip<<endl;
            cout<<"time connection:"<<current_clients[2].time_connection<<"\n\n"<<endl;

            return i+1; 
        } 
    }

    return 1;
}

//Recibe clientMessage y dependiendo de la opcion discienre que accion del server ejecutar
int managementServer(int fd, string client_ip)
{
    int numbytes,action,code,resp;
    char buf[MAXDATASIZE];
    char buffer[MAXDATASIZE];
    ServerMessage sm;
    ClientMessage c;
    string msg;
    numbytes = recv(fd, buf, MAXDATASIZE, MSG_WAITALL);
    if(numbytes!=0  && numbytes!=-1)
    {    
        buf[numbytes] = '\0';
        string a = buf;
        c.ParseFromString(a);
        code = c.option();
        
        //cout<<"code: "<<code<<"\n";
    }
    switch(code)
    {
        case 1:
        { //conecction handshake "synchronize"
            cout << "\n\nSe detecta opcion numero 1 synchronize\n\n";
            action = 1;
        }
        break;
        case 2:
        {
            cout << "\n\nSe detecta opcion numero 2 connectedUsers\n\n";
            action = 2;
        }
        break;
        case 3:
        {
            cout << "\n\nSe detecta opcion numero 3 changeStatus\n\n";
            action = 3;
        }
        break;
        case 4:
        {
            cout << "\n\nSe detecta opcion numero 4 Broadcast\n\n";
            action = 4;
        }
        break;
        case 5:
        {
           cout << "\n\nSe detecta opcion numero 5 Direct Message\n\n";
           action = 5;
        }
        case 6:
        {
            cout << "\n\nSe recibe  MY INFO ACK.\n";
            cout << "Usuario conectado listo para chatear\n\n";
            code = 0;

        }
        break;
    }

    if(numbytes!=0  && numbytes!=-1){
        //cout<<"action: "<<action<<"\n";
    }
    switch(action)
    {
        case 1:
        {
            resp = checkUser(fd,c.synchronize().username(), client_ip);
            if(resp != 500)
            {
                MyInfoResponse * MyInfo(new MyInfoResponse);
                MyInfo -> set_userid(resp);

                sm.set_option(4);
                sm.set_allocated_myinforesponse(MyInfo);
                sm.SerializeToString(&msg);
                sprintf(buffer,"%s",msg.c_str());
                send(fd , buffer , sizeof(buffer) , 0 );
                cout << "Se envio el MY INFO RESPONSE" << endl;
            }
            code = 0;
            action = 0;
            return 0;
        }
        break;
        case 2:
        {
            //aqui podria haber clavo porque no se si es connectedusers()
            if(c.connectedusers().has_userid() == 1 && c.connectedusers().has_username() == 0)
            {
                getUsers(fd, c.connectedusers().userid(), "");

            }else if (c.connectedusers().has_userid() == 0 && c.connectedusers().has_username() == 1)
            {
                getUsers(fd, 0, c.connectedusers().username());

            }else if (c.connectedusers().has_userid() == 1 && c.connectedusers().has_username() == 1)
            {
                getUsers(fd, c.connectedusers().userid(), c.connectedusers().username());

            }else{
                ErrorResponse * MyError(new ErrorResponse);
                MyError -> set_errormessage("error3");
                sm.set_option(3);
                sm.set_allocated_error(MyError);
                string msg;
                sm.SerializeToString(&msg);
                sprintf(buffer,"%s",msg.c_str());
                send(fd , buffer , sizeof(buffer) , 0 );
                cout << "Se envio ERROR RESPONSE" << endl;
            }

            code = 0;
            action = 0;
            return 0;
        }
        break;
        case 3: 
        {
            change_status changsta;
            changsta = changeStatus(fd, c.changestatus().status());

            ChangeStatusResponse * MyResp(new ChangeStatusResponse);
            MyResp -> set_userid(changsta.id);
            MyResp -> set_status(changsta.status);
            
            sm.set_option(6);
            sm.set_allocated_changestatusresponse(MyResp);
            sm.SerializeToString(&msg);
            sprintf(buffer,"%s",msg.c_str());
            send(fd, buffer, sizeof(buffer), 0);
            cout << "Se envio CHANGE STATUS" << endl;

            code = 0;
            action = 0;
            return 0;
        }
        break;
        case 4:
        {
            messageToAll(fd, c.broadcast().message());
            code = 0;
            action = 0;
            return 0;
        }
        break;
        case 5:
        {
            // cout << "directmessage: " << c.directmessage().has_username() << endl;
            messageToSomeone(fd, c.directmessage().message(), c.directmessage().userid());
            code = 0;
            action = 0;
            return 0;
        }
        break;
        default:
            break;
        // string data;
        // demo::People to;
        // to.set_name("Lysting Huang");
        // to.set_id(123);
        // to.set_email("lytsing@hotmail.com");
        // to.SerializeToString(&data);
        // char bts[data.length()];
        // sprintf(bts, "%s", data.c_str());
        // send(connectfd, bts, sizeof(bts), 0);

    }
}



//funcion que ejecutara cada thread, recibe el file descriptor que regresa accept()
void *conHandler(void *arguments)
{
    struct pthread_args *arg = (struct pthread_args *)arguments;
    //Parseamos el parametro de void a long para usar el file descriptor
    long connectfd = arg -> connectfd;
    //parseamos el parametro de voir a un struct para obtener el ip del cliente
    string client = arg -> ip_address;
    //aumentamos el numero de conexiones activas en el server
    clientnum++;

    while(1) {
        if(connectfd<0 || managementServer(connectfd, client) == 1)
        {
            clientnum = clientnum - 1;
            //close(connectfd);
            //serverON = 0;
            pthread_exit(0);
        }
    }

}


//Funcion para desplegar errores y salir del programa
static void err(const char* s) {
    perror(s);
    exit(EXIT_FAILURE);
}

int main(int argc, char** argv) {
    int listenfd;
    int connectfd;
    struct sockaddr_in server;
    struct sockaddr_in client;
    socklen_t sin_size;
    struct sigaction sa;
    string client_ip;
    struct pthread_args pargs;

    if ((listenfd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        err("socket");
    }

    int opt = SO_REUSEADDR;
    if (setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) == -1) {
        err("setsockopt");
    }

    bzero(&server, sizeof(server));
    server.sin_family = AF_INET;              // host byte order
    char *end;
    intmax_t puerto_ = strtoimax(argv[1],&end,10);
    uint16_t puerto;
    puerto = (uint16_t) puerto_;
    server.sin_port = htons(puerto);              // short, network byte order
    server.sin_addr.s_addr = htonl(INADDR_ANY); // automatically fill with my IP

    if (bind(listenfd, (struct sockaddr *)&server, sizeof(struct sockaddr)) == -1) {
        err("bind");
    }else{
        cout << "Socket succefully created and binded\n";
    }

    if (listen(listenfd, BACKLOG) == -1) {
        err("listen");
    }else{
        cout << "Server listening ...\n";
    }

    sa.sa_handler = sigchld_handler;  // reap all dead processes
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    if (sigaction(SIGCHLD, &sa, NULL) == -1) {
        err("sigaction");
    }


    while (serverON) {     // main accept() loop
        sin_size = sizeof(struct sockaddr_in);

        connectfd = accept(listenfd, (struct sockaddr *)&client, &sin_size);
        client_ip =  inet_ntoa(client.sin_addr);
        pargs.connectfd = connectfd;
        pargs.ip_address = client_ip;
        cout << "Server detected new connection\n";

        // // Send msg to clients
        // string data;
        // demo::People to;
        // to.set_name("Lysting Huang");
        // to.set_id(123);
        // to.set_email("lytsing@hotmail.com");
        // to.SerializeToString(&data);
        // char bts[data.length()];
        // sprintf(bts, "%s", data.c_str());
        // send(connectfd, bts, sizeof(bts), 0);
        pthread_t conection_thread;
        pthread_create(&conection_thread, NULL, conHandler, (void *)(&pargs));
    }

    //close(listenfd);
    //close(connectfd);

    return 0;
}
