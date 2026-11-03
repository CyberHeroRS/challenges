FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pyelftools==0.31 capstone==5.0.3
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solve.py ./
# The real elf-patrol ELF is bind-mounted in at test time. solve.py statically
# disassembles it (capstone) to pull every check constant directly out of its
# own code/.data bytes -- no ptrace/rdtsc/anti-debug exists in this binary, so
# the recovered 41-byte candidate is simply fed to the unmodified binary over
# stdin via a plain subprocess call, and the binary's own "Congrats!" stdout
# is what gets compared against the real $flag_main.
CMD ["sh", "-c", "python solve.py > out.txt; status=$?; cat out.txt; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" out.txt"]
