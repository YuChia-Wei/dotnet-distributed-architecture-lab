namespace Example.Plans.Domain;

public sealed record PlanId
{
    public string Value { get; }

    public PlanId(string value)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ArgumentException("PlanId value cannot be null or empty.", nameof(value));
        }
        Value = value;
    }

    public static PlanId Create() => new(Guid.NewGuid().ToString());
    public static PlanId ValueOf(string value) => new(value);
    public override string ToString() => Value;
}
