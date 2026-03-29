# EZDDD Framework Reference (.NET)

## 重要：ezDDD/ezSpec 概念必須保留

目前 .NET 尚無對應 ezDDD/ezSpec 套件。請保留所有概念與規範，並以 TODO 標記待實作。

## 核心概念 (TODO: .NET package)
- AggregateRoot / Entity / ValueObject
- DomainEvent
- UseCase (Command/Query)
- Repository 介面（僅 findById / save / delete）
- MessageBus / MessageProducer
- Contract (Design by Contract)
- CqrsOutput

## Import / Namespace 參考 (概念對照)
- `DomainEvent` -> `IDomainEvent` (自定義介面)
- `AggregateRoot` -> `AggregateRoot` 基底類別 (自定義)
- `ValueObject` -> `ValueObject` 基底類別 (自定義或 record)
- `UseCase` -> Handler 介面 / WolverineFx Handler
- `Repository` -> `IRepository<TAggregate, TId>`
- `Contract` -> `Contract` (Design by Contract helper)

## 測試
- xUnit + BDDfy (Gherkin-style naming only)
- NSubstitute (Mock)

## TODO
- 建立 .NET 版 ezddd/ezspec 封裝套件
- 建立統一命名空間與基底類別
