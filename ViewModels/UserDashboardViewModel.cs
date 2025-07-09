using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PictureLinkViewer.Models;
using PictureLinkViewer.Services;
using System.Collections.ObjectModel;

namespace PictureLinkViewer.ViewModels;

public partial class UserDashboardViewModel : BaseViewModel
{
    private readonly IAuthenticationService _authService;
    private readonly IPictureLinkService _pictureLinkService;

    [ObservableProperty]
    private ObservableCollection<PictureLink> pictureLinks = new();

    [ObservableProperty]
    private User? currentUser;

    [ObservableProperty]
    private bool isRefreshing;

    public UserDashboardViewModel(IAuthenticationService authService, IPictureLinkService pictureLinkService)
    {
        _authService = authService;
        _pictureLinkService = pictureLinkService;
        Title = "Picture Links";
    }

    public async Task InitializeAsync()
    {
        CurrentUser = await _authService.GetCurrentUserAsync();
        await LoadPictureLinksAsync();
    }

    [RelayCommand]
    private async Task LoadPictureLinks()
    {
        if (IsBusy) return;

        try
        {
            IsBusy = true;
            ClearError();

            var links = await _pictureLinkService.GetAllPictureLinksAsync();
            PictureLinks.Clear();
            foreach (var link in links)
            {
                PictureLinks.Add(link);
            }
        }
        catch (Exception ex)
        {
            SetError($"Failed to load picture links: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task RefreshPictureLinks()
    {
        if (IsRefreshing) return;

        try
        {
            IsRefreshing = true;
            ClearError();

            var links = await _pictureLinkService.GetAllPictureLinksAsync();
            PictureLinks.Clear();
            foreach (var link in links)
            {
                PictureLinks.Add(link);
            }
        }
        catch (Exception ex)
        {
            SetError($"Failed to refresh picture links: {ex.Message}");
        }
        finally
        {
            IsRefreshing = false;
        }
    }

    [RelayCommand]
    private async Task OpenLink(string url)
    {
        try
        {
            if (!string.IsNullOrEmpty(url))
            {
                if (!Uri.TryCreate(url, UriKind.Absolute, out Uri? uri))
                {
                    // If the URL doesn't have a scheme, add https://
                    url = $"https://{url}";
                    if (!Uri.TryCreate(url, UriKind.Absolute, out uri))
                    {
                        SetError("Invalid URL format.");
                        return;
                    }
                }

                await Browser.OpenAsync(uri, BrowserLaunchMode.SystemPreferred);
            }
        }
        catch (Exception ex)
        {
            SetError($"Failed to open link: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task ViewImageFullscreen(string imageUrl)
    {
        try
        {
            if (!string.IsNullOrEmpty(imageUrl))
            {
                // For a full implementation, you might want to create a custom page
                // to display the image in fullscreen mode
                await Application.Current!.MainPage!.DisplayAlert("Image", "Image fullscreen view would open here", "OK");
            }
        }
        catch (Exception ex)
        {
            SetError($"Failed to view image: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task Logout()
    {
        try
        {
            var confirm = await Application.Current!.MainPage!.DisplayAlert(
                "Logout", 
                "Are you sure you want to logout?", 
                "Yes", "No");

            if (confirm)
            {
                await _authService.LogoutAsync();
                await Shell.Current.GoToAsync("//LoginSelectionPage");
            }
        }
        catch (Exception ex)
        {
            SetError($"Logout failed: {ex.Message}");
        }
    }
}