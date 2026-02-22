using System.Collections.Generic;

namespace Example.Shared.InquiryArchive;

// TODO: Replace these placeholders with ezDDD .NET ports.
public interface IInquiry<in TInput, out TOutput>
{
    TOutput Query(TInput input);
}

public interface IArchive<TEntity, in TId>
{
    TEntity? FindById(TId id);
    void Save(TEntity entity);
    void Delete(TEntity entity);
}
