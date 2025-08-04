FROM mcr.microsoft.com/dotnet/runtime:9.0 AS base
USER $APP_UID
WORKDIR /app

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/SaleProducts.Consumer/SaleProducts.Consumer.csproj", "src/SaleProducts.Consumer/"]
RUN dotnet restore "src/SaleProducts.Consumer/SaleProducts.Consumer.csproj"
COPY . .
WORKDIR "/src/src/SaleProducts.Consumer"
RUN dotnet build "./SaleProducts.Consumer.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./SaleProducts.Consumer.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "SaleProducts.Consumer.dll"]
