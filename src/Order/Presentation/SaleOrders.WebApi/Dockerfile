FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
USER $APP_UID
WORKDIR /app
EXPOSE 8080
EXPOSE 8081

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/Order/Presentation/SaleOrders.WebApi/SaleOrders.WebApi.csproj", "Order/Presentation/SaleOrders.WebApi/"]
COPY ["src/Order/DomainCore/SaleOrders.Infrastructure/SaleOrders.Infrastructure.csproj", "Order/DomainCore/SaleOrders.Infrastructure/"]
COPY ["src/Order/DomainCore/SaleOrders.Applications/SaleOrders.Applications.csproj", "Order/DomainCore/SaleOrders.Applications/"]
COPY ["src/BuildingBlocks/Lab.BuildingBlocks.Integrations/Lab.BuildingBlocks.Integrations.csproj", "BuildingBlocks/Lab.BuildingBlocks.Integrations/"]
COPY ["src/Order/DomainCore/SaleOrders.Domains/SaleOrders.Domains.csproj", "Order/DomainCore/SaleOrders.Domains/"]
COPY ["src/BC-Contracts/Lab.BoundedContextContracts.Orders/Lab.BoundedContextContracts.Orders.csproj", "BC-Contracts/Lab.BoundedContextContracts.Orders/"]
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
