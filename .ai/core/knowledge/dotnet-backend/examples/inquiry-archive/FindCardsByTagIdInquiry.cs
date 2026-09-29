using System.Collections.Generic;
using Example.Shared.InquiryArchive;
using Example.Tags.Domain;

namespace Example.Cards.ReadModel;

public interface IFindCardsByTagIdInquiry : IInquiry<TagId, IReadOnlyList<string>>
{
}
