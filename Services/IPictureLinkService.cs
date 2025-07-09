using PictureLinkViewer.Models;

namespace PictureLinkViewer.Services;

public interface IPictureLinkService
{
    Task<List<PictureLink>> GetAllPictureLinksAsync();
    Task<PictureLink?> GetPictureLinkAsync(string id);
    Task<bool> CreatePictureLinkAsync(PictureLink pictureLink);
    Task<bool> UpdatePictureLinkAsync(PictureLink pictureLink);
    Task<bool> DeletePictureLinkAsync(string id);
    Task<string> UploadImageAsync(string localPath, string fileName);
    Task<byte[]?> DownloadImageAsync(string imageUrl);
}