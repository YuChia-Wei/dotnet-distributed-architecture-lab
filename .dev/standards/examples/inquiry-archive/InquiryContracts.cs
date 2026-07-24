using System.Collections.Generic;

namespace Example.Shared.InquiryArchive;

// Framework-neutral placeholders; replace them with target-owned contracts.
public interface IInquiry<in TInput, out TOutput>
{
    TOutput Query(TInput input);
}

public interface IArchive<TEntity, in TId>
{
    TEntity? FindById(TId id);
    void Save(TEntity entity);
}
