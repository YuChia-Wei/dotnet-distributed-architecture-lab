namespace Example.Plans.Domain;

public sealed record TaskId
{
    public string Value { get; }

    public TaskId(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ArgumentException("TaskId value cannot be null or empty.", nameof(value));
        }
        Value = value;
    }

    public static TaskId Create() => new(Guid.NewGuid().ToString());
    public static TaskId ValueOf(string value) => new(value);
    public override string ToString() => Value;
}
