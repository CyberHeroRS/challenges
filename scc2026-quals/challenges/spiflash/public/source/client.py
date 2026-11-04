import socket
import json

def exchange(hex_list, value=0):
    host = '127.0.0.1'
    port = 1337
    cs = 0
    usb_device_url = 'ftdi://ftdi:2232h/1'

    command_data = {
        "tool": "pyftdi",
        "cs_pin": cs,
        "url": usb_device_url,
        "data_out": [hex(x) for x in hex_list],
        "readlen": value
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(json.dumps(command_data).encode('utf-8'))
        data = b''
        while True:
            data += s.recv(1024)
            if data.endswith(b']'):
                break
        response = json.loads(data.decode('utf-8'))
        return response

if __name__ == '__main__':
    data = exchange([0x03, 0x00, 0x00, 0x00], 10)
    print(data)