using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PictureLinkViewer.Models;
using PictureLinkViewer.Services;
using PictureLinkViewer.Views;

namespace PictureLinkViewer.ViewModels;

public partial class AdminLoginViewModel : BaseViewModel
{
    private readonly IAuthenticationService _authService;

    [ObservableProperty]
    private string email = string.Empty;

    [ObservableProperty]
    private string password = string.Empty;

    [ObservableProperty]
    private bool isPasswordVisible;

    public AdminLoginViewModel(IAuthenticationService authService)
    {
        _authService = authService;
        Title = "Admin Login";
    }

    [RelayCommand]
    private async Task Login()
    {
        if (IsBusy) return;

        try
        {
            IsBusy = true;
            ClearError();

            if (string.IsNullOrWhiteSpace(Email) || string.IsNullOrWhiteSpace(Password))
            {
                SetError("Please enter both email and password.");
                return;
            }

            var success = await _authService.LoginAsync(Email, Password);
            if (success)
            {
                var user = await _authService.GetCurrentUserAsync();
                if (user?.Role == UserRole.Admin)
                {
                    await Shell.Current.GoToAsync($"//{nameof(AdminDashboardPage)}");
                }
                else
                {
                    SetError("You do not have admin privileges.");
                    await _authService.LogoutAsync();
                }
            }
            else
            {
                SetError("Invalid email or password.");
            }
        }
        catch (Exception ex)
        {
            SetError($"Login failed: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private void TogglePasswordVisibility()
    {
        IsPasswordVisible = !IsPasswordVisible;
    }

    [RelayCommand]
    private async Task GoBack()
    {
        await Shell.Current.GoToAsync("..");
    }

    [RelayCommand]
    private async Task ForgotPassword()
    {
        if (string.IsNullOrWhiteSpace(Email))
        {
            SetError("Please enter your email address first.");
            return;
        }

        try
        {
            IsBusy = true;
            var success = await _authService.ResetPasswordAsync(Email);
            if (success)
            {
                await Application.Current!.MainPage!.DisplayAlert(
                    "Password Reset", 
                    "Password reset email sent successfully.", 
                    "OK");
            }
            else
            {
                SetError("Failed to send password reset email.");
            }
        }
        catch (Exception ex)
        {
            SetError($"Password reset failed: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }
}