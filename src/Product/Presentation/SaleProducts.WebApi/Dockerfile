FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
USER $APP_UID
WORKDIR /app
EXPOSE 8080
EXPOSE 8081

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/Product/Presentation/SaleProducts.WebApi/SaleProducts.WebApi.csproj", "Product/Presentation/SaleProducts.WebApi/"]
COPY ["src/Product/DomainCore/SaleProducts.Infrastructure/SaleProducts.Infrastructure.csproj", "Product/DomainCore/SaleProducts.Infrastructure/"]
COPY ["src/Product/DomainCore/SaleProducts.Applications/SaleProducts.Applications.csproj", "Product/DomainCore/SaleProducts.Applications/"]
COPY ["src/Product/DomainCore/SaleProducts.Domains/SaleProducts.Domains.csproj", "Product/DomainCore/SaleProducts.Domains/"]
RUN dotnet restore "Product/Presentation/SaleProducts.WebApi/SaleProducts.WebApi.csproj"
COPY . .
WORKDIR "Product/Presentation/SaleProducts.WebApi"
RUN dotnet build "./SaleProducts.WebApi.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./SaleProducts.WebApi.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "SaleProducts.WebApi.dll"]
