# Baby6502

Very simple reversing challenge.

Builds a Motorola 6502 object and assembly from generated C using a GCC-compatible 6502 toolchain.
Organizer solve helper is in solve.py.

## Build

```sh
make dist
```

If your compiler binary is named differently:

```sh
make dist CC6502=<your-6502-gcc>
```
