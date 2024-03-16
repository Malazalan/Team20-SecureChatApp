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
#define MAX_PACKET_LENGTH 256
#define HEADER_LENGTH 16
#define MAX_CLIENTS 10

// Header types
#define metadata 0
#define text 1
#define file 2

pthread_mutex_t lock;

struct Client {
    char* username;
    int usernameSize;
    char* IP;
    int IPSize;
};

void secureFreeClient (struct Client * client) {
    if (client) {
        if (client->username) {
            memset(client->username, 0, client->usernameSize);
            free(client->username);
        }

        if (client->IP) {
            memset(client->IP, 0, client->IPSize);
            free(client->IP);
        }

        memset(client, 0, sizeof(*client));
        free(client);
    }
}

void secureFreeString (char * string) {
    if (string) {
        memset(string, 0, strlen(string));
        free(string);
    }
}

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
    printf("-> ");
}

void handleWrite(char* address, struct Header * messageHeader, struct Header * metadataHeader,
        struct Header * fileMetadataHeader, const unsigned char* messageToSend, const unsigned char* metadataToSend) {
    int sockfd;
    struct sockaddr_in clientAddr;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        printf("Failed to create write socket");
        pthread_exit(NULL);
    }

    clientAddr.sin_family = AF_INET;
    printf("Contacting %s\n", address);
    clientAddr.sin_addr.s_addr = inet_addr(address);
    clientAddr.sin_port = htons(CLIENT_PORT);

    if (connect(sockfd, (struct sockaddr*)&clientAddr, sizeof(clientAddr)) != 0) {
        printf("Failed to connect to client listener");
        pthread_exit(NULL);
    }

    // Send the message header
    unsigned char headerBytes[HEADER_LENGTH];
    convertHeaderToBytes(*messageHeader, headerBytes);
    printf("Sending message header\n");
    send(sockfd, headerBytes, HEADER_LENGTH, 0);

    // Send the metadata header
    convertHeaderToBytes(*metadataHeader, headerBytes);
    printf("Sending metadata header\n");
    send(sockfd, headerBytes, HEADER_LENGTH, 0);

    if (fileMetadataHeader->numberOfPackets > 0) {
        // Send file metadata header
        convertHeaderToBytes(*fileMetadataHeader, headerBytes);
        printf("Sending file metadata header\n");
        send(sockfd, headerBytes, HEADER_LENGTH, 0);
    }

    // Send the packets
    printf("Sending message\n");
    //printf("Preparing %s\n", messageToSend);
    for (int packetNum = 0; packetNum < messageHeader->numberOfPackets; packetNum++) {
        unsigned char* buffer = malloc(MAX_PACKET_LENGTH);

        if (packetNum < messageHeader->numberOfPackets - 1) {
            for (int i = 0; i < MAX_PACKET_LENGTH; i++) {
                buffer[i] = messageToSend[(packetNum * MAX_PACKET_LENGTH) + i];
            }
        } else {
            /*int counter = 0;
            for (int i = 0; i < MAX_PACKET_LENGTH; i++) {
                if ((packetNum * MAX_PACKET_LENGTH) + i < strlen((const char*)messageToSend)) {
                    buffer[i] = messageToSend[(packetNum * MAX_PACKET_LENGTH) + i];
                    counter++;
                } else {
                    for (int j = counter; j < MAX_PACKET_LENGTH; j++) {
                        buffer[j] = '\0';
                    }
                }
            }*/
            for (int i = 0; i < MAX_PACKET_LENGTH; i++) {
                buffer[i] = messageToSend[(packetNum * MAX_PACKET_LENGTH) + i];
            }
        }

        printf("Sent %s\n", buffer);
        send(sockfd, buffer, MAX_PACKET_LENGTH, 0);
        secureFreeString((char*) buffer);
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
    // TODO make these addable through code - manual for testing
    struct Client *allClients[MAX_CLIENTS];

    // Alan
    struct Client * Alan = malloc(sizeof(struct Client));
    Alan->username = malloc(strlen("Alice"));
    strncpy(Alan->username, "Alice", 5);
    Alan->usernameSize = strlen("Alice") + 1;
    Alan->IP = malloc(strlen("127.0.0.1"));
    strncpy(Alan->IP, "127.0.0.1", strlen("127.0.0.1") + 1);
    Alan->IPSize = strlen("127.0.0.1") + 1;

    // Joe
    struct Client * Joe = malloc(sizeof(struct Client));
    Joe->username = malloc(strlen("Bob"));
    strncpy(Joe->username, "Bob", 4);
    Joe->usernameSize = strlen("Bob") + 1;
    Joe->IP = malloc(strlen("127.0.0.1")); //TODO change to his public IP
    strncpy(Joe->IP, "127.0.0.1", strlen("127.0.0.1") + 10);
    Joe->IPSize = strlen("127.0.0.1") + 1;

    allClients[0] = Alan;
    allClients[1] = Joe;

    printf("Team 20 Secure Chat App Server V1\n\n");

    // Set up the listening server
    // Init
    int server_fd, new_client;
    struct sockaddr_in address;
    int opt = 1;
    socklen_t addrlen = sizeof(address);
    unsigned char buffer[MAX_PACKET_LENGTH] = { 0 };

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

        // Receive message header
        printf("Receive message header\n");
        unsigned char num_message_packets[HEADER_LENGTH];  // Assuming the length is represented using MAX_PACKET_LENGTH bytes
        if (recv(new_client, num_message_packets, HEADER_LENGTH, 0) < 0) {
            perror("Error receiving number of packets");
            exit(EXIT_FAILURE);
        }
        unsigned char messageType = num_message_packets[0];

        // Convert the bytes to an integer - ignoring the first byte
        printf("Convert message header\n");
        int int_message_packets = 0;
        for (int i = 1; i < HEADER_LENGTH; i++) {
            int_message_packets |= (num_message_packets[i] & 0xFF) << ((i-1) * 8);
        }

        // Receive metadata header
        printf("Receive metadata header\n");
        unsigned char num_metadata_packets[HEADER_LENGTH];  // Assuming the length is represented using MAX_PACKET_LENGTH bytes
        if (recv(new_client, num_metadata_packets, HEADER_LENGTH, 0) < 0) {
            perror("Error receiving number of packets");
            exit(EXIT_FAILURE);
        }

        // Convert the bytes to an integer - ignoring the first byte
        printf("Convert metadata header\n");
        int int_metadata_packets = 0;
        for (int i = 1; i < HEADER_LENGTH; i++) {
            int_metadata_packets |= (num_metadata_packets[i] & 0xFF) << ((i-1) * 8);
        }

        unsigned char num_file_metadata_packets[HEADER_LENGTH];
        int int_file_metadata_packets = 0;
        if (messageType == file) {
            printf("Receive file metadata header\n");
            if (recv(new_client, num_file_metadata_packets, HEADER_LENGTH, 0) < 0) {
                perror("Error receiving number of packets");
                exit(EXIT_FAILURE);
            }
            for (int i = 1; i < HEADER_LENGTH; i++) {
                int_file_metadata_packets |= (num_file_metadata_packets[i] & 0xFF) << ((i-1) * 8);
            }
            printf("The file is %d bytes long\n", int_file_metadata_packets);
        }

        printf("Expecting %d message packets\nExpecting %d metadata packets\n", int_message_packets, int_metadata_packets);

        unsigned char* receivedMessage = malloc(int_message_packets * MAX_PACKET_LENGTH);
        int nextChar = 0;
        //printf("Saved message\n");
        for (int message_id = 0; message_id < int_message_packets; message_id++) {
            if (recv(new_client, buffer, MAX_PACKET_LENGTH, 0) < 0) {
                perror("Error receiving message contents");
                exit(EXIT_FAILURE);
            }
            for (int charNum = 0; charNum < MAX_PACKET_LENGTH; charNum++) {
                receivedMessage[nextChar] = buffer[charNum];
                nextChar++;
                //printf("%d", buffer[charNum]);
            }
            //printf("%s", buffer);
        }
        //printf("\nSaved message\n%d\n", receivedMessage);
        char* receivedMetadata = malloc(int_metadata_packets * MAX_PACKET_LENGTH);
        nextChar = 0;
        for (int message_id = 0; message_id < int_metadata_packets; message_id++) {
            if (recv(new_client, buffer, MAX_PACKET_LENGTH, 0) < 0) {
                perror("Error receiving message contents");
                exit(EXIT_FAILURE);
            }
            for (int charNum = 0; charNum < MAX_PACKET_LENGTH; charNum++) {
                receivedMetadata[nextChar] = buffer[charNum];
                nextChar++;
            }
            //printf("%s", buffer);
        }

        close(new_client);

        int tokenCount = 0;
        char** tokens = splitMessage(receivedMetadata, &tokenCount);

        //printf("Encrypted message - %s\n", tokens[0]);
        //printf("Ciphertext sign - %s\n", tokens[1]);
        printf("Sender - %s\n", tokens[0]);
        printf("Target - %s\n", tokens[1]);
        printf("Timestamp - %s\n", tokens[2]);

        struct Header messageHeader;
        messageHeader.numberOfPackets = int_message_packets;
        messageHeader.messageType = messageType;

        struct Header metadataHeader;
        metadataHeader.numberOfPackets = int_metadata_packets;
        metadataHeader.messageType = 0;

        struct Header fileMetadataHeader;
        fileMetadataHeader.numberOfPackets = int_file_metadata_packets;
        metadataHeader.messageType = 0;

        printf("\n\n");

        int metadataLen = 0;
        for(int i = 0; i < tokenCount; i++) {
            metadataLen += strlen(tokens[i]);
        }

        // Add space for separators (ASCII 31). Note: tokenCount-1 because no separator after the last token
        metadataLen += tokenCount - 1;

        char metadataToSend[metadataLen + 1]; // +1 for the null terminator
        metadataToSend[0] = '\0'; // Initialize the first character to null terminator to make it an empty string for strcat

        for (int i = 0; i < tokenCount; i++) {
            strcat(metadataToSend, tokens[i]);
            if (i < tokenCount - 1) { // Don't add a separator after the last token
                int len = strlen(metadataToSend);
                metadataToSend[len] = (char)31; // ASCII 31 - Unit separator
                metadataToSend[len + 1] = '\0'; // Null-terminate the string
            }
        }

        for (int i = 0; i < MAX_CLIENTS; i++) {
            // Find the IP address of the target
            if (allClients[i] != NULL) {
                printf("Checking %s with %s\n", tokens[1], allClients[i]->username);
                if (strcmp(tokens[1], allClients[i]->username) == 0) {
                    printf("Metadata -> %s\n", metadataToSend);

                    handleWrite(allClients[i]->IP, &messageHeader, &metadataHeader, &fileMetadataHeader,
                               receivedMessage, (unsigned char*)metadataToSend);
                    break;
                }
            }
        }

        //printf("%s\n%s\n---\n", messageToSend, receivedMessage);

        /*for (int i = 0; i < MAX_CLIENTS; i++) {
            if (allClients[i] != NULL) {
                printf("Checking %s with %s\n", tokens[3], allClients[i]->username);
                if (strcmp(tokens[3], allClients[i]->username) == 0) {
                    handleWrite(allClients[i]->IP, &headerToSend, (unsigned char*)messageToSend);
                    //TODO handle write in a separate thread
                    break;
                }
            } else {
                break;
            }
        }*/

        for(int i = 0; i < tokenCount; i++) {
            secureFreeString(tokens[i]);
        }
        free(tokens);
    }
    // Cleanup
    close(server_fd);
    return 0;
}