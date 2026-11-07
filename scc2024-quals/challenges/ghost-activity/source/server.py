import os
import socket

# Define your questions and answers
questions = [
    {
        "question": "What are major and minor version of Windows? (<major>.<minor> eg 5.2)",
        "answer": "10.0"
    },
    {
        "question": "What is the username of the current user? ",
        "answer": "cyberhero"
    },
    {
        "question": "What is the nthash of cyberhero's password?",
        "answer": "f8f880509d176c4c4c23c8e55d0da5dc"
    },
    {
        "question": "CyberHero was preparing an email for his friend using popular text editor, what is its pid?",
        "answer": "9096"
    },
    {
        "question": "In the email, CyberHero mentioned marathon. What was friend's name?",
        "answer": "Royce"
    },
    {
        "question": "CyberHero was testing his download speed by trying to download large file using a srcipt language, can you find URL that he was targeting?",
        "answer": "https://hil-speed.hetzner.com/1GB.bin"
    },
    {
        "question": "At which time was connection to that site established? (yyyy-mm-dd hh:mm:ss)",
        "answer": "2024-03-17 13:02:35"
    }
]


def handle_client(client_socket):
    correct = 0
    for q in questions:
        client_socket.sendall(f'{q["question"]}\nAnswer: '.encode())
        client_socket.settimeout(10.0)
        try:
            response = client_socket.recv(1024).decode().strip()
        except socket.timeout:
            client_socket.sendall(b"Timeout: No response received. Disconnecting.\n")
            break

        if response.lower() == q["answer"].lower():
            client_socket.sendall(b"Correct!\n")
            correct += 1
        else:
            client_socket.sendall(b"Wrong answer.\n")
            break
    if correct == len(questions):
        client_socket.sendall(f"Congratulations, here is your flag: {os.environ['FLAG']}\n".encode())
    client_socket.sendall(b"Thanks for playing!\n")
    client_socket.close()


def main():
    host = '0.0.0.0'
    port = 1500

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr[0]}:{addr[1]}")

        try:
            handle_client(client_socket)
        except OSError:
            # A client that disconnects early (e.g. a bare TCP readiness
            # probe) can make a later sendall() fail with a broken pipe;
            # that must not take down the whole server for everyone else.
            pass


if __name__ == "__main__":
    main()
