using System.Security.Cryptography;
using System.Text;

namespace generator
{
    internal class Program
    {
        public static void Main(string[] args)
        {
            string flag = "SCC{clicking_is_so_fun_i_could_do_it_all_day}";
            for (int i = 9876; i >= 0; i--)
            {
                flag = Xor(flag, $"{i}{i+3}{i+7}");
            }

            Console.WriteLine(flag);
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
