using PictureLinkViewer.Views;

namespace PictureLinkViewer;

public partial class App : Application
{
    public App()
    {
        InitializeComponent();

        // Start with login selection page
        MainPage = new AppShell();
    }
}