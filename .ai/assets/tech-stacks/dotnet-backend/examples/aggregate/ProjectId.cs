namespace Example.Plans.Domain;

public sealed record ProjectId
{
    public string Value { get; }

    public ProjectId(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ArgumentException("ProjectId value cannot be null or empty.", nameof(value));
        }
        Value = value;
    }

    public static ProjectId Create() => new(Guid.NewGuid().ToString());
    public static ProjectId ValueOf(string value) => new(value);
    public override string ToString() => Value;
}
