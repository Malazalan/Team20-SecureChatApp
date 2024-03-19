#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <string.h>
#include <arpa/inet.h>
#include <stdarg.h>

#define PORT 54321
#define CLIENT_PORT 12345
#define MAX_CONN 5
#define MAX_PACKET_LENGTH 256
#define HEADER_LENGTH 16
#define MAX_CLIENTS 10
#define DEBUG_THRESHOLD INFO

// Header types
#define metadata 0
#define text 1
#define file 2

// Define ANSI escape codes for colors
#define ANSI_RESET   "\033[0m"
#define ANSI_RED     "\x1B[31m"
#define ANSI_GREEN   "\x1B[32m"
#define ANSI_YELLOW  "\x1B[33m"
#define ANSI_BLUE    "\x1B[34m"
#define ANSI_MAGENTA "\x1B[35m"
#define ANSI_CYAN    "\x1B[36m"

pthread_mutex_t actionLogLock;
pthread_mutex_t debugLogLock;

enum logLevel {
    TRACE,
    DEBUG,
    INFO,
    WARN,
    ALERT,
    CRITICAL,
    FATAL
};

void colourLogLevel(enum logLevel level, char* buffer, int bufSize) {
    switch (level) {
        case TRACE:
            snprintf(buffer, bufSize, "%sTRACE%s", ANSI_CYAN, ANSI_RESET);
            break;
        case DEBUG:
            snprintf(buffer, bufSize, "%sDEBUG%s", ANSI_BLUE, ANSI_RESET);
            break;
        case INFO:
            snprintf(buffer, bufSize, "%sINFO%s", ANSI_GREEN, ANSI_RESET);
            break;
        case WARN:
            snprintf(buffer, bufSize, "%sWARN%s", ANSI_YELLOW, ANSI_RESET);
            break;
        case ALERT:
            snprintf(buffer, bufSize, "%sALERT%s", ANSI_MAGENTA, ANSI_RESET);
            break;
        case CRITICAL:
            snprintf(buffer, bufSize, "%sCRITICAL%s", ANSI_RED, ANSI_RESET);
            break;
        case FATAL:
            snprintf(buffer, bufSize, "%sFATAL%s", ANSI_RED, ANSI_RESET);
            break;
    }
}

int logDebug(enum logLevel level, const char* format, ...) {
    if (level < DEBUG_THRESHOLD) {
        return 0;
    }
    time_t current_time;
    time(&current_time);

    char timeBuffer[80];
    memset(timeBuffer, '\0', 80);
    struct tm * timeInfo;
    timeInfo = localtime(&current_time);
    strftime(timeBuffer, 80, "%Y-%m-%d %H:%M:%S", timeInfo);

    pthread_mutex_lock(&debugLogLock);
    FILE* debugLogFile = fopen("debug.log", "a");
    if (!debugLogFile) {
        pthread_mutex_unlock(&debugLogLock);
        printf("Failed to open debug.log\n");
        return 1;
    }

    char levelBuffer[20];
    colourLogLevel(level, levelBuffer, 19);

    fprintf(debugLogFile, "%s | %s - ", timeBuffer, levelBuffer);
    va_list args;
    va_start(args, format);
    vfprintf(debugLogFile, format, args);
    va_end(args);
    fprintf(debugLogFile, "\n");

    fclose(debugLogFile);
    pthread_mutex_unlock(&debugLogLock);
    return 0;
}

int logAction(enum logLevel level, char* subject, char* format, ...) {
    if (level < DEBUG_THRESHOLD) {
        return 0;
    }
    time_t current_time;
    time(&current_time);

    char timeBuffer[80];
    memset(timeBuffer, '\0', 80);
    struct tm * timeInfo;
    timeInfo = localtime(&current_time);
    strftime(timeBuffer, 80, "%Y-%m-%d %H:%M:%S", timeInfo);

    pthread_mutex_lock(&actionLogLock);
    FILE* actionLogFile = fopen("action.log", "a");
    if (!actionLogFile) {
        pthread_mutex_unlock(&actionLogLock);
        printf("Failed to open action.log\n");
        return 1 + logDebug(CRITICAL, "Failed to open action.log");;
    }

    char levelBuffer[20];
    colourLogLevel(level, levelBuffer, 19);

    fprintf(actionLogFile, "%s | %s - %s : ", timeBuffer, levelBuffer, subject);
    va_list args;
    va_start(args, format);
    vfprintf(actionLogFile, format, args);
    va_end(args);
    fprintf(actionLogFile, "\n");

    fclose(actionLogFile);
    pthread_mutex_unlock(&actionLogLock);
    return 0;
};

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

void secureFree (void * buffer, size_t length) {
    if (buffer) {  // Get the length of the string
        memset(buffer, 0, length);       // Clear the content of the string
        free(buffer);                    // Free the memory
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
        //printf("%02X ", headerBytes[i]);
    }
    //printf("-> ");
}

void handleWrite(char* address, struct Header * messageHeader, struct Header * metadataHeader,
        struct Header * fileMetadataHeader, const unsigned char* messageToSend, const unsigned char* metadataToSend) {
    int sockfd;
    struct sockaddr_in clientAddr;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        logDebug(FATAL, "Failed to create write socket");
        pthread_exit(NULL);
    }

    clientAddr.sin_family = AF_INET;
    logDebug(WARN, "Contacting %s", address);
    clientAddr.sin_addr.s_addr = inet_addr(address);
    clientAddr.sin_port = htons(CLIENT_PORT);

    if (connect(sockfd, (struct sockaddr*)&clientAddr, sizeof(clientAddr)) != 0) {
        logDebug(FATAL, "Failed to connect to client listener");
        pthread_exit(NULL);
    }

    // Send the message header
    unsigned char headerBytes[HEADER_LENGTH];
    convertHeaderToBytes(*messageHeader, headerBytes);
    logDebug(TRACE, "Sending message header");
    send(sockfd, headerBytes, HEADER_LENGTH, 0);

    // Send the metadata header
    convertHeaderToBytes(*metadataHeader, headerBytes);
    logDebug(TRACE, "Sending metadata header");
    send(sockfd, headerBytes, HEADER_LENGTH, 0);

    if (fileMetadataHeader->numberOfPackets > 0) {
        // Send file metadata header
        convertHeaderToBytes(*fileMetadataHeader, headerBytes);
        logDebug(TRACE, "Sending file metadata header");
        send(sockfd, headerBytes, HEADER_LENGTH, 0);
    }

    // Send the packets
    logDebug(TRACE, "Sending message to %s", address);
    //printf("Preparing %s\n", messageToSend);
    for (int packetNum = 0; packetNum < messageHeader->numberOfPackets; packetNum++) {
        logDebug(DEBUG, "Pre malloc 236");
        unsigned char* buffer = malloc(MAX_PACKET_LENGTH);
        logDebug(DEBUG, "Post malloc 236");

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

        logDebug(TRACE, "Sent %d/%d", packetNum + 1, messageHeader->numberOfPackets);
        send(sockfd, buffer, MAX_PACKET_LENGTH, 0);
        logDebug(TRACE, "Pre secureFree 265");
        secureFree(buffer, MAX_PACKET_LENGTH);
        //free(buffer);
        logDebug(TRACE, "Post secureFree 265");
    }
    logDebug(INFO, "Finished");
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
            logDebug(FATAL,  "Memory allocation failed\n");
            exit(EXIT_FAILURE);
        }

        logDebug(DEBUG, "Pre malloc 294");
        tokens[count] = malloc(strlen(token) + 1);
        logDebug(DEBUG, "Post malloc 294");
        if(tokens[count] == NULL) {
            logDebug(FATAL, "Memory allocation failed for token\n");
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
    logDebug(DEBUG, "%d", Alan);
    Alan->username = malloc(strlen("EnergeticTangerine") + 1);
    strncpy(Alan->username, "EnergeticTangerine", strlen("EnergeticTangerine") + 1);
    Alan->usernameSize = strlen("EnergeticTangerine") + 1;
    logDebug(DEBUG, "Pre malloc 327");
    Alan->IP = malloc(strlen("127.0.0.1") + 1);
    logDebug(DEBUG, "Post malloc 327");
    strncpy(Alan->IP, "127.0.0.1", strlen("127.0.0.1") + 1);
    Alan->IPSize = strlen("127.0.0.1") + 1;

    // Joe
    logDebug(DEBUG, "Pre malloc 334");
    struct Client * Joe = malloc(sizeof(struct Client));
    logDebug(DEBUG, "Post malloc 334");
    logDebug(DEBUG, "Pre malloc 337");
    Joe->username = malloc(strlen("ResourcefulBoysenberry") + 1);
    logDebug(DEBUG, "Post malloc 337");
    strncpy(Joe->username, "ResourcefulBoysenberry", strlen("ResourcefulBoysenberry") + 1);
    Joe->usernameSize = strlen("ResourcefulBoysenberry") + 1;
    logDebug(DEBUG, "Pre malloc 342");
    Joe->IP = malloc(strlen("127.0.0.1") + 1);
    logDebug(DEBUG, "Post malloc 342");
    strncpy(Joe->IP, "127.0.0.1", strlen("127.0.0.1") + 1);
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
        logDebug(FATAL, "Error creating socket");
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }

    // Tell the server to reuse ports even if in use by other processes
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        logDebug(FATAL, "Error setting sockopt");
        perror("Error setting sockopt");
        exit(EXIT_FAILURE);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY; // Is accepting ANY request smart or secure? No. Do I care? Also no.
    address.sin_port = htons(PORT);

    // Bind to the port
    if (bind(server_fd, (struct sockaddr*) &address, sizeof(address)) < 0) {
        logDebug(FATAL, "Error binding server");
        perror("Error binding server");
        exit(EXIT_FAILURE);
    }

    for (;;) {
        // Wait for a connection
        if (listen(server_fd, MAX_CONN) < 0) {
            logDebug(FATAL, "Error listening");
            exit(EXIT_FAILURE);
        }

        logDebug(INFO, "Ready to receive");
        if ((new_client = accept(server_fd, (struct sockaddr*) &address, &addrlen)) < 0) {
            logDebug(FATAL, "Error accepting new client connection");
            exit(EXIT_FAILURE);
        }

        // Receive message header
        logDebug(TRACE, "Receive message header");
        unsigned char num_message_packets[HEADER_LENGTH];  // Assuming the length is represented using MAX_PACKET_LENGTH bytes
        if (recv(new_client, num_message_packets, HEADER_LENGTH, 0) < 0) {
            logDebug(ALERT, "Error receiving number of message packets");
            //exit(EXIT_FAILURE);
            close(new_client);
            continue;
        }
        unsigned char messageType = num_message_packets[0];

        // Convert the bytes to an integer - ignoring the first byte
        logDebug(TRACE, "Convert message header");
        int int_message_packets = 0;
        for (int i = 1; i < HEADER_LENGTH; i++) {
            int_message_packets |= (num_message_packets[i] & 0xFF) << ((i-1) * 8);
        }

        // Receive metadata header
        logDebug(TRACE, "Receive metadata header");
        unsigned char num_metadata_packets[HEADER_LENGTH];  // Assuming the length is represented using MAX_PACKET_LENGTH bytes
        if (recv(new_client, num_metadata_packets, HEADER_LENGTH, 0) < 0) {
            logDebug(ALERT, "Error receiving number of metadata packets");
            //exit(EXIT_FAILURE);
            close(new_client);
            continue;
        }

        // Convert the bytes to an integer - ignoring the first byte
        logDebug(TRACE, "Convert metadata header");
        int int_metadata_packets = 0;
        for (int i = 1; i < HEADER_LENGTH; i++) {
            int_metadata_packets |= (num_metadata_packets[i] & 0xFF) << ((i-1) * 8);
        }

        unsigned char num_file_metadata_packets[HEADER_LENGTH];
        int int_file_metadata_packets = 0;
        if (messageType == file) {
            logDebug(TRACE, "Receive file metadata header\n");
            if (recv(new_client, num_file_metadata_packets, HEADER_LENGTH, 0) < 0) {
                logDebug(ALERT, "Error receiving number of file size");
                //exit(EXIT_FAILURE);
                close(new_client);
                continue;
            }
            for (int i = 1; i < HEADER_LENGTH; i++) {
                int_file_metadata_packets |= (num_file_metadata_packets[i] & 0xFF) << ((i-1) * 8);
            }
            logDebug(DEBUG, "The file is %d bytes long\n", int_file_metadata_packets);
        }

        logDebug(DEBUG, "Expecting %d message packets", int_message_packets);
        logDebug(DEBUG, "Expecting %d metadata packets", int_metadata_packets);

        logDebug(DEBUG, "Pre malloc 443");
        unsigned char* receivedMessage = malloc(int_message_packets * MAX_PACKET_LENGTH);
        logDebug(DEBUG, "Post malloc 443");
        int nextChar = 0;
        //printf("Saved message\n");
        for (int message_id = 0; message_id < int_message_packets; message_id++) {
            if (recv(new_client, buffer, MAX_PACKET_LENGTH, 0) < 0) {
                logDebug(CRITICAL, "Error receiving file size");
                perror("Error receiving message contents");
                //exit(EXIT_FAILURE);
                close(new_client);
                continue;
            }
            for (int charNum = 0; charNum < MAX_PACKET_LENGTH; charNum++) {
                receivedMessage[nextChar] = buffer[charNum];
                nextChar++;
                //printf("%d", buffer[charNum]);
            }
            //printf("%s", buffer);
        }
        //printf("\nSaved message\n%d\n", receivedMessage);
        logDebug(DEBUG, "Pre malloc 461");
        char* receivedMetadata = malloc(int_metadata_packets * MAX_PACKET_LENGTH);
        logDebug(DEBUG, "Pre malloc 462");
        nextChar = 0;
        for (int message_id = 0; message_id < int_metadata_packets; message_id++) {
            if (recv(new_client, buffer, MAX_PACKET_LENGTH, 0) < 0) {
                logDebug(FATAL, "Error receiving message contents");
                //exit(EXIT_FAILURE);
                close(new_client);
                continue;
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
        logDebug(TRACE, "Sender - %s", tokens[0]);
        logDebug(TRACE, "Target - %s", tokens[1]);
        logDebug(TRACE, "Timestamp - %s", tokens[2]);
        logAction(INFO, tokens[0], "Send type %d", messageType);

        struct Header messageHeader;
        messageHeader.numberOfPackets = int_message_packets;
        messageHeader.messageType = messageType;

        struct Header metadataHeader;
        metadataHeader.numberOfPackets = int_metadata_packets;
        metadataHeader.messageType = 0;

        struct Header fileMetadataHeader;
        fileMetadataHeader.numberOfPackets = int_file_metadata_packets;
        metadataHeader.messageType = 0;

        //printf("\n\n");

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
                logDebug(TRACE, "Checking %s with %s", tokens[1], allClients[i]->username);
                if (strcmp(tokens[1], allClients[i]->username) == 0) {
                    logDebug(TRACE, "Metadata -> %s", metadataToSend);

                    handleWrite(allClients[i]->IP, &messageHeader, &metadataHeader, &fileMetadataHeader,
                               receivedMessage, (unsigned char*)metadataToSend);
                    break;
                }
            } else {
                logAction(WARN, tokens[0], "Cannot find %s", tokens[1]);
                break;
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
            secureFree(tokens[i], strlen(tokens[i]));
        }
        free(tokens);
    }
    // Cleanup
    close(server_fd);
    return 0;
}