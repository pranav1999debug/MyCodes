using PictureLinkViewer.Models;
using System.Text.Json;

namespace PictureLinkViewer.Services;

public class FirebaseAuthenticationService : IAuthenticationService
{
    private readonly HttpClient _httpClient;
    private readonly string _firebaseApiKey;
    private User? _currentUser;

    public event EventHandler<User?>? AuthStateChanged;

    public FirebaseAuthenticationService(HttpClient httpClient)
    {
        _httpClient = httpClient;
        _firebaseApiKey = "YOUR_FIREBASE_API_KEY"; // Replace with actual API key
    }

    public async Task<bool> LoginAsync(string email, string password)
    {
        try
        {
            var loginData = new
            {
                email = email,
                password = password,
                returnSecureToken = true
            };

            var json = JsonSerializer.Serialize(loginData);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(
                $"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={_firebaseApiKey}",
                content);

            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                var loginResponse = JsonSerializer.Deserialize<Dictionary<string, object>>(responseContent);

                if (loginResponse != null && loginResponse.ContainsKey("localId"))
                {
                    _currentUser = new User
                    {
                        Id = loginResponse["localId"].ToString()!,
                        Email = email,
                        DisplayName = loginResponse.ContainsKey("displayName") ? loginResponse["displayName"].ToString()! : email,
                        Role = IsAdminEmail(email) ? UserRole.Admin : UserRole.User,
                        LastLoginAt = DateTime.UtcNow
                    };

                    AuthStateChanged?.Invoke(this, _currentUser);
                    return true;
                }
            }

            return false;
        }
        catch (Exception ex)
        {
            // Log exception
            System.Diagnostics.Debug.WriteLine($"Login error: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> RegisterAsync(string email, string password, string displayName)
    {
        try
        {
            var registerData = new
            {
                email = email,
                password = password,
                returnSecureToken = true
            };

            var json = JsonSerializer.Serialize(registerData);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(
                $"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={_firebaseApiKey}",
                content);

            if (response.IsSuccessStatusCode)
            {
                var responseContent = await response.Content.ReadAsStringAsync();
                var registerResponse = JsonSerializer.Deserialize<Dictionary<string, object>>(responseContent);

                if (registerResponse != null && registerResponse.ContainsKey("localId"))
                {
                    // Update profile with display name
                    await UpdateProfileAsync(registerResponse["idToken"].ToString()!, displayName);

                    _currentUser = new User
                    {
                        Id = registerResponse["localId"].ToString()!,
                        Email = email,
                        DisplayName = displayName,
                        Role = UserRole.User,
                        CreatedAt = DateTime.UtcNow,
                        LastLoginAt = DateTime.UtcNow
                    };

                    AuthStateChanged?.Invoke(this, _currentUser);
                    return true;
                }
            }

            return false;
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Register error: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> LogoutAsync()
    {
        try
        {
            _currentUser = null;
            AuthStateChanged?.Invoke(this, null);
            return await Task.FromResult(true);
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Logout error: {ex.Message}");
            return false;
        }
    }

    public async Task<User?> GetCurrentUserAsync()
    {
        return await Task.FromResult(_currentUser);
    }

    public async Task<bool> IsUserLoggedInAsync()
    {
        return await Task.FromResult(_currentUser != null);
    }

    public async Task<bool> ResetPasswordAsync(string email)
    {
        try
        {
            var resetData = new
            {
                requestType = "PASSWORD_RESET",
                email = email
            };

            var json = JsonSerializer.Serialize(resetData);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(
                $"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={_firebaseApiKey}",
                content);

            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Password reset error: {ex.Message}");
            return false;
        }
    }

    private async Task<bool> UpdateProfileAsync(string idToken, string displayName)
    {
        try
        {
            var updateData = new
            {
                idToken = idToken,
                displayName = displayName,
                returnSecureToken = true
            };

            var json = JsonSerializer.Serialize(updateData);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(
                $"https://identitytoolkit.googleapis.com/v1/accounts:update?key={_firebaseApiKey}",
                content);

            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Update profile error: {ex.Message}");
            return false;
        }
    }

    private bool IsAdminEmail(string email)
    {
        // Define admin emails here
        var adminEmails = new[] { "admin@picturelink.com", "admin@example.com" };
        return adminEmails.Contains(email.ToLowerInvariant());
    }
}