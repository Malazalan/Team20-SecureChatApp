#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <string.h>

#define PORT 54321
#define MAX_CONN 5
#define MAX_PACKET_LENGTH 128
#define HEADER_LENGTH 16

// Header types
#define text 1
#define file 2

pthread_mutex_t lock;

char** splitMessage(char* receivedMessage, int* tokenCount) {
    const char delim[2] = "\x1F";
    char *token;
    char** tokens = NULL;
    int count = 0;

    token = strtok(receivedMessage, delim);

    while(token != NULL) {
        tokens = realloc(tokens, sizeof(char*) * (count + 1));
        if(tokens == NULL) {
            fprintf(stderr, "Memory allocation failed\n");
            exit(EXIT_FAILURE);
        }

        tokens[count] = malloc(strlen(token) + 1);
        if(tokens[count] == NULL) {
            fprintf(stderr, "Memory allocation failed for token\n");
            exit(EXIT_FAILURE);
        }

        strcpy(tokens[count], token);

        count++;
        token = strtok(NULL, delim);
    }

    // Store the token count
    *tokenCount = count;

    return tokens; // Return the dynamic array of tokens
}

int main(int argc, char * argv[]) {
    char* Alice = "127.0.0.1";
    printf("Team 20 Secure Chat App Server V1\n\n");

    // Set up the listening server
    // Init
    int server_fd, new_client;
    struct sockaddr_in address;
    int opt = 1;
    socklen_t addrlen = sizeof(address);
    char buffer[MAX_PACKET_LENGTH] = { 0 };

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
        unsigned char num_packets_bytes[HEADER_LENGTH];  // Assuming the length is represented using MAX_PACKET_LENGTH bytes
        if (recv(new_client, num_packets_bytes, HEADER_LENGTH, 0) < 0) {
            perror("Error receiving number of packets");
            exit(EXIT_FAILURE);
        }

        unsigned char messageType = num_packets_bytes[0];

        // Convert the bytes to an integer - ignoring the first byte
        int num_packets = 0;
        for (int i = 1; i < HEADER_LENGTH; i++) {
            num_packets |= (num_packets_bytes[i] & 0xFF) << ((i-1) * 8);
        }

        char* receivedMessage = malloc(num_packets * MAX_PACKET_LENGTH);
        int nextChar = 0;
        for (int message_id = 0; message_id < num_packets; message_id++) {
            if (recv(new_client, buffer, MAX_PACKET_LENGTH, 0) < 0) {
                perror("Error receiving message contents");
                exit(EXIT_FAILURE);
            }
            for (int charNum = 0; charNum < MAX_PACKET_LENGTH; charNum++) {
                receivedMessage[nextChar] = buffer[charNum];
                nextChar++;
            }
        }

        close(new_client);

        int tokenCount = 0;
        char** tokens = splitMessage(receivedMessage, &tokenCount);

        printf("Encrypted message - %s\n", tokens[0]);
        printf("Ciphertext sign - %s\n", tokens[1]);
        printf("Sender - %s\n", tokens[2]);
        printf("Target - %s\n", tokens[3]);
        printf("Timestamp - %s\n", tokens[4]);

        for(int i = 0; i < tokenCount; i++) {
            free(tokens[i]);
        }
        free(tokens);

        printf("\n\n");
    }
    // Cleanup
    close(server_fd);
    return 0;
}