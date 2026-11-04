using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Threading;
using System;
using System.Text;

namespace ClickersReturn;

public partial class MainWindow : Window
{
    private static readonly int[] TargetTicks = { 1337, 6769, 420 }; // 10ms per tick
    private const int RequiredRounds = 3;
    
    // LCG parameters for each round (multiplier, addend)
    private static readonly (uint mult, uint add)[] LcgParams = {
        (1103515245, 12345),      // Round 1 - classic glibc
        (214013, 2531011),        // Round 2 - MSVC
        (1664525, 1013904223)     // Round 3 - Numerical Recipes
    };
    
    // Triple-encrypted flag (will be decrypted progressively)
    // Encrypted with: XOR(key1) -> ADD(key2) -> ROL(key3)
    private static readonly byte[] EncryptedFlag = {
        0x81, 0xC1, 0x7F, 0x49, 0x05, 0x88, 0x17, 0x28, 0xB1, 0x88, 0x3F, 0xD9,
        0x7E, 0x9D, 0xF7, 0x2D, 0x19, 0x85, 0x03, 0x10, 0x6D, 0x51, 0x57
    };

    private readonly DispatcherTimer _displayTimer;
    private int _currentRound = 0;
    private bool _isRunning = false;
    
    // Key generation state - tick count IS the time
    private uint _keyAccumulator = 0;
    private int _tickCount = 0;
    private readonly uint[] _collectedKeys = new uint[3];

    private int CurrentTargetTick => TargetTicks[_currentRound];
    private double CurrentTargetTime => CurrentTargetTick / 100.0;

    public MainWindow()
    {
        InitializeComponent();

        _displayTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromMilliseconds(10)
        };
        _displayTimer.Tick += UpdateDisplay;

        UpdateRoundDisplay();
    }

    private void OnButtonClick(object? sender, RoutedEventArgs e)
    {
        if (!_isRunning)
        {
            StartTimer();
        }
        else
        {
            CheckClick();
        }
    }

    private void StartTimer()
    {
        _isRunning = true;
        _displayTimer.Start();
        
        // Reset key generation for this round
        _keyAccumulator = 0;
        _tickCount = 0;

        ActionButton.Content = "CLICK!";
        ActionButton.Background = new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#16c79a"));
        StatusText.Text = $"Click at exactly {CurrentTargetTime:F2} seconds!";
        InstructionText.Text = $"Round {_currentRound + 1} of {RequiredRounds}";
    }

    private void CheckClick()
    {
        _displayTimer.Stop();
        _isRunning = false;

        // Time is derived purely from tick count
        double elapsed = _tickCount / 100.0;
        int tickDifference = Math.Abs(_tickCount - CurrentTargetTick);

        TimerText.Text = elapsed.ToString("F2");

        // Check if tick count matches target exactly
        if (_tickCount == CurrentTargetTick)
        {
            // Capture the key from the accumulator at this exact tick
            _collectedKeys[_currentRound] = _keyAccumulator;
            
            _currentRound++;
            UpdateRoundDisplay();

            if (_currentRound >= RequiredRounds)
            {
                ShowVictory();
            }
            else
            {
                StatusText.Text = $"Perfect! Tick {_tickCount} - {RequiredRounds - _currentRound} more to go!";
                StatusText.Foreground = new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#16c79a"));
                ActionButton.Content = "NEXT ROUND";
                ActionButton.Background = new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#e94560"));
            }
        }
        else
        {
            // Failed - reset progress and clear collected keys
            _currentRound = 0;
            Array.Clear(_collectedKeys, 0, _collectedKeys.Length);
            UpdateRoundDisplay();

            string message = _tickCount < CurrentTargetTick
                ? $"Too early! ({tickDifference * 10}ms off)"
                : $"Too late! ({tickDifference * 10}ms off)";

            StatusText.Text = $"{message} - Starting over!";
            StatusText.Foreground = new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#e94560"));
            ActionButton.Content = "TRY AGAIN";
            ActionButton.Background = new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#e94560"));
        }
    }

    private void UpdateDisplay(object? sender, EventArgs e)
    {
        // Update key accumulator using LCG for current round
        _tickCount++;
        var (mult, add) = LcgParams[_currentRound];
        _keyAccumulator = unchecked(_keyAccumulator * mult + add);
        
        // Display time derived from tick count
        double elapsed = _tickCount / 100.0;
        TimerText.Text = elapsed.ToString("F2");

#if DEBUG
        // Auto-click at exact target tick for testing
        if (_tickCount == CurrentTargetTick)
        {
            CheckClick();
            return;
        }
#endif

        // Color feedback based on proximity to target
        if (elapsed >= CurrentTargetTime - 0.5 && elapsed <= CurrentTargetTime + 0.5)
        {
            TimerText.Foreground = new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#f9ed69"));
        }
        else if (elapsed > CurrentTargetTime + 0.5)
        {
            TimerText.Foreground = new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#e94560"));
        }
        else
        {
            TimerText.Foreground = new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#16c79a"));
        }
    }

    private void UpdateRoundDisplay()
    {
        RoundText.Text = $"{_currentRound}/{RequiredRounds}";
    }

    private void ShowVictory()
    {
        // Progressive decryption using collected keys
        byte[] data = (byte[])EncryptedFlag.Clone();
        
        // Layer 1: XOR decryption with key from round 1 (13.37s)
        DecryptXor(data, _collectedKeys[0]);
        
        // Layer 2: Subtraction cipher with key from round 2 (67.69s)
        DecryptSubtract(data, _collectedKeys[1]);
        
        // Layer 3: Bit rotation with key from round 3 (4.20s)
        DecryptRotate(data, _collectedKeys[2]);
        
        string flag = Encoding.ASCII.GetString(data);

        TimerText.Text = "🏆";
        TimerText.FontSize = 96;
        InstructionText.Text = "CONGRATULATIONS!";
        InstructionText.Foreground = new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#f9ed69"));
        StatusText.Text = $"Flag: {flag}";
        StatusText.Foreground = new Avalonia.Media.SolidColorBrush(Avalonia.Media.Color.Parse("#16c79a"));
        ActionButton.IsVisible = false;
    }
    
    // Layer 1: XOR each byte with rotating key bytes
    private static void DecryptXor(byte[] data, uint key)
    {
        byte[] keyBytes = BitConverter.GetBytes(key);
        for (int i = 0; i < data.Length; i++)
        {
            data[i] ^= keyBytes[i % 4];
        }
    }
    
    // Layer 2: Subtract key bytes (reverse of addition cipher)
    private static void DecryptSubtract(byte[] data, uint key)
    {
        byte[] keyBytes = BitConverter.GetBytes(key);
        for (int i = 0; i < data.Length; i++)
        {
            data[i] = (byte)(data[i] - keyBytes[i % 4]);
        }
    }
    
    // Layer 3: Rotate bits right (reverse of left rotation)
    private static void DecryptRotate(byte[] data, uint key)
    {
        int rotation = (int)(key % 7) + 1; // 1-7 bit rotation
        for (int i = 0; i < data.Length; i++)
        {
            data[i] = (byte)((data[i] >> rotation) | (data[i] << (8 - rotation)));
        }
    }
}
