# Picture Link Viewer - .NET MAUI App

A cross-platform mobile application built with .NET MAUI that allows admins to upload pictures with custom buttons and links, while users can view and interact with these picture-link combinations.

## 🎯 Features

### 👨‍💼 Admin Features
- **Secure Admin Login**: Firebase Authentication with admin role verification
- **Picture Upload**: Upload images with Firebase Storage integration
- **Link Management**: Create custom buttons with labels and target URLs
- **CRUD Operations**: Create, read, update, and delete picture links
- **Real-time Preview**: Preview images and links before publishing
- **User Management**: Role-based access control

### 👤 User Features  
- **User Registration & Login**: Firebase Authentication for secure access
- **Picture Gallery**: Beautiful card-based layout displaying all picture links
- **Interactive Buttons**: Tap custom buttons to navigate to assigned URLs
- **Pull-to-Refresh**: Refresh content to see latest additions
- **Responsive Design**: Optimized for mobile devices
- **Offline Caching**: Cache images for offline viewing

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | .NET MAUI 8.0 |
| **UI Pattern** | MVVM with Community Toolkit |
| **Authentication** | Firebase Authentication |
| **Database** | Firebase Firestore |
| **File Storage** | Firebase Storage |
| **Local Database** | SQLite (for offline support) |
| **HTTP Client** | Refit for API calls |
| **Dependency Injection** | Microsoft.Extensions.DependencyInjection |

## 📋 Prerequisites

- **.NET 8.0 SDK** or later
- **Visual Studio 2022** or **Visual Studio Code** with C# extension
- **Android SDK** (for Android deployment)
- **Xcode** (for iOS deployment - macOS only)
- **Firebase Project** with Authentication, Firestore, and Storage enabled

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd PictureLinkViewer
```

### 2. Firebase Configuration

#### Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Authentication, Firestore Database, and Storage

#### Configure Authentication
1. In Firebase Console → Authentication → Sign-in method
2. Enable Email/Password authentication
3. Add admin emails to the `IsAdminEmail` method in `FirebaseAuthenticationService.cs`

#### Get Firebase Credentials
1. Go to Project Settings → General → Your apps
2. Add Android/iOS app if needed
3. Copy your Firebase configuration:
   - **Web API Key** (for Authentication)
   - **Project ID** (for Firestore)
   - **Storage Bucket** (for Storage)

### 3. Configure the App

Update the following files with your Firebase credentials:

**FirebaseAuthenticationService.cs**:
```csharp
_firebaseApiKey = "YOUR_FIREBASE_API_KEY";
```

**FirebasePictureLinkService.cs**:
```csharp
_firebaseProjectId = "YOUR_FIREBASE_PROJECT_ID";
_firebaseStorageBucket = "YOUR_FIREBASE_STORAGE_BUCKET";
```

### 4. Build and Run

#### For Development
```bash
dotnet build
dotnet run --framework net8.0-android
```

#### For Android Release
```bash
dotnet publish -f net8.0-android -c Release
```

#### For iOS (macOS only)
```bash
dotnet build -f net8.0-ios
```

## 📱 App Structure

```
PictureLinkViewer/
├── Models/                 # Data models
│   ├── User.cs
│   └── PictureLink.cs
├── Services/               # Business logic services
│   ├── IAuthenticationService.cs
│   ├── FirebaseAuthenticationService.cs
│   ├── IPictureLinkService.cs
│   └── FirebasePictureLinkService.cs
├── ViewModels/             # MVVM ViewModels
│   ├── BaseViewModel.cs
│   ├── LoginSelectionViewModel.cs
│   ├── AdminLoginViewModel.cs
│   ├── UserLoginViewModel.cs
│   ├── AdminDashboardViewModel.cs
│   └── UserDashboardViewModel.cs
├── Views/                  # UI Pages
│   ├── LoginSelectionPage.xaml
│   ├── AdminLoginPage.xaml
│   ├── UserLoginPage.xaml
│   ├── AdminDashboardPage.xaml
│   └── UserDashboardPage.xaml
├── Converters/             # XAML Value Converters
├── Resources/              # App resources
│   ├── Styles/
│   ├── Images/
│   └── Fonts/
└── Platforms/              # Platform-specific code
```

## 🔐 Default Admin Credentials

For testing, add your email to the admin list in `FirebaseAuthenticationService.cs`:

```csharp
private bool IsAdminEmail(string email)
{
    var adminEmails = new[] { "admin@picturelink.com", "your-email@example.com" };
    return adminEmails.Contains(email.ToLowerInvariant());
}
```

## 🎨 UI Features

- **Modern Design**: Clean, card-based interface with smooth animations
- **Dark/Light Theme**: Automatic theme support based on system preferences
- **Responsive Layout**: Optimized for different screen sizes
- **Intuitive Navigation**: Shell-based navigation with smooth transitions
- **Loading States**: Activity indicators and progress feedback
- **Error Handling**: User-friendly error messages and retry options

## 🔄 Data Flow

1. **Admin Workflow**:
   - Login with admin credentials
   - Upload image and configure button/link
   - Save to Firebase (Firestore + Storage)
   - Content becomes available to all users

2. **User Workflow**:
   - Register/Login with user credentials
   - Browse picture links in a scrollable feed
   - Tap buttons to navigate to external links
   - Pull to refresh for new content

## 🧪 Testing

### Test Admin Account
- Email: `admin@picturelink.com`
- Password: `admin123`

### Test User Account
- Register with any email/password combination

## 📦 NuGet Packages Used

- Microsoft.Maui.Controls
- CommunityToolkit.Mvvm
- Microsoft.Extensions.DependencyInjection
- SQLite-net-pcl
- Refit
- Plugin.Firebase.Storage
- Plugin.Firebase.Auth
- Plugin.Firebase.Firestore

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Build Errors**: Ensure .NET 8.0 SDK is installed and MAUI workload is available
2. **Firebase Connection**: Verify API keys and project configuration
3. **Android Build**: Check Android SDK and emulator setup
4. **iOS Build**: Requires macOS with Xcode installed

### Support

For issues and questions:
- Check the [Issues](../../issues) section
- Review Firebase documentation
- Consult .NET MAUI documentation

---

**Built with ❤️ using .NET MAUI and Firebase**