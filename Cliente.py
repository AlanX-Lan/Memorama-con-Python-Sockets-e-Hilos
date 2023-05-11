# Elaborado por Trinidad González Alan Isaac
import socket

# Configurar el cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Solicitar al usuario que ingrese el host y el puerto para la conexión del socket
HOST = input("Ingresa el host para el servidor: ")
PORT = int(input("Ingresa el puerto para el servidor: "))

# Conectarse al servidor
client_socket.connect((HOST, PORT))

# Jugar al memorama
while True:
    # Recibir el tablero del servidor
    board_str = client_socket.recv(4096).decode()
    print(board_str)

    # Solicitar la posición de la primera carta al usuario
    card_1_pos = input("Ingresa la posición de la primera carta (fila y columna, ej. 00) o 'exit' para salir: ")
    if card_1_pos == "exit":
        client_socket.sendall("exit".encode())
        break
    client_socket.sendall(card_1_pos.encode())

    # Recibir el tablero del servidor con la primera carta revelada
    board_str = client_socket.recv(4096).decode()
    print(board_str)

    # Solicitar la posición de la segunda carta al usuario
    card_2_pos = input("Ingresa la posición de la segunda carta (fila y columna, ej. 00): ")
    client_socket.sendall(card_2_pos.encode())

    # Recibir la respuesta del servidor
    message = client_socket.recv(1024).decode()
    print(message)
    #if "¡Felicidades!" in message:
        #client_socket.close()
        #break

# Cerrar la conexión
client_socket.close()