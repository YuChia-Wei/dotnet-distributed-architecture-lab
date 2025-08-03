namespace Lab.SharedKernel;

public abstract class ValueObject
{
    public override bool Equals(object? obj)
    {
        if (obj == null || obj.GetType() != this.GetType())
        {
            return false;
        }

        var other = (ValueObject)obj;
        return this.GetEqualityComponents().SequenceEqual(other.GetEqualityComponents());
    }

    public abstract IEnumerable<object> GetEqualityComponents();

    public override int GetHashCode()
    {
        return this.GetEqualityComponents()
                   .Select(x => x.GetHashCode())
                   .Aggregate((x, y) => x ^ y);
    }

    public static bool operator ==(ValueObject a, ValueObject b)
    {
        if (ReferenceEquals(a, null) && ReferenceEquals(b, null))
        {
            return true;
        }

        if (ReferenceEquals(a, null) || ReferenceEquals(b, null))
        {
            return false;
        }

        return a.Equals(b);
    }

    public static bool operator !=(ValueObject a, ValueObject b)
    {
        return !(a == b);
    }
}