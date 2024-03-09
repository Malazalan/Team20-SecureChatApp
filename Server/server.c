#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <string.h>
#include <arpa/inet.h>

#define PORT 54321
#define CLIENT_PORT 12345
#define MAX_CONN 5
#define MAX_PACKET_LENGTH 12
#define HEADER_LENGTH 16

// Header types
#define text 1
#define file 2

pthread_mutex_t lock;

struct Header {
    int messageType;
    int numberOfPackets;
};

void convertHeaderToBytes(struct Header header, unsigned char* headerBytes) {
    headerBytes[0] = header.messageType;

    for (int i = 1; i < HEADER_LENGTH; i++) {
        headerBytes[i] = header.numberOfPackets & 0xFF; // Extract the least significant byte
        header.numberOfPackets >>= 8; // Shift right by 8 bits to get the next byte
    }
    for (int i = 0; i < HEADER_LENGTH; i++) {
        printf("%02X ", headerBytes[i]);
    }
}

void handleWrite(char* address, struct Header * header, const unsigned char* messageToSend) {
    int sockfd;
    struct sockaddr_in clientAddr;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        printf("Failed to create write socket");
        pthread_exit(NULL);
    }

    clientAddr.sin_family = AF_INET;
    clientAddr.sin_addr.s_addr = inet_addr(address);
    clientAddr.sin_port = htons(CLIENT_PORT);

    if (connect(sockfd, (struct sockaddr*)&clientAddr, sizeof(clientAddr)) != 0) {
        printf("Failed to connect to client listener");
        pthread_exit(NULL);
    }

    printf("Size %ld\n", strlen(messageToSend));
    unsigned char headerBytes[HEADER_LENGTH];
    convertHeaderToBytes(*header, headerBytes);

    // Send the header
    printf("Sending header\n");
    send(sockfd, headerBytes, HEADER_LENGTH, 0);

    // Send the packets
    printf("Sending message\n");
    printf("Preparing %s\n", messageToSend);
    for (int packetNum = 0; packetNum < header->numberOfPackets; packetNum++) {
        unsigned char* buffer = malloc(MAX_PACKET_LENGTH);

        if (packetNum < header->numberOfPackets - 1) {
            for (int i = 0; i < MAX_PACKET_LENGTH; i++) {
                buffer[i] = messageToSend[(packetNum * MAX_PACKET_LENGTH) + i];
            }
        } else {
            int counter = 0;
            for (int i = 0; i < MAX_PACKET_LENGTH; i++) {
                if ((packetNum * MAX_PACKET_LENGTH) + i < strlen((const char*)messageToSend)) {
                    buffer[i] = messageToSend[(packetNum * MAX_PACKET_LENGTH) + i];
                    counter++;
                } else {
                    for (int j = counter; j < MAX_PACKET_LENGTH; j++) {
                        buffer[j] = '\0';
                    }
                }
            }
        }

        printf("Sent %s\n", buffer);
        send(sockfd, buffer, MAX_PACKET_LENGTH, 0);
        free(buffer);
    }
    printf("Finished\n\n");
}

struct WriteThreadArgs {
    char * addr;
    struct Header * header;
    unsigned char messageToSend;
};

void *writeThreadWrapper(void* args) {
    struct WriteThreadArgs* threadArgs = (struct WriteThreadArgs*) args;

}

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

        printf("Ready to receive\n");
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

        struct Header headerToSend;
        headerToSend.numberOfPackets = num_packets;
        headerToSend.messageType = messageType;

        printf("\n\n");

        int messageLen = 0;
        for(int i = 0; i < tokenCount; i++) {
            messageLen += strlen(tokens[i]);
        }

        printf("%d\n", messageLen);
        char messageToSend[messageLen];
        for (int i = 0; i < tokenCount; i++) {
            strcat(messageToSend, tokens[i]);
        }

        printf("%s\n%s\n---\n", messageToSend, receivedMessage);

        handleWrite(Alice, &headerToSend, (unsigned char*)messageToSend);

        for(int i = 0; i < tokenCount; i++) {
            free(tokens[i]);
        }
        free(tokens);
    }
    // Cleanup
    close(server_fd);
    return 0;
}