using PictureLinkViewer.Views;

namespace PictureLinkViewer;

public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();

        // Register routes for navigation
        Routing.RegisterRoute(nameof(AdminLoginPage), typeof(AdminLoginPage));
        Routing.RegisterRoute(nameof(UserLoginPage), typeof(UserLoginPage));
        Routing.RegisterRoute(nameof(AdminDashboardPage), typeof(AdminDashboardPage));
        Routing.RegisterRoute(nameof(UserDashboardPage), typeof(UserDashboardPage));
    }
}