namespace Example.Plans.Domain;

public sealed record ProjectName
{
    public string Value { get; }

    public ProjectName(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ArgumentException("ProjectName value cannot be null or empty.", nameof(value));
        }
        Value = value;
    }

    public static ProjectName ValueOf(string value) => new(value);
    public override string ToString() => Value;
}
