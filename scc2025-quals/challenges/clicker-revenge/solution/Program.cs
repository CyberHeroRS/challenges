namespace solver
{
    internal class Program
    {
        static void Main(string[] args)
        {
            string flag = "kyqMQXPTRPTZdVFlM^mZ@YfRa[XHRUbPWaUDfS_YgP\\IE";
            int i = 0;
            while(true)
            {
                flag = Xor(flag, $"{i}{i + 3}{i + 7}");
                i ++;

                if(flag.StartsWith("SCC{")&& flag.EndsWith("}"))
                {
                    Console.WriteLine(flag);
                    break;
                }
            }

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
    }
}
