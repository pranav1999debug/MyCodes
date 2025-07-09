using CommunityToolkit.Mvvm.Input;
using PictureLinkViewer.Views;

namespace PictureLinkViewer.ViewModels;

public partial class LoginSelectionViewModel : BaseViewModel
{
    public LoginSelectionViewModel()
    {
        Title = "Picture Link Viewer";
    }

    [RelayCommand]
    private async Task GoToAdminLogin()
    {
        try
        {
            await Shell.Current.GoToAsync(nameof(AdminLoginPage));
        }
        catch (Exception ex)
        {
            SetError($"Navigation error: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task GoToUserLogin()
    {
        try
        {
            await Shell.Current.GoToAsync(nameof(UserLoginPage));
        }
        catch (Exception ex)
        {
            SetError($"Navigation error: {ex.Message}");
        }
    }
}