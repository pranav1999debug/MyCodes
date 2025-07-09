using PictureLinkViewer.Models;
using System.Text.Json;

namespace PictureLinkViewer.Services;

public class FirebasePictureLinkService : IPictureLinkService
{
    private readonly HttpClient _httpClient;
    private readonly string _firebaseProjectId;
    private readonly string _firebaseStorageBucket;

    public FirebasePictureLinkService(HttpClient httpClient)
    {
        _httpClient = httpClient;
        _firebaseProjectId = "YOUR_FIREBASE_PROJECT_ID"; // Replace with actual project ID
        _firebaseStorageBucket = "YOUR_FIREBASE_STORAGE_BUCKET"; // Replace with actual storage bucket
    }

    public async Task<List<PictureLink>> GetAllPictureLinksAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync(
                $"https://firestore.googleapis.com/v1/projects/{_firebaseProjectId}/databases/(default)/documents/pictureLinks");

            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                var firestoreResponse = JsonSerializer.Deserialize<Dictionary<string, object>>(content);

                if (firestoreResponse != null && firestoreResponse.ContainsKey("documents"))
                {
                    var documents = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(
                        firestoreResponse["documents"].ToString()!);

                    var pictureLinks = new List<PictureLink>();
                    foreach (var doc in documents!)
                    {
                        var pictureLink = ParseFirestoreDocument(doc);
                        if (pictureLink != null)
                            pictureLinks.Add(pictureLink);
                    }

                    return pictureLinks.Where(p => p.IsActive).OrderByDescending(p => p.CreatedAt).ToList();
                }
            }

            return new List<PictureLink>();
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Get picture links error: {ex.Message}");
            return new List<PictureLink>();
        }
    }

    public async Task<PictureLink?> GetPictureLinkAsync(string id)
    {
        try
        {
            var response = await _httpClient.GetAsync(
                $"https://firestore.googleapis.com/v1/projects/{_firebaseProjectId}/databases/(default)/documents/pictureLinks/{id}");

            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                var document = JsonSerializer.Deserialize<Dictionary<string, object>>(content);

                return ParseFirestoreDocument(document!);
            }

            return null;
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Get picture link error: {ex.Message}");
            return null;
        }
    }

    public async Task<bool> CreatePictureLinkAsync(PictureLink pictureLink)
    {
        try
        {
            var firestoreDoc = ConvertToFirestoreDocument(pictureLink);
            var json = JsonSerializer.Serialize(firestoreDoc);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(
                $"https://firestore.googleapis.com/v1/projects/{_firebaseProjectId}/databases/(default)/documents/pictureLinks?documentId={pictureLink.Id}",
                content);

            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Create picture link error: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> UpdatePictureLinkAsync(PictureLink pictureLink)
    {
        try
        {
            pictureLink.UpdatedAt = DateTime.UtcNow;
            var firestoreDoc = ConvertToFirestoreDocument(pictureLink);
            var json = JsonSerializer.Serialize(firestoreDoc);
            var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");

            var response = await _httpClient.PatchAsync(
                $"https://firestore.googleapis.com/v1/projects/{_firebaseProjectId}/databases/(default)/documents/pictureLinks/{pictureLink.Id}",
                content);

            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Update picture link error: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> DeletePictureLinkAsync(string id)
    {
        try
        {
            var response = await _httpClient.DeleteAsync(
                $"https://firestore.googleapis.com/v1/projects/{_firebaseProjectId}/databases/(default)/documents/pictureLinks/{id}");

            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Delete picture link error: {ex.Message}");
            return false;
        }
    }

    public async Task<string> UploadImageAsync(string localPath, string fileName)
    {
        try
        {
            // For now, return a placeholder URL
            // In a real implementation, you would upload to Firebase Storage
            var imageBytes = await File.ReadAllBytesAsync(localPath);
            
            // Simulate upload delay
            await Task.Delay(1000);
            
            // Return a placeholder URL - replace with actual Firebase Storage upload
            return $"https://firebasestorage.googleapis.com/v0/b/{_firebaseStorageBucket}/o/{fileName}?alt=media";
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Upload image error: {ex.Message}");
            return string.Empty;
        }
    }

    public async Task<byte[]?> DownloadImageAsync(string imageUrl)
    {
        try
        {
            var response = await _httpClient.GetAsync(imageUrl);
            if (response.IsSuccessStatusCode)
            {
                return await response.Content.ReadAsByteArrayAsync();
            }
            return null;
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Download image error: {ex.Message}");
            return null;
        }
    }

    private PictureLink? ParseFirestoreDocument(Dictionary<string, object> document)
    {
        try
        {
            if (!document.ContainsKey("fields")) return null;

            var fields = JsonSerializer.Deserialize<Dictionary<string, Dictionary<string, object>>>(
                document["fields"].ToString()!);

            if (fields == null) return null;

            return new PictureLink
            {
                Id = GetStringValue(fields, "id"),
                Title = GetStringValue(fields, "title"),
                Description = GetStringValue(fields, "description"),
                ImageUrl = GetStringValue(fields, "imageUrl"),
                LocalImagePath = GetStringValue(fields, "localImagePath"),
                ButtonLabel = GetStringValue(fields, "buttonLabel"),
                TargetUrl = GetStringValue(fields, "targetUrl"),
                CreatedAt = GetDateTimeValue(fields, "createdAt"),
                UpdatedAt = GetDateTimeValue(fields, "updatedAt"),
                IsActive = GetBoolValue(fields, "isActive"),
                CreatedBy = GetStringValue(fields, "createdBy")
            };
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Parse document error: {ex.Message}");
            return null;
        }
    }

    private Dictionary<string, object> ConvertToFirestoreDocument(PictureLink pictureLink)
    {
        return new Dictionary<string, object>
        {
            ["fields"] = new Dictionary<string, object>
            {
                ["id"] = new { stringValue = pictureLink.Id },
                ["title"] = new { stringValue = pictureLink.Title },
                ["description"] = new { stringValue = pictureLink.Description },
                ["imageUrl"] = new { stringValue = pictureLink.ImageUrl },
                ["localImagePath"] = new { stringValue = pictureLink.LocalImagePath },
                ["buttonLabel"] = new { stringValue = pictureLink.ButtonLabel },
                ["targetUrl"] = new { stringValue = pictureLink.TargetUrl },
                ["createdAt"] = new { timestampValue = pictureLink.CreatedAt.ToString("yyyy-MM-ddTHH:mm:ss.fffZ") },
                ["updatedAt"] = new { timestampValue = pictureLink.UpdatedAt.ToString("yyyy-MM-ddTHH:mm:ss.fffZ") },
                ["isActive"] = new { booleanValue = pictureLink.IsActive },
                ["createdBy"] = new { stringValue = pictureLink.CreatedBy }
            }
        };
    }

    private string GetStringValue(Dictionary<string, Dictionary<string, object>> fields, string fieldName)
    {
        if (fields.ContainsKey(fieldName) && fields[fieldName].ContainsKey("stringValue"))
            return fields[fieldName]["stringValue"].ToString() ?? string.Empty;
        return string.Empty;
    }

    private DateTime GetDateTimeValue(Dictionary<string, Dictionary<string, object>> fields, string fieldName)
    {
        if (fields.ContainsKey(fieldName) && fields[fieldName].ContainsKey("timestampValue"))
        {
            if (DateTime.TryParse(fields[fieldName]["timestampValue"].ToString(), out DateTime result))
                return result;
        }
        return DateTime.UtcNow;
    }

    private bool GetBoolValue(Dictionary<string, Dictionary<string, object>> fields, string fieldName)
    {
        if (fields.ContainsKey(fieldName) && fields[fieldName].ContainsKey("booleanValue"))
        {
            if (bool.TryParse(fields[fieldName]["booleanValue"].ToString(), out bool result))
                return result;
        }
        return true;
    }
}