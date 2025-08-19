# Project Development Guide & AI Assistant Prompt for MQArchLab

## 1. Overview

This document provides development guidelines for the `dotnet-mq-arch-lab` project to ensure code consistency, quality, and adherence to the established architecture. All interactions with and outputs from the AI assistant must strictly follow the rules defined herein.

## 2. Architectural Principles

The software architecture must adhere to the following core principles:

- **Clean Architecture (CA):** Enforce separation of concerns and dependency rules.
- **Domain-Driven Design (DDD):** Focus on the core domain and domain logic.
- **Command Query Responsibility Segregation (CQRS):** Separate read and write operations.

## 3. Core Technologies

- **Main Framework:** .NET 9
- **Primary Language:** C#
- **Containerization:** Docker

## 3.1 Key Libraries/Frameworks

- **Messaging/Command/Query Handling:** WolverineFx (replaces MediatR)

## 3.2 Data Storage

- **Database:** PostgreSQL

## 3.3 Message Broker

- **Message Queue:** RabbitMQ or Kafka

## 4. Project Structure

The project follows a strict, layered directory structure based on Clean Architecture, organized by business context (e.g., `Order`, `Product`). **All source code projects must be placed under the `src` directory.**

### Naming Conventions:

- **Pluralization:** Project names for layers like `Applications`, `Repositories`, and `Domains`, as well as folders within projects, should be in **plural form** whenever appropriate.
- **Business Context Folder:** Each business context should have its own top-level folder within `src` (e.g., `src/Order`, `src/Product`).

### Example Structure for a Service (e.g., "SaleOrders"):

The following shows the physical file structure on the disk, which is grouped by business context (`Order`) and then by architectural layer (`DomainCore`, `Presentation`).

```
dotnet-mq-arch-lab/
├── src/
│   └── Order/
│       ├── DomainCore/
│       │   ├── SaleOrders.Applications/
│       │   ├── SaleOrders.Domains/
│       │   └── SaleOrders.Infrastructure/
│       └── Presentation/
│           ├── SaleOrders.Consumer/
│           └── SaleOrders.WebApi/
│               └── Dockerfile
├── docker-compose/
│   └── docker-compose.yml
├── .gitignore
└── MQArchLab.slnx
```

In the Visual Studio Solution (`.slnx`), these projects are organized into solution folders that mirror the physical directory structure for clarity:

```
/Order/
├── DomainCore/
│   ├── SaleOrders.Applications
│   ├── SaleOrders.Domains
│   └── SaleOrders.Infrastructure
└── Presentation/
    ├── SaleOrders.Consumer
    └── SaleOrders.WebApi
```

### Rules:

1.  **Source Code Location:** All .NET projects **must** be created in a separate folder under `src/<BusinessContext>/<LayerGroup>/`.
2.  **Docker Compose:** The `docker-compose` directory is exclusively for local development and testing configurations.
3.  **Solution File:** The root `MQArchLab.slnx` is the solution file. New projects must be added to it, preferably within solution folders that match the directory structure.

## 5. Dockerfile Requirements

**Every** executable project (e.g., an API or a background service) located in the `src` directory **must** include a `Dockerfile`.

### Dockerfile Template:

Please use the following multi-stage build template to ensure optimized and secure images.

```Dockerfile
# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copy csproj and restore as distinct layers to leverage Docker cache
COPY ["src/Order/Presentation/SaleOrders.WebApi/SaleOrders.WebApi.csproj", "Order/Presentation/SaleOrders.WebApi/"]
# Adjust the path above for other projects, e.g., "src/Product/Presentation/SaleProducts.WebApi/..."

RUN dotnet restore "Order/Presentation/SaleOrders.WebApi/SaleOrders.WebApi.csproj"

# Copy everything else and build
COPY . .
WORKDIR "/src/Order/Presentation/SaleOrders.WebApi"
RUN dotnet build "SaleOrders.WebApi.csproj" -c Release -o /app/build

# Stage 2: Publish
FROM build AS publish
RUN dotnet publish "SaleOrders.WebApi.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Stage 3: Final
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "SaleOrders.WebApi.dll"]
```

## 6. Development Workflow

### Creating a New Service

When a new service (e.g., "Invoices") is required, follow these steps, creating each project layer as needed:

1.  **Confirm Service Name and Project Layers:** Ask the user for the core service name (e.g., `Invoices`), the business context folder (e.g., `Invoice`), and which project layers are needed (e.g., `WebApi`, `Applications`).

2.  **Create Project Directories and Files:** For each layer, create the project in the correct location. The project name should be `<ServiceName>.<LayerName>` (e.g., `Invoices.WebApi`).
    ```shell
    # Example for the WebApi layer for a new "Invoices" service
    dotnet new webapi -n Invoices.WebApi -o src/Invoice/Presentation/Invoices.WebApi
    ```

3.  **Add to Solution with Solution Folders:** Add each new project to the solution, specifying the correct solution folder that mirrors the directory structure.
    ```shell
    # Example for adding the WebApi project to the "Presentation" folder within a new "Invoice" folder
    dotnet sln add src/Invoice/Presentation/Invoices.WebApi/Invoices.WebApi.csproj --solution-folder "Invoice/Presentation"
    ```

4.  **Create Dockerfile:** For any executable project (like an API or Consumer), create a `Dockerfile` in its root directory (e.g., `src/Invoice/Invoices.Api/Dockerfile`) based on the template above.
5.  **Update Docker Compose (Optional):** If local integration testing is needed, add a new service entry for the project in `docker-compose/docker-compose.yml`.

## 7. Coding Conventions

- Follow the official Microsoft [C# Coding Conventions](https://docs.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions).
- Adhere to the settings defined in the `.editorconfig` file for all code and text files.
- **Dependency Injection:** For `Infrastructure` and `Applications` projects, DI registration should be encapsulated within the project using a dedicated extension method (e.g., `AddInfrastructureServices`).
- **API Design:** Web APIs must adhere to RESTful design principles.
- **API DTOs:** API input and output should use dedicated objects. Input objects are uniformly suffixed with "Request", and output objects are uniformly suffixed with "Response".
- **API Documentation:** All public API controllers must have an XML summary (`<summary>`) written in Traditional Chinese (Taiwan).
- **Naming:** Use plural form for layer-specific projects (`Applications`, `Repositories`) and internal folders.
- Prefer file-scoped namespaces.
- Use top-level statements where appropriate (e.g., in `Program.cs`).