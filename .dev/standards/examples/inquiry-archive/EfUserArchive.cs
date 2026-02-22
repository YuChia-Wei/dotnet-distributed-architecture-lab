using System;
using Example.Shared.InquiryArchive;
using Microsoft.EntityFrameworkCore;

namespace Example.Users.ReadModel;

public sealed class EfUserArchive : IUserArchive
{
    private readonly UserDbContext _db;

    public EfUserArchive(UserDbContext db)
    {
        _db = db ?? throw new ArgumentNullException(nameof(db));
    }

    public UserData? FindById(string id)
    {
        return _db.Users.Find(id);
    }

    public void Save(UserData entity)
    {
        _db.Users.Update(entity);
        _db.SaveChanges();
    }

    public void Delete(UserData entity)
    {
        _db.Users.Remove(entity);
        _db.SaveChanges();
    }
}

// TODO: Replace with actual read-side DbContext.
// UserDbContext lives in UserDbContext.cs
