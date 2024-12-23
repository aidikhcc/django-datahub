using Microsoft.Identity.Web;
using Microsoft.Identity.Web.UI;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;

var builder = WebApplication.CreateBuilder(args);

// Add authentication services
builder.Services.AddAuthentication(OpenIdConnectDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApp(builder.Configuration.GetSection("AzureAd"));

builder.Services.AddAuthorization(options =>
{
    options.FallbackPolicy = options.DefaultPolicy;
});

// Add controllers with views and Razor pages if you're using them
builder.Services.AddControllersWithViews()
    .AddMicrosoftIdentityUI();

// Existing code...

var app = builder.Build();

// Existing middleware...
app.UseAuthentication();
app.UseAuthorization();
// Other middleware...

app.Run(); 