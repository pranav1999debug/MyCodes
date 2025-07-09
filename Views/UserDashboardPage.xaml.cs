using PictureLinkViewer.ViewModels;

namespace PictureLinkViewer.Views;

public partial class UserDashboardPage : ContentPage
{
    private readonly UserDashboardViewModel _viewModel;

    public UserDashboardPage(UserDashboardViewModel viewModel)
    {
        InitializeComponent();
        _viewModel = viewModel;
        BindingContext = _viewModel;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        await _viewModel.InitializeAsync();
    }
}