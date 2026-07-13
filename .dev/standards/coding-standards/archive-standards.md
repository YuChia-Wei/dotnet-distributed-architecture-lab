# Archive Coding Standards (.NET)

This document defines coding standards for the Archive Pattern, which handles database write requirements for Query Models.

---

## 📌 Overview

The Archive Pattern is used for soft deletion and historical data management and is dedicated to Query Model writes in a CQRS architecture.

- **Query Model writes**: An Archive handles database write requirements for a Query Model.
- **Distinction from Repository**: A Repository is limited to writing a single Aggregate in the Command Model.
- **Event-driven**: A Reactor invokes an Archive when it receives a Domain Event.

---

## 🏷️ Pattern Markers (for Automated Checks)

The following markers are used by automated code review scripts:

```yaml
# Archive rules (soft-delete support)
Pattern (required, any): IsDeleted|IsArchived|ArchivedAt
```

The marker verifies that the read model represents archive state. It is not a
method-naming rule. Physical deletion is governed through the restricted purge
capability described below, so a generic `HardDelete` text check would be both
too broad and too easy to evade.

---

## 📌 Core Concept

An **Archive** is a database write pattern dedicated to Query Models in a CQRS architecture:

- Its interface resembles a Write Model Repository, but an Archive handles database write requirements for a Query Model.
- A Repository is limited to writing a single Aggregate in the Command Model.
- It may write to one table or across multiple tables.
- A Reactor in the Handler layer invokes the Archive after receiving a Domain Event and writes the data to the database.

---

## 🔴 Mandatory Rules (MUST FOLLOW)

### 1. Archive Interface Design

#### Namespace

```csharp
// ✅ Correct: define the Archive interface in the Application layer
namespace YourProject.Application.Users.Archives;

// ❌ Incorrect: do not place it in the Infrastructure layer
namespace YourProject.Infrastructure.Persistence;  // Incorrect!
```

#### Interface Naming Rules

```csharp
// ✅ Correct: use the singular I[Entity]Archive naming pattern
public interface IUserArchive { }

// ❌ Incorrect: do not use other naming patterns
public interface IUserRepository { }  // Do not use Repository for a Read Model
public interface UserArchive { }      // Add the I prefix
public interface IUserDtoArchive { }  // Do not use DtoArchive
```

#### Interface Definition

```csharp
// ✅ Correct: define an Archive interface
public interface IUserArchive
{
    Task<UserData?> FindByIdAsync(string userId, CancellationToken ct = default);
    Task SaveAsync(UserData userData, CancellationToken ct = default);
}

// ❌ Incorrect: do not return a domain object
public interface IUserArchive
{
    Task<User?> FindByIdAsync(string userId);  // Incorrect! Return UserData instead
}

// ❌ Incorrect: do not return a DTO
public interface IUserArchive
{
    Task<UserDto?> FindByIdAsync(string userId);  // Incorrect! Return UserData instead
}
```

The general Archive port owns lookup and persistence only. Archive state belongs
to the read-side data model (`IsArchived`, `ArchivedAt`, and related audit
metadata) and is persisted through `SaveAsync`. Do not put `DeleteAsync` on this
port: that name hides whether the operation changes archive state or physically
deletes data.

When the application needs an explicit state transition, define a narrowly
named operation such as `ArchiveAsync` or `MarkArchivedAsync` on a use-case- or
capability-specific port. The operation must update archive metadata and retain
the record.

Physical read-model cleanup is a separate restricted capability. It must not be
added to `IUserArchive` or reused as an aggregate purge mechanism:

```csharp
// Application capability for controlled read-model cleanup only.
public interface IUserReadModelPurgePort
{
    Task PurgeAsync(string userId, CancellationToken ct = default);
}
```

Calling this port requires explicit authorization plus satisfied retention,
legal-hold, audit-evidence, and dependent-read-model cleanup gates. The adapter
must make those decisions observable; normal Reactor and CRUD flows must not
receive this capability.

---

### 2. Archive Implementation

#### Implementation Location

```csharp
// ✅ Correct: place the implementation in the Infrastructure layer
namespace YourProject.Infrastructure.Persistence.Archives;
```

#### EF Core Archive Implementation

```csharp
// ✅ Correct: EF Core implementation
namespace YourProject.Infrastructure.Persistence.Archives;

public class EfCoreUserArchive : IUserArchive
{
    private readonly ApplicationDbContext _context;

    public EfCoreUserArchive(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<UserData?> FindByIdAsync(string userId, CancellationToken ct = default)
    {
        ArgumentNullException.ThrowIfNull(userId);
        
        return await _context.Users
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == userId, ct);
    }

    public async Task SaveAsync(UserData userData, CancellationToken ct = default)
    {
        ArgumentNullException.ThrowIfNull(userData);
        
        var existing = await _context.Users
            .FirstOrDefaultAsync(x => x.Id == userData.Id, ct);
        
        if (existing is null)
        {
            await _context.Users.AddAsync(userData, ct);
        }
        else
        {
            _context.Entry(existing).CurrentValues.SetValues(userData);
        }
    }
}
```

To archive a record, construct or update `UserData` with its archive state and
metadata, then call `SaveAsync`. An EF Archive adapter must not call `Remove` as
part of normal archive behavior.

---

### 3. DI Registration

```csharp
// ✅ Correct: register in ServiceExtensions
public static class ArchiveServiceExtensions
{
    public static IServiceCollection AddArchives(this IServiceCollection services)
    {
        services.AddScoped<IUserArchive, EfCoreUserArchive>();
        // Other Archive registrations...
        
        return services;
    }
}
```

---

## 🎯 Usage Guide

### When to Use an Archive

- ✅ Query Model CRUD operations
- ✅ Reference-data synchronization across Bounded Contexts
- ✅ Event-driven Read Model writes
- ✅ Persisting soft-delete/archive state and audit metadata
- ❌ Write Model CRUD operations (use a Repository)
- ❌ Physical deletion through the general Archive port

### Difference from a Repository

```csharp
// Repository: persistence for a Write Model Aggregate
IAggregateRepository<Product, ProductId> repository;
await repository.FindByIdAsync(id);  // Returns a Product domain object
await repository.SaveAsync(product); // Persists a domain object

// Archive: persistence for Read Model Data
IUserArchive archive;
await archive.FindByIdAsync(userId);   // Returns UserData
await archive.SaveAsync(userData);     // Persists a Data object
```

---

## 🎯 Event-Driven Write Example

### A Reactor Uses an Archive

```csharp
// ✅ Correct: use WolverineFx to handle a Domain Event
public class UserCreatedReactor
{
    private readonly IUserArchive _archive;

    public UserCreatedReactor(IUserArchive archive)
    {
        _archive = archive;
    }

    public async Task Handle(UserCreated @event, CancellationToken ct)
    {
        var userData = new UserData
        {
            Id = @event.UserId.Value,
            Name = @event.Name,
            Email = @event.Email,
            CreatedAt = @event.OccurredOn
        };

        await _archive.SaveAsync(userData, ct);
    }
}
```

---

## 🔍 Checklist

### Archive Interface
- [ ] Defined in the `Application` layer.
- [ ] Uses the `I[Entity]Archive` naming pattern.
- [ ] Returns Data (a Persistence Object), not a domain object or DTO.
- [ ] The general port has lookup and save operations; archive state is represented by Data.
- [ ] Explicit archive operations use names such as `ArchiveAsync` or `MarkArchivedAsync`, never ambiguous `DeleteAsync`.
- [ ] Physical read-model purge, when required, uses a separate restricted capability-specific port.
- [ ] Supports `CancellationToken`.

### Archive Implementation
- [ ] Implemented in `Infrastructure.Persistence.Archives`.
- [ ] If the adapter uses EF Core, it follows EF Core tracking/materialization guidance.
- [ ] Uses `ArgumentNullException.ThrowIfNull`.
- [ ] Does not use EF `Remove` for normal archive behavior.
- [ ] Purge access is gated by authorization, retention, legal, audit, and dependent-cleanup policy.
- [ ] Registered through DI.

---

## 📂 Code Examples

For more complete examples, see:

| Example | Path |
|------|------|
| Inquiry + Archive examples | [../examples/inquiry-archive/](../examples/inquiry-archive/) |
| Usage guide | [../examples/inquiry-archive/USAGE-GUIDE.md](../examples/inquiry-archive/USAGE-GUIDE.md) |

---

## Related Documents

- [repository-standards.md](repository-standards.md)
- [projection-standards.md](projection-standards.md)
- [usecase-standards.md](usecase-standards.md)
