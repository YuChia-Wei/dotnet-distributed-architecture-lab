using System.Collections.Generic;
using System.Linq;
using Example.Shared.InquiryArchive;
using Example.Tags.Domain;
using Microsoft.EntityFrameworkCore;

namespace Example.Cards.ReadModel;

public sealed class EfFindCardsByTagIdInquiry : IFindCardsByTagIdInquiry
{
    private readonly CardReadDbContext _db;

    public EfFindCardsByTagIdInquiry(CardReadDbContext db)
    {
        _db = db;
    }

    public IReadOnlyList<string> Query(TagId tagId)
    {
        return _db.Cards
            .AsNoTracking()
            .Where(card => card.Tags.Any(tag => tag.TagId == tagId.Value))
            .Select(card => card.CardId)
            .ToList();
    }
}

// TODO: Replace these with real EF Core read models.
public sealed class CardReadDbContext : DbContext
{
    public DbSet<CardReadModel> Cards => Set<CardReadModel>();
}

public sealed class CardReadModel
{
    public string CardId { get; set; } = string.Empty;
    public List<CardTagReadModel> Tags { get; set; } = new();
}

public sealed class CardTagReadModel
{
    public string TagId { get; set; } = string.Empty;
}
