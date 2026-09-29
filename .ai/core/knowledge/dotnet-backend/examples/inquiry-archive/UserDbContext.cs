using Microsoft.EntityFrameworkCore;

namespace Example.Users.ReadModel;

// TODO: Replace with actual read-side DbContext.
public sealed class UserDbContext : DbContext
{
    public DbSet<UserData> Users => Set<UserData>();
}
