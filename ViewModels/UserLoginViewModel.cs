using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PictureLinkViewer.Services;
using PictureLinkViewer.Views;

namespace PictureLinkViewer.ViewModels;

public partial class UserLoginViewModel : BaseViewModel
{
    private readonly IAuthenticationService _authService;

    [ObservableProperty]
    private string email = string.Empty;

    [ObservableProperty]
    private string password = string.Empty;

    [ObservableProperty]
    private string displayName = string.Empty;

    [ObservableProperty]
    private bool isPasswordVisible;

    [ObservableProperty]
    private bool isLoginMode = true;

    public UserLoginViewModel(IAuthenticationService authService)
    {
        _authService = authService;
        Title = "User Login";
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
                await Shell.Current.GoToAsync($"//{nameof(UserDashboardPage)}");
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
    private async Task Register()
    {
        if (IsBusy) return;

        try
        {
            IsBusy = true;
            ClearError();

            if (string.IsNullOrWhiteSpace(Email) || string.IsNullOrWhiteSpace(Password) || string.IsNullOrWhiteSpace(DisplayName))
            {
                SetError("Please fill in all fields.");
                return;
            }

            if (Password.Length < 6)
            {
                SetError("Password must be at least 6 characters long.");
                return;
            }

            var success = await _authService.RegisterAsync(Email, Password, DisplayName);
            if (success)
            {
                await Shell.Current.GoToAsync($"//{nameof(UserDashboardPage)}");
            }
            else
            {
                SetError("Registration failed. Email may already be in use.");
            }
        }
        catch (Exception ex)
        {
            SetError($"Registration failed: {ex.Message}");
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
    private void ToggleMode()
    {
        IsLoginMode = !IsLoginMode;
        Title = IsLoginMode ? "User Login" : "User Registration";
        ClearError();
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