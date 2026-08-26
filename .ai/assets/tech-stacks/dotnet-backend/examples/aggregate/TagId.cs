namespace Example.Tags.Domain;

public sealed record TagId
{
    public string Value { get; }

    public TagId(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ArgumentException("TagId value cannot be null or empty.", nameof(value));
        }
        Value = value;
    }

    public static TagId Create() => new(Guid.NewGuid().ToString());
    public static TagId ValueOf(string value) => new(value);
    public static TagId ValueOf(Guid value) => new(value.ToString());
    public override string ToString() => Value;
}
