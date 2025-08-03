FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
USER $APP_UID
WORKDIR /app
EXPOSE 8080
EXPOSE 8081

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/SaleProducts.Api/SaleProducts.Api.csproj", "src/SaleProducts.Api/"]
COPY ["src/SaleProducts.Infrastructure/SaleProducts.Infrastructure.csproj", "src/SaleProducts.Infrastructure/"]
COPY ["src/SaleProducts.Domains/SaleProducts.Domains.csproj", "src/SaleProducts.Domains/"]
COPY ["src/SaleProducts.Applications/SaleProducts.Applications.csproj", "src/SaleProducts.Applications/"]
RUN dotnet restore "src/SaleProducts.Api/SaleProducts.Api.csproj"
COPY . .
WORKDIR "/src/src/SaleProducts.Api"
RUN dotnet build "./SaleProducts.Api.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./SaleProducts.Api.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "SaleProducts.Api.dll"]
