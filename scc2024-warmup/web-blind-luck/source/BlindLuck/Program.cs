using Microsoft.AspNetCore.Mvc;

namespace BlindLuck
{
    public class Program
    {
        public static void Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            // Add services to the container.
            builder.Services.AddRazorPages()
                        .AddRazorPagesOptions(options =>
                         {
                             options.Conventions.ConfigureFilter(new IgnoreAntiforgeryTokenAttribute());
                         });

            var app = builder.Build();

            app.UseHttpsRedirection();
            app.UseStaticFiles();

            app.UseRouting();

            app.UseAuthorization();

            app.MapRazorPages();

            app.Run();
        }
    }
}
