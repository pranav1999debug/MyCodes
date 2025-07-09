using PictureLinkViewer.Models;

namespace PictureLinkViewer.Services;

public interface IAuthenticationService
{
    Task<bool> LoginAsync(string email, string password);
    Task<bool> RegisterAsync(string email, string password, string displayName);
    Task<bool> LogoutAsync();
    Task<User?> GetCurrentUserAsync();
    Task<bool> IsUserLoggedInAsync();
    Task<bool> ResetPasswordAsync(string email);
    event EventHandler<User?> AuthStateChanged;
}