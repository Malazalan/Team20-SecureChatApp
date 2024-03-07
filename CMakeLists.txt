# CMakeLists.txt

cmake_minimum_required(VERSION 3.0)
project(SecureChatApp)

# Set C standard to C11
set(CMAKE_C_STANDARD 11)

# Add the Server directory
add_subdirectory(Server)

# Add the Client directory
add_subdirectory(Client)
