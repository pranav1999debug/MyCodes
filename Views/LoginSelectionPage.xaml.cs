using PictureLinkViewer.ViewModels;

namespace PictureLinkViewer.Views;

public partial class LoginSelectionPage : ContentPage
{
    public LoginSelectionPage(LoginSelectionViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}