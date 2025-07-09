using System.ComponentModel.DataAnnotations;

namespace PictureLinkViewer.Models;

public class PictureLink
{
    [Key]
    public string Id { get; set; } = Guid.NewGuid().ToString();
    
    public string Title { get; set; } = string.Empty;
    
    public string Description { get; set; } = string.Empty;
    
    public string ImageUrl { get; set; } = string.Empty;
    
    public string LocalImagePath { get; set; } = string.Empty;
    
    public string ButtonLabel { get; set; } = string.Empty;
    
    public string TargetUrl { get; set; } = string.Empty;
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    
    public bool IsActive { get; set; } = true;
    
    public string CreatedBy { get; set; } = string.Empty;
}