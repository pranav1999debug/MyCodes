using PictureLinkViewer.ViewModels;

namespace PictureLinkViewer.Views;

public partial class UserLoginPage : ContentPage
{
    public UserLoginPage(UserLoginViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}