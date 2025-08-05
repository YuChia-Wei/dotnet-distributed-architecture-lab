FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
USER $APP_UID
WORKDIR /app
EXPOSE 8080
EXPOSE 8081

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/Product/Presentation/SaleProducts.WebApi/SaleProducts.WebApi.csproj", "src/Product/Presentation/SaleProducts.WebApi/"]
COPY ["src/Product/DomainCore/SaleProducts.Infrastructure/SaleProducts.Infrastructure.csproj", "src/Product/DomainCore/SaleProducts.Infrastructure/"]
COPY ["src/Product/DomainCore/SaleProducts.Applications/SaleProducts.Applications.csproj", "src/Product/DomainCore/SaleProducts.Applications/"]
COPY ["src/Product/DomainCore/SaleProducts.Domains/SaleProducts.Domains.csproj", "src/Product/DomainCore/SaleProducts.Domains/"]
RUN dotnet restore "src/Product/Presentation/SaleProducts.WebApi/SaleProducts.WebApi.csproj"
COPY . .
WORKDIR "/src/src/Product/Presentation/SaleProducts.WebApi"
RUN dotnet build "./SaleProducts.WebApi.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./SaleProducts.WebApi.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "SaleProducts.WebApi.dll"]
