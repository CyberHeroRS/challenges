#!/usr/bin/env python3
import socket
import json
import os
import sys
from typing import List, Dict, Any

FLASH_SIZE = 16 * 1024 * 1024
SECTOR_SIZE = 4096
BLOCK_SIZE = 65536

SR_WIP = 0x01
SR_WEL = 0x02
SR_BP0 = 0x04
SR_BP1 = 0x08
SR_BP2 = 0x10

class SPIFlash:
    def __init__(self):
        self.memory = bytearray([0xFF] * FLASH_SIZE)
        self.status_register = 0x00
        self.write_enabled = False

        flag1 = os.getenv('FLAG1', 'SCC{test_flag1_jedec_id_reader}')
        flag2 = os.getenv('FLAG2', 'SCC{test_flag2_memory_writer}')
        flag3 = os.getenv('FLAG3', 'SCC{test_flag3_protection_bypass}')

        welcome_msg = b"SCC2026!!\x00"
        self.memory[0:len(welcome_msg)] = welcome_msg
        
        self.jedec_id = list(flag1.encode())
        
        self.unlock_address = 0x1000
        self.unlock_key = b"UNLOCK"
        self.flag2_address = 0x2000
        
        flag2_bytes = flag2.encode() + b'\x00'
        encrypted_flag2 = self._xor_data(flag2_bytes, 0xAA)
        self.memory[self.flag2_address:self.flag2_address + len(encrypted_flag2)] = encrypted_flag2
        
        self.flag3_address = 0x3000
        self.flag3_sector = self.flag3_address // SECTOR_SIZE
        
        flag3_bytes = flag3.encode() + b'\x00'
        encrypted_flag3 = self._xor_data(flag3_bytes, 0x55)
        self.memory[self.flag3_address:self.flag3_address + len(encrypted_flag3)] = encrypted_flag3
        
        self.status_register = SR_BP0 | SR_BP1
        print(f"[*] Flag3 location: 0x{self.flag3_address:X}")

    def _xor_data(self, data: bytes, key: int) -> bytearray:
        return bytearray([b ^ key for b in data])

    def _is_protected(self, address: int) -> bool:
        if self.status_register & (SR_BP0 | SR_BP1 | SR_BP2):
            if address >= FLASH_SIZE // 2:
                return True
        return False

    def process_command(self, data_out: List[int]) -> List[int]:
        if not data_out:
            return []

        cmd = data_out[0]

        if cmd == 0x9F:
            print(f"[CMD] Read JEDEC ID")
            return self.jedec_id

        elif cmd == 0x05:
            print(f"[CMD] Read Status Register: 0x{self.status_register:02X}")
            return [self.status_register]

        elif cmd == 0x01:
            if len(data_out) >= 2:
                if self.write_enabled:
                    old_sr = self.status_register
                    self.status_register = data_out[1] & 0xFC
                    self.write_enabled = False
                    print(f"[CMD] Write Status Register: 0x{old_sr:02X} -> 0x{self.status_register:02X}")
                else:
                    print(f"[CMD] Write Status Register: FAILED (write not enabled)")
            return []

        elif cmd == 0x06:
            self.write_enabled = True
            self.status_register |= SR_WEL
            print(f"[CMD] Write Enable")
            return []

        elif cmd == 0x04:
            self.write_enabled = False
            self.status_register &= ~SR_WEL
            print(f"[CMD] Write Disable")
            return []

        elif cmd == 0x03:
            if len(data_out) >= 4:
                address = (data_out[1] << 16) | (data_out[2] << 8) | data_out[3]
                length = len(data_out) - 4
                if length == 0:
                    length = 256

                unlock_data = bytes(self.memory[self.unlock_address:self.unlock_address + len(self.unlock_key)])
                if unlock_data == self.unlock_key and address == self.flag2_address:
                    encrypted = self.memory[address:address + length]
                    decrypted = self._xor_data(encrypted, 0xAA)
                    print(f"[CMD] Read Data: addr=0x{address:X}, len={length} (FLAG2 DECRYPTED)")
                    return list(decrypted)

                if address == self.flag3_address:
                    if not self._is_protected(address):
                        encrypted = self.memory[address:address + length]
                        decrypted = self._xor_data(encrypted, 0x55)
                        print(f"[CMD] Read Data: addr=0x{address:X}, len={length} (FLAG3 DECRYPTED)")
                        return list(decrypted)
                    else:
                        print(f"[CMD] Read Data: addr=0x{address:X}, len={length} (PROTECTED - ENCRYPTED)")

                data = self.memory[address:address + length]
                print(f"[CMD] Read Data: addr=0x{address:X}, len={length}")
                return list(data)
            return []

        elif cmd == 0x02:
            if len(data_out) >= 4 and self.write_enabled:
                address = (data_out[1] << 16) | (data_out[2] << 8) | data_out[3]
                write_data = data_out[4:]

                if self._is_protected(address):
                    print(f"[CMD] Page Program: addr=0x{address:X}, FAILED (protected)")
                else:
                    for i, byte in enumerate(write_data):
                        if address + i < FLASH_SIZE:
                            self.memory[address + i] &= byte
                    print(f"[CMD] Page Program: addr=0x{address:X}, len={len(write_data)}")

                self.write_enabled = False
                self.status_register &= ~SR_WEL
            return []

        elif cmd == 0x20:
            if len(data_out) >= 4 and self.write_enabled:
                address = (data_out[1] << 16) | (data_out[2] << 8) | data_out[3]
                sector_address = (address // SECTOR_SIZE) * SECTOR_SIZE

                if self._is_protected(sector_address):
                    print(f"[CMD] Sector Erase: addr=0x{sector_address:X}, FAILED (protected)")
                else:
                    self.memory[sector_address:sector_address + SECTOR_SIZE] = [0xFF] * SECTOR_SIZE
                    print(f"[CMD] Sector Erase: addr=0x{sector_address:X}")

                self.write_enabled = False
                self.status_register &= ~SR_WEL
            return []

        else:
            print(f"[CMD] Unknown: 0x{cmd:02X}")
            return []

    def handle_request(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        data_out = command_data.get('data_out', [])
        readlen = command_data.get('readlen', 0)

        if data_out and isinstance(data_out[0], str):
            data_out = [int(x, 16) for x in data_out]

        response_data = self.process_command(data_out)

        if readlen > 0:
            response_data = response_data[:readlen]

        return response_data

def main():
    host = '0.0.0.0'
    port = int(os.getenv('PORT', '1337'))

    flash = SPIFlash()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"[*] Server listening on port {port}")

        while True:
            try:
                client_socket, address = server_socket.accept()
                print(f"\n[+] Connection from {address}")

                with client_socket:
                    data = b''
                    while True:
                        chunk = client_socket.recv(1024)
                        if not chunk:
                            break
                        data += chunk
                        if data.endswith(b'}'):
                            break

                    if not data:
                        continue

                    try:
                        command_data = json.loads(data.decode('utf-8'))
                        print(f"[<] {command_data}")

                        response = flash.handle_request(command_data)

                        response_json = json.dumps(response).encode('utf-8')
                        client_socket.sendall(response_json)
                        print(f"[>] {response}")

                    except json.JSONDecodeError as e:
                        print(f"[!] JSON decode error: {e}")
                        error_response = json.dumps({"error": "Invalid JSON"}).encode('utf-8')
                        client_socket.sendall(error_response)

            except KeyboardInterrupt:
                print("\n[*] Shutting down server")
                break
            except Exception as e:
                print(f"[!] Error: {e}")
                import traceback
                traceback.print_exc()

if __name__ == '__main__':
    main()