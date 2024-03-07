#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>

#define PORT 54321
#define MAX_CONN 5
#define MAX_PACKET_LENGTH 128

pthread_mutex_t lock;

int main(int argc, char * argv[]) {
    printf("Team 20 Secure Chat App Server V1\n\n");

    // Set up the listening server
    // Init
    int server_fd, new_client;
    ssize_t valread;
    struct sockaddr_in address;
    int opt = 1;
    socklen_t addrlen = sizeof(address);
    char buffer[MAX_PACKET_LENGTH] = { 0 };
    char * hello = "Hello from server!";

    // Create socket fd
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }

    // Tell the server to reuse ports even if in use by other processes
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        perror("Error setting sockopt");
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY; // Is accepting ANY request smart or secure? No. Do I care? Also no.
    address.sin_port = htons(PORT);

    // Bind to the port
    if (bind(server_fd, (struct sockaddr*) &address, sizeof(address)) < 0) {
        perror("Error binding server");
        exit(EXIT_FAILURE);
    }

    for (;;) {
        // Wait for a connection
        if (listen(server_fd, MAX_CONN) < 0) {
            perror("Error listening");
            exit(EXIT_FAILURE);
        }

        if ((new_client = accept(server_fd, (struct sockaddr*) &address, &addrlen)) < 0) {
            perror("Error accepting new client connection");
            exit(EXIT_FAILURE);
        }

        // Receive number of packets to accept
        unsigned char num_packets_bytes[MAX_PACKET_LENGTH];  // Assuming the length is represented using MAX_PACKET_LENGTH bytes
        if (recv(new_client, num_packets_bytes, MAX_PACKET_LENGTH, 0) < 0) {
            perror("Error receiving number of packets");
            exit(EXIT_FAILURE);
        }

        // Convert the bytes to an integer
        int num_packets = 0;
        for (int i = 0; i < MAX_PACKET_LENGTH; i++) {
            num_packets |= (num_packets_bytes[i] & 0xFF) << (i * 8);
        }
        printf("%d\n", num_packets);

        for (int message_id = 0; message_id < num_packets; message_id++) {
            if (recv(new_client, buffer, MAX_PACKET_LENGTH, 0) < 0) {
                perror("Error receiving message contents");
                exit(EXIT_FAILURE);
            }
            printf("%s", buffer);
        }
        printf("\n");

        close(new_client);
    }
    // Cleanup
    close(server_fd);
    return 0;
}