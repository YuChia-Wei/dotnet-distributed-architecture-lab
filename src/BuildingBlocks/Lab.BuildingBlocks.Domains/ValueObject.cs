namespace Lab.BuildingBlocks.Domains;

/// <summary>
/// 值物件 (Value Object) 介面
/// 值物件是用來描述領域內某個事物特徵的不可變物件
/// 它們沒有身份識別，而是透過其屬性值來判斷等同性
/// 實作此介面的類型必須：
/// 1. 確保不可變性 (Immutability)
/// 2. 實作適當的等同性比較 (通常使用 C# record 即可)
/// 3. 不應包含任何領域實體參考，只引用其他值物件或基本型別
/// </summary>
public interface IValueObject
{
    // 標記介面，無方法定義
    // 主要用於識別值物件及啟用靜態程式碼分析
}

public abstract class ValueObject : IValueObject
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