using Example.Shared.InquiryArchive;

namespace Example.Users.ReadModel;

// Archive interface for managing User data in the Query Model.
public interface IUserArchive : IArchive<UserData, string>
{
}

// TODO: Replace with real read-side data model.
public sealed record UserData(string Id, string Name, string Email);
