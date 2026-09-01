FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
USER $APP_UID
WORKDIR /app
EXPOSE 8080
EXPOSE 8443

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["Order/Presentation/SaleOrders.WebApi/SaleOrders.WebApi.csproj", "Order/Presentation/SaleOrders.WebApi/"]
COPY ["Order/DomainCore/SaleOrders.Infrastructure/SaleOrders.Infrastructure.csproj", "Order/DomainCore/SaleOrders.Infrastructure/"]
COPY ["Order/DomainCore/SaleOrders.Applications/SaleOrders.Applications.csproj", "Order/DomainCore/SaleOrders.Applications/"]
COPY ["Order/DomainCore/SaleOrders.Domains/SaleOrders.Domains.csproj", "Order/DomainCore/SaleOrders.Domains/"]
COPY ["BuildingBlocks/Lab.BuildingBlocks.Application/Lab.BuildingBlocks.Application.csproj", "BuildingBlocks/Lab.BuildingBlocks.Application/"]
COPY ["BuildingBlocks/Lab.BuildingBlocks.Domains/Lab.BuildingBlocks.Domains.csproj", "BuildingBlocks/Lab.BuildingBlocks.Domains/"]
COPY ["BuildingBlocks/Lab.BuildingBlocks.Integrations/Lab.BuildingBlocks.Integrations.csproj", "BuildingBlocks/Lab.BuildingBlocks.Integrations/"]
COPY ["BC-Contracts/Lab.BoundedContextContracts.Orders/Lab.BoundedContextContracts.Orders.csproj", "BC-Contracts/Lab.BoundedContextContracts.Orders/"]
COPY ["BC-Contracts/Lab.BoundedContextContracts.Inventory/Lab.BoundedContextContracts.Inventory.csproj", "BC-Contracts/Lab.BoundedContextContracts.Inventory/"]
RUN dotnet restore "Order/Presentation/SaleOrders.WebApi/SaleOrders.WebApi.csproj"
COPY . .
WORKDIR "Order/Presentation/SaleOrders.WebApi"
RUN dotnet build "./SaleOrders.WebApi.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./SaleOrders.WebApi.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "SaleOrders.WebApi.dll"]
