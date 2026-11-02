FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /solver
COPY solver.csproj Program.cs ./
RUN dotnet publish -c Release -o /out

FROM mcr.microsoft.com/dotnet/runtime:8.0
COPY --from=build /out /solver
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "dotnet /solver/solver.dll > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
