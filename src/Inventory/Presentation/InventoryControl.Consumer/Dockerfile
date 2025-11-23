FROM mcr.microsoft.com/dotnet/runtime:10.0 AS base
USER $APP_UID
WORKDIR /app

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/Inventory/Presentation/InventoryControl.Consumer/InventoryControl.Consumer.csproj", "Inventory/Presentation/InventoryControl.Consumer/"]
RUN dotnet restore "Inventory/Presentation/InventoryControl.Consumer/InventoryControl.Consumer.csproj"
COPY . .
WORKDIR "Inventory/Presentation/InventoryControl.Consumer"
RUN dotnet build "./InventoryControl.Consumer.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./InventoryControl.Consumer.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "InventoryControl.Consumer.dll"]
