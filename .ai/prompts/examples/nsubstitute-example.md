# NSubstitute Example

```csharp
var repo = Substitute.For<IRepository<Product, ProductId>>();
repo.FindById(Arg.Any<ProductId>()).Returns(product);
```
