# Clicker's Return

A reversing challenge featuring an Avalonia .NET desktop application.

## Challenge

Users must click a button exactly at 13.37 seconds, three times in a row, to reveal the flag.

## Building

```bash
cd rev-clickers-return
dotnet build
```

## Running

```bash
dotnet run
```

Or run the compiled binary:

```bash
./bin/Debug/net10.0/ClickersReturn
```

## Solution

The flag is embedded in the binary as a byte array. Use a .NET decompiler (dnSpy, ILSpy, dotPeek) to analyze the `MainWindow.ShowVictory()` method and extract the flag bytes.

Alternatively, you can patch the binary or use a debugger to bypass the timing checks.
