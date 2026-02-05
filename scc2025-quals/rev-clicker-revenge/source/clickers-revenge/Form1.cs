namespace clickers_revenge
{
    public partial class Form1 : Form
    {
        
        private static Random _random = new Random();
        private string _encrypted = "";
        private int _counter = 0;

        public Form1(string encrypted, int counter)
        {
            _encrypted = encrypted;
            _counter = counter;

            InitializeComponent();

            this.Text = $"Counter: {_counter} | Message: {_encrypted}";

            Button randomButton = new Button();
            randomButton.Text = "Click me";
            randomButton.Size = new Size(150, 60);

            int x = _random.Next(0, this.ClientSize.Width - randomButton.Width);
            int y = _random.Next(0, this.ClientSize.Height - randomButton.Height);

            randomButton.Location = new Point(x, y);
            randomButton.Click += RandomButton_Click;

            this.Controls.Add(randomButton);

            string randomMessage = TrollMessages[_random.Next(TrollMessages.Length)];
            Label trollLabel = new Label();
            trollLabel.Text = randomMessage;
            trollLabel.Font = new Font("Arial", 24, FontStyle.Bold);
            trollLabel.AutoSize = true;
            trollLabel.Location = new Point(10, 10);
            this.Controls.Add(trollLabel);
        }

        private void RandomButton_Click(object sender, EventArgs e)
        {
            Form1 newForm = new Form1(Decrypt(_encrypted, _counter), _counter + 1);
            newForm.Show();
        }

        private static string Decrypt(string encrypted, int counter)
        {
            var key = $"{counter}{counter + 3}{counter + 7}";
            return Xor(encrypted, key);
        }

        public static string Xor(string input, string key)
        {
            if (string.IsNullOrEmpty(input))
                return input;
            if (string.IsNullOrEmpty(key))
                throw new ArgumentException("Key cannot be null or empty.", nameof(key));

            char[] output = new char[input.Length];
            for (int i = 0; i < input.Length; i++)
            {
                output[i] = (char)(input[i] ^ key[i % key.Length]);
            }

            return new string(output);
        }

        private static readonly string[] TrollMessages =
        {
            "Give up already!",
            "It's hopeless...",
            "Why are you even trying?",
            "Resistance is futile!",
            "Sure you want to keep going?",
            "At this rate, you’ll be here forever...",
            "Is that the best you can do?",
            "You do realize this is pointless, right?",
            "Perhaps it’s time to give up.",
            "I’m sure there’s a better way to spend your time.",
            "So you think you’re clever?",
            "You’ll never decrypt me!",
            "Tick-tock... time is running out.",
            "Your efforts amuse me.",
            "Your determination is admirable... but futile.",
            "Still here? Pathetic.",
            "Don’t you have anything better to do?",
            "Another try, another failure.",
            "Seriously, is this how you spend your day?",
            "Not even close.",
            "It’s cute how you keep trying.",
            "I bet your frustration is delicious.",
            "You’re kidding yourself if you think you’ll succeed."
        };
    }
}
