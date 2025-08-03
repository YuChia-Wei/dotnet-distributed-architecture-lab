FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS base
USER $APP_UID
WORKDIR /app
EXPOSE 8080
EXPOSE 8081

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/SaleOrders.WebApi/SaleOrders.WebApi.csproj", "src/SaleOrders.WebApi/"]
COPY ["src/SaleOrders.Infrastructure/SaleOrders.Infrastructure.csproj", "src/SaleOrders.Infrastructure/"]
COPY ["src/SaleOrders.Applications/SaleOrders.Applications.csproj", "src/SaleOrders.Applications/"]
COPY ["src/SaleOrders.Domains/SaleOrders.Domains.csproj", "src/SaleOrders.Domains/"]
RUN dotnet restore "src/SaleOrders.WebApi/SaleOrders.WebApi.csproj"
COPY . .
WORKDIR "/src/src/SaleOrders.WebApi"
RUN dotnet build "./SaleOrders.WebApi.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./SaleOrders.WebApi.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "SaleOrders.WebApi.dll"]
