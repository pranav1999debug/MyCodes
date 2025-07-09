using PictureLinkViewer.ViewModels;

namespace PictureLinkViewer.Views;

public partial class AdminLoginPage : ContentPage
{
    public AdminLoginPage(AdminLoginViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}