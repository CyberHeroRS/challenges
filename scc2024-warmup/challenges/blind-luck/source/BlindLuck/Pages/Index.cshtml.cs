using Microsoft.AspNetCore.Mvc.RazorPages;

namespace BlindLuck.Pages
{
    public class IndexModel : PageModel
    {
        private static string _flag = "SCC{l00k1n6_1n70_7h3_fu7ur3e}";

        private Random _random = new Random();

        public string Message { get; set; } = "";
        public string Time { get; set; } = "";

        public void OnGet()
        {

        }

        private readonly string[] failMessages =
        [
            "Nope, that's not it. Maybe try 'Password123'?",
            "Wrong! But don't worry, it's just a password",
            "Incorrect. Did you let your cat walk on the keyboard again?",
            "Oh, so close! Just kidding, not even close.",
            "Error 404: Password not found."
        ];


        public void OnPostCheckPassword()
        {
            var inputPassword = Request.Form["Password"];
            
            var (validPassword, ticks) = CheckPassword(inputPassword);
            Time = $"Time taken: {ticks * 50}ms";

            if(validPassword)
            {
                Message = "You succeeded. But at what cost?";
            }
            else
            {
                int index = _random.Next(failMessages.Length);
                Message = failMessages[index];
            }
        }

        private (bool, int) CheckPassword(string? password)
        {
            if (password == null)
            {
                return (false, 0);
            }

            for (int i = 0; i < _flag.Length; i++)
            {
                if(i >= password.Length || password[i] != _flag[i])
                {
                    return (false, i);
                }

                Thread.Sleep(50);
            }

            return (true, _flag.Length);
        }
    }
}
