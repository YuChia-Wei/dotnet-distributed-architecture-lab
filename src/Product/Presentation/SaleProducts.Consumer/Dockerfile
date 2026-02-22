FROM mcr.microsoft.com/dotnet/runtime:10.0 AS base
USER $APP_UID
WORKDIR /app

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/Product/Presentation/SaleProducts.Consumer/SaleProducts.Consumer.csproj", "Product/Presentation/SaleProducts.Consumer/"]
COPY ["src/Product/DomainCore/SaleProducts.Infrastructure/SaleProducts.Infrastructure.csproj", "Product/DomainCore/SaleProducts.Infrastructure/"]
COPY ["src/Product/DomainCore/SaleProducts.Applications/SaleProducts.Applications.csproj", "Product/DomainCore/SaleProducts.Applications/"]
COPY ["src/Product/DomainCore/SaleProducts.Domains/SaleProducts.Domains.csproj", "Product/DomainCore/SaleProducts.Domains/"]
COPY ["src/BuildingBlocks/Lab.BuildingBlocks.Application/Lab.BuildingBlocks.Application.csproj", "BuildingBlocks/Lab.BuildingBlocks.Application/"]
COPY ["src/BuildingBlocks/Lab.BuildingBlocks.Domains/Lab.BuildingBlocks.Domains.csproj", "BuildingBlocks/Lab.BuildingBlocks.Domains/"]
COPY ["src/BuildingBlocks/Lab.BuildingBlocks.Integrations/Lab.BuildingBlocks.Integrations.csproj", "BuildingBlocks/Lab.BuildingBlocks.Integrations/"]
COPY ["src/BC-Contracts/Lab.BoundedContextContracts.Orders/Lab.BoundedContextContracts.Orders.csproj", "BC-Contracts/Lab.BoundedContextContracts.Orders/"]
COPY ["src/BC-Contracts/Lab.BoundedContextContracts.Products/Lab.BoundedContextContracts.Products.csproj", "BC-Contracts/Lab.BoundedContextContracts.Products/"]
RUN dotnet restore "Product/Presentation/SaleProducts.Consumer/SaleProducts.Consumer.csproj"
COPY . .
WORKDIR "Product/Presentation/SaleProducts.Consumer"
RUN dotnet build "./SaleProducts.Consumer.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./SaleProducts.Consumer.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "SaleProducts.Consumer.dll"]
