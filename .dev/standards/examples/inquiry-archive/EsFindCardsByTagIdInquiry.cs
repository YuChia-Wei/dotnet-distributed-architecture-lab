using System.Collections.Generic;
using System.Linq;
using Example.Shared.InquiryArchive;
using Example.Tags.Domain;

namespace Example.Cards.ReadModel;

public sealed class EsFindCardsByTagIdInquiry : IFindCardsByTagIdInquiry
{
    private readonly IEventStore _eventStore;

    public EsFindCardsByTagIdInquiry(IEventStore eventStore)
    {
        _eventStore = eventStore;
    }

    public IReadOnlyList<string> Query(TagId tagId)
    {
        var tagAssignedStream = _eventStore.GetEventsByType(CardEvents.TypeMapper.TagAssignedType);
        if (tagAssignedStream == null || tagAssignedStream.DomainEventDatas.Count == 0)
        {
            return new List<string>();
        }

        var tagAssigneds = DomainEventMapper.ToDomain(tagAssignedStream.DomainEventDatas)
            .Cast<CardEvents.TagAssigned>()
            .ToList();

        var cardIds = tagAssigneds
            .Where(evt => evt.TagId.Equals(tagId))
            .Select(evt => evt.CardId)
            .Distinct()
            .ToList();

        var result = new List<string>();
        foreach (var cardId in cardIds)
        {
            var cardData = _eventStore.GetEventsByStreamName(Card.GetStreamName(Card.Category, cardId.Value));
            if (cardData == null)
            {
                continue;
            }

            var domainEvents = DomainEventMapper.ToDomain(cardData.DomainEventDatas).Cast<CardEvents.ICardEvent>().ToList();
            var card = new Card(domainEvents);
            if (!card.IsDeleted && card.TagIds.Contains(tagId))
            {
                card.Version = cardData.Version;
                result.Add(cardId.Value);
            }
        }

        return result;
    }
}

// TODO: Replace placeholders below with ezDDD .NET port types.
public interface IEventStore
{
    EventStreamData? GetEventsByType(string eventType);
    EventStreamData? GetEventsByStreamName(string streamName);
}

public sealed class EventStreamData
{
    public List<DomainEventData> DomainEventDatas { get; } = new();
    public int Version { get; set; }
}

public sealed class DomainEventData { }

public static class DomainEventMapper
{
    public static IEnumerable<object> ToDomain(IEnumerable<DomainEventData> datas) => new List<object>();
}

public sealed class Card
{
    public const string Category = "Card";
    public bool IsDeleted { get; private set; }
    public IReadOnlyCollection<TagId> TagIds { get; } = new List<TagId>();
    public int Version { get; set; }

    public Card(IEnumerable<CardEvents.ICardEvent> events)
    {
    }

    public static string GetStreamName(string category, string id) => $"{category}-{id}";
}

public static class CardEvents
{
    public interface ICardEvent { }

    public sealed record TagAssigned(TagId TagId, CardId CardId) : ICardEvent;

    public static class TypeMapper
    {
        public const string TagAssignedType = "CardEvents.TagAssigned";
    }
}

public sealed record CardId(string Value);
