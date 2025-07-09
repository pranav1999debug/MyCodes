using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using PictureLinkViewer.Models;
using PictureLinkViewer.Services;
using System.Collections.ObjectModel;

namespace PictureLinkViewer.ViewModels;

public partial class AdminDashboardViewModel : BaseViewModel
{
    private readonly IAuthenticationService _authService;
    private readonly IPictureLinkService _pictureLinkService;

    [ObservableProperty]
    private ObservableCollection<PictureLink> pictureLinks = new();

    [ObservableProperty]
    private PictureLink? selectedPictureLink;

    [ObservableProperty]
    private bool isEditMode;

    [ObservableProperty]
    private string newTitle = string.Empty;

    [ObservableProperty]
    private string newDescription = string.Empty;

    [ObservableProperty]
    private string newButtonLabel = string.Empty;

    [ObservableProperty]
    private string newTargetUrl = string.Empty;

    [ObservableProperty]
    private string selectedImagePath = string.Empty;

    [ObservableProperty]
    private User? currentUser;

    public AdminDashboardViewModel(IAuthenticationService authService, IPictureLinkService pictureLinkService)
    {
        _authService = authService;
        _pictureLinkService = pictureLinkService;
        Title = "Admin Dashboard";
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
    private async Task SelectImage()
    {
        try
        {
            var result = await FilePicker.PickAsync(new PickOptions
            {
                PickerTitle = "Select an image",
                FileTypes = FilePickerFileType.Images
            });

            if (result != null)
            {
                SelectedImagePath = result.FullPath;
            }
        }
        catch (Exception ex)
        {
            SetError($"Failed to select image: {ex.Message}");
        }
    }

    [RelayCommand]
    private async Task CreatePictureLink()
    {
        if (IsBusy) return;

        try
        {
            IsBusy = true;
            ClearError();

            if (string.IsNullOrWhiteSpace(NewTitle) || string.IsNullOrWhiteSpace(NewButtonLabel) || 
                string.IsNullOrWhiteSpace(NewTargetUrl) || string.IsNullOrWhiteSpace(SelectedImagePath))
            {
                SetError("Please fill in all required fields and select an image.");
                return;
            }

            if (!Uri.TryCreate(NewTargetUrl, UriKind.Absolute, out _))
            {
                SetError("Please enter a valid URL.");
                return;
            }

            // Upload image first
            var fileName = Path.GetFileName(SelectedImagePath);
            var imageUrl = await _pictureLinkService.UploadImageAsync(SelectedImagePath, fileName);

            if (string.IsNullOrEmpty(imageUrl))
            {
                SetError("Failed to upload image.");
                return;
            }

            var pictureLink = new PictureLink
            {
                Title = NewTitle,
                Description = NewDescription,
                ButtonLabel = NewButtonLabel,
                TargetUrl = NewTargetUrl,
                ImageUrl = imageUrl,
                LocalImagePath = SelectedImagePath,
                CreatedBy = CurrentUser?.Email ?? "Unknown"
            };

            var success = await _pictureLinkService.CreatePictureLinkAsync(pictureLink);
            if (success)
            {
                PictureLinks.Insert(0, pictureLink);
                ClearForm();
                await Application.Current!.MainPage!.DisplayAlert("Success", "Picture link created successfully!", "OK");
            }
            else
            {
                SetError("Failed to create picture link.");
            }
        }
        catch (Exception ex)
        {
            SetError($"Failed to create picture link: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task EditPictureLink(PictureLink pictureLink)
    {
        SelectedPictureLink = pictureLink;
        NewTitle = pictureLink.Title;
        NewDescription = pictureLink.Description;
        NewButtonLabel = pictureLink.ButtonLabel;
        NewTargetUrl = pictureLink.TargetUrl;
        SelectedImagePath = pictureLink.LocalImagePath;
        IsEditMode = true;
    }

    [RelayCommand]
    private async Task UpdatePictureLink()
    {
        if (IsBusy || SelectedPictureLink == null) return;

        try
        {
            IsBusy = true;
            ClearError();

            if (string.IsNullOrWhiteSpace(NewTitle) || string.IsNullOrWhiteSpace(NewButtonLabel) || 
                string.IsNullOrWhiteSpace(NewTargetUrl))
            {
                SetError("Please fill in all required fields.");
                return;
            }

            if (!Uri.TryCreate(NewTargetUrl, UriKind.Absolute, out _))
            {
                SetError("Please enter a valid URL.");
                return;
            }

            SelectedPictureLink.Title = NewTitle;
            SelectedPictureLink.Description = NewDescription;
            SelectedPictureLink.ButtonLabel = NewButtonLabel;
            SelectedPictureLink.TargetUrl = NewTargetUrl;

            // Upload new image if selected
            if (!string.IsNullOrEmpty(SelectedImagePath) && SelectedImagePath != SelectedPictureLink.LocalImagePath)
            {
                var fileName = Path.GetFileName(SelectedImagePath);
                var imageUrl = await _pictureLinkService.UploadImageAsync(SelectedImagePath, fileName);
                if (!string.IsNullOrEmpty(imageUrl))
                {
                    SelectedPictureLink.ImageUrl = imageUrl;
                    SelectedPictureLink.LocalImagePath = SelectedImagePath;
                }
            }

            var success = await _pictureLinkService.UpdatePictureLinkAsync(SelectedPictureLink);
            if (success)
            {
                ClearForm();
                await Application.Current!.MainPage!.DisplayAlert("Success", "Picture link updated successfully!", "OK");
            }
            else
            {
                SetError("Failed to update picture link.");
            }
        }
        catch (Exception ex)
        {
            SetError($"Failed to update picture link: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task DeletePictureLink(PictureLink pictureLink)
    {
        try
        {
            var confirm = await Application.Current!.MainPage!.DisplayAlert(
                "Confirm Delete", 
                $"Are you sure you want to delete '{pictureLink.Title}'?", 
                "Yes", "No");

            if (!confirm) return;

            IsBusy = true;
            var success = await _pictureLinkService.DeletePictureLinkAsync(pictureLink.Id);
            if (success)
            {
                PictureLinks.Remove(pictureLink);
                await Application.Current!.MainPage!.DisplayAlert("Success", "Picture link deleted successfully!", "OK");
            }
            else
            {
                SetError("Failed to delete picture link.");
            }
        }
        catch (Exception ex)
        {
            SetError($"Failed to delete picture link: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private void CancelEdit()
    {
        ClearForm();
    }

    [RelayCommand]
    private async Task Logout()
    {
        try
        {
            await _authService.LogoutAsync();
            await Shell.Current.GoToAsync("//LoginSelectionPage");
        }
        catch (Exception ex)
        {
            SetError($"Logout failed: {ex.Message}");
        }
    }

    private void ClearForm()
    {
        NewTitle = string.Empty;
        NewDescription = string.Empty;
        NewButtonLabel = string.Empty;
        NewTargetUrl = string.Empty;
        SelectedImagePath = string.Empty;
        SelectedPictureLink = null;
        IsEditMode = false;
        ClearError();
    }
}