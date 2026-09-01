FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
USER $APP_UID
WORKDIR /app
EXPOSE 8080
EXPOSE 8443

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["Inventory/Presentation/InventoryControl.WebApi/InventoryControl.WebApi.csproj", "Inventory/Presentation/InventoryControl.WebApi/"]
COPY ["Inventory/DomainCore/InventoryControl.Infrastructure/InventoryControl.Infrastructure.csproj", "Inventory/DomainCore/InventoryControl.Infrastructure/"]
COPY ["Inventory/DomainCore/InventoryControl.Applications/InventoryControl.Applications.csproj", "Inventory/DomainCore/InventoryControl.Applications/"]
COPY ["Inventory/DomainCore/InventoryControl.Domains/InventoryControl.Domains.csproj", "Inventory/DomainCore/InventoryControl.Domains/"]
COPY ["BuildingBlocks/Lab.BuildingBlocks.Application/Lab.BuildingBlocks.Application.csproj", "BuildingBlocks/Lab.BuildingBlocks.Application/"]
COPY ["BuildingBlocks/Lab.BuildingBlocks.Domains/Lab.BuildingBlocks.Domains.csproj", "BuildingBlocks/Lab.BuildingBlocks.Domains/"]
COPY ["BuildingBlocks/Lab.BuildingBlocks.Integrations/Lab.BuildingBlocks.Integrations.csproj", "BuildingBlocks/Lab.BuildingBlocks.Integrations/"]
COPY ["BC-Contracts/Lab.BoundedContextContracts.Inventory/Lab.BoundedContextContracts.Inventory.csproj", "BC-Contracts/Lab.BoundedContextContracts.Inventory/"]
COPY ["BC-Contracts/Lab.BoundedContextContracts.Orders/Lab.BoundedContextContracts.Orders.csproj", "BC-Contracts/Lab.BoundedContextContracts.Orders/"]
RUN dotnet restore "Inventory/Presentation/InventoryControl.WebApi/InventoryControl.WebApi.csproj"
COPY . .
WORKDIR "Inventory/Presentation/InventoryControl.WebApi"
RUN dotnet build "./InventoryControl.WebApi.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./InventoryControl.WebApi.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "InventoryControl.WebApi.dll"]
