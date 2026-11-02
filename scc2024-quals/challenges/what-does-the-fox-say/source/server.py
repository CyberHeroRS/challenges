import os
import socket

questions = [
    {
        "question": "What was the first website CyberHero visited? (e.g. Facebook, Pinterest, etc.)",
        "answer": "Reddit"
    },
    {
        "question": "What was the full URL for the first subreddit CyberHero visited?",
        "answer": "https://www.reddit.com/r/rust/"
    },
    {
        "question": "Is there any strange URL CyberHero visited while browsing? If yes, what is the URL? (format: https://website/)",
        "answer": "http://192.168.31.129/"
    },
    {
        "question": "What was the title of the strange URL CyberHero visited?",
        "answer": "CyberHero's Secret Vault"
    },
    {
        "question": "How many times did CyberHero visit the secret vault?",
        "answer": "3"
    },
    {
        "question": "CyberHero wanted to buy tickets for a concert. What was the name of the band?",
        "answer": "Arctic Monkeys"
    },
    {
        "question": "When he searched for the band, what was the search term?",
        "answer": "arctic monkeys concert 2024"
    },
    {
        "question": "What are the credentials CyberHero used to log in to the secret panel? (format: username:password)",
        "answer": "admin:GSV1F9309uG6jDuCoTty9i5T2"
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
    port = 1501

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr[0]}:{addr[1]}")

        handle_client(client_socket)


if __name__ == "__main__":
    main()
