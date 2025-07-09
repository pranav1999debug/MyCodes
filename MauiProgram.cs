using Microsoft.Extensions.Logging;
using PictureLinkViewer.Services;
using PictureLinkViewer.ViewModels;
using PictureLinkViewer.Views;

namespace PictureLinkViewer;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            });

        // Register HttpClient
        builder.Services.AddHttpClient();

        // Register Services
        builder.Services.AddSingleton<IAuthenticationService, FirebaseAuthenticationService>();
        builder.Services.AddSingleton<IPictureLinkService, FirebasePictureLinkService>();

        // Register ViewModels
        builder.Services.AddTransient<LoginSelectionViewModel>();
        builder.Services.AddTransient<AdminLoginViewModel>();
        builder.Services.AddTransient<UserLoginViewModel>();
        builder.Services.AddTransient<AdminDashboardViewModel>();
        builder.Services.AddTransient<UserDashboardViewModel>();

        // Register Views
        builder.Services.AddTransient<LoginSelectionPage>();
        builder.Services.AddTransient<AdminLoginPage>();
        builder.Services.AddTransient<UserLoginPage>();
        builder.Services.AddTransient<AdminDashboardPage>();
        builder.Services.AddTransient<UserDashboardPage>();

        builder.Logging.AddDebug();

        return builder.Build();
    }
}