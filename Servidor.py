# Elaborado por Trinidad González Alan Isaac
import socket
import random
import time
import sys
import threading


def servirPorSiempre(socketTcp, listaconexiones):
    try:
        while True:
            client_conn, client_addr = socketTcp.accept()
            print("Conectado a", client_addr)
            listaconexiones.append(client_conn)
            thread_read = threading.Thread(target=recibir_datos, args=[client_conn, client_addr, listaconexiones])
            thread_read.start()
            gestion_conexiones(listaconexiones)
    except Exception as e:
        print(e)


def gestion_conexiones(listaconexiones):
    conexiones_cerradas = []
    for conn in listaconexiones: # Estaremos en la lista de las conexiones establecidas
        if conn.fileno() == -1:
            conexiones_cerradas.append(conn)
    for conn in conexiones_cerradas:
        listaconexiones.remove(conn)
    print("hilos activos:", threading.active_count())
    print("enum", threading.enumerate())
    print("conexiones: ", len(listaconexiones))
    print(listaconexiones)


def recibir_datos(conn, addr, listaconexiones):
    try:
        cur_thread = threading.current_thread()
        print("Recibiendo datos del cliente {} en el {}".format(addr, cur_thread.name))

        # Crear el tablero del memorama
        BOARD_SIZE = 4
        values = list(range(1, (BOARD_SIZE * BOARD_SIZE) // 2 + 1)) * 2
        random.shuffle(values)
        board = [[0] * BOARD_SIZE for i in range(BOARD_SIZE)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                board[i][j] = values.pop()
        revealed = [[False for _ in range(len(board))] for _ in range(len(board[0]))]

        # Jugar al memorama
        matches = 0
        while matches < (len(board) * len(board[0])) // 2:
            # Enviar el tablero actual a todos los clientes
            board_string = ""
            for i in range(len(board)):
                row_str = " ".join([str(board[i][j]) if revealed[i][j] else "-" for j in range(len(board[i]))])
                board_string += row_str + "\n"
            for conn in listaconexiones:
                conn.sendall(board_string.encode())

            # Recibir la posición de la primera carta del cliente
            card_1_pos = conn.recv(1024).decode()
            if card_1_pos == "exit":
                conn.sendall("¡Juego cancelado por el usuario!".encode())
                break
            card_1_row, card_1_col = int(card_1_pos[0]), int(card_1_pos[1])
            revealed[card_1_row][card_1_col] = True

            # Enviar el tablero con la primera carta revelada a todos los clientes
            board_string = ""
            for i in range(len(board)):
                row_str = " ".join([str(board[i][j]) if revealed[i][j] else "-" for j in range(len(board[i]))])
                board_string += row_str + "\n"
            for conn in listaconexiones:
                conn.sendall(board_string.encode())

            # Recibir la posición de la segunda carta del cliente
            card_2_pos = conn.recv(1024).decode()
            if card_2_pos == "exit":
                conn.sendall("¡Juego cancelado por el usuario!".encode())
                break
            card_2_row, card_2_col = int(card_2_pos[0]), int(card_2_pos[1])
            revealed[card_2_row][card_2_col] = True

            # Enviar el tablero con las dos cartas reveladas a todos los clientes
            board_string = ""
            for i in range(len(board)):
                row_str = " ".join([str(board[i][j]) if revealed[i][j] else "-" for j in range(len(board[i]))])
                board_string += row_str + "\n"
            for conn in listaconexiones:
                conn.sendall(board_string.encode())

            # Comprobar si las cartas son iguales
            if board[card_1_row][card_1_col] == board[card_2_row][card_2_col]:
                matches += 1
                message = "¡Cartas iguales! "
                if matches == (len(board) * len(board[0])) // 2:
                    message += "¡Felicidades! Has completado el memorama."
            else:
                message = "¡Cartas diferentes! Sigue intentando."
                time.sleep(2)
                revealed[card_1_row][card_1_col] = False
                revealed[card_2_row][card_2_col] = False

            # Enviar la respuesta a todos los clientes
            for conn in listaconexiones:
                conn.sendall(message.encode())
    except Exception as e:
        print(e)
    finally:
        conn.close()

listaconexiones = []

# Definir HOST y PORT
HOST = "192.168.1.75"
PORT = 44000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind((HOST, PORT))
    TCPServerSocket.listen()
    print(f"Servidor escuchando en {HOST}:{PORT}")

    while True:
        client_conn, client_addr = TCPServerSocket.accept()
        print(f"Conexión establecida desde {client_addr}.")
        listaconexiones.append(client_conn)
        thread_read = threading.Thread(target=recibir_datos, args=[client_conn, client_addr, listaconexiones]) # Creamos el hilo
        thread_read.start() # Inicia el hilo
        gestion_conexiones(listaconexiones) # Con esto gestionamos las conexiones