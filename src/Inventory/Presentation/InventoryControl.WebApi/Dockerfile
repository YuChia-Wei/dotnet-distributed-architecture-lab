FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
USER $APP_UID
WORKDIR /app
EXPOSE 8080
EXPOSE 8081

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/Inventory/Presentation/InventoryControl.WebApi/InventoryControl.WebApi.csproj", "Inventory/Presentation/InventoryControl.WebApi/"]
COPY ["src/Inventory/DomainCore/InventoryControl.Infrastructure/InventoryControl.Infrastructure.csproj", "Inventory/DomainCore/InventoryControl.Infrastructure/"]
COPY ["src/Inventory/DomainCore/InventoryControl.Applications/InventoryControl.Applications.csproj", "Inventory/DomainCore/InventoryControl.Applications/"]
COPY ["src/Inventory/DomainCore/InventoryControl.Domains/InventoryControl.Domains.csproj", "Inventory/DomainCore/InventoryControl.Domains/"]
COPY ["src/BuildingBlocks/Lab.BuildingBlocks.Integrations/Lab.BuildingBlocks.Integrations.csproj", "BuildingBlocks/Lab.BuildingBlocks.Integrations/"]
COPY ["src/BC-Contracts/Lab.BoundedContextContracts.Inventorys/Lab.BoundedContextContracts.Inventorys.csproj", "BC-Contracts/Lab.BoundedContextContracts.Inventorys/"]
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
