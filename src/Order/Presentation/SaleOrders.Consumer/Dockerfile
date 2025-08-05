FROM mcr.microsoft.com/dotnet/runtime:9.0 AS base
USER $APP_UID
WORKDIR /app

FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/Order/Presentation/SaleOrders.Consumer/SaleOrders.Consumer.csproj", "src/Order/Presentation/SaleOrders.Consumer/"]
COPY ["src/Shared/Lab.SharedKernel/Lab.SharedKernel.csproj", "src/Shared/Lab.SharedKernel/"]
RUN dotnet restore "src/Order/Presentation/SaleOrders.Consumer/SaleOrders.Consumer.csproj"
COPY . .
WORKDIR "/src/src/Order/Presentation/SaleOrders.Consumer"
RUN dotnet build "./SaleOrders.Consumer.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "./SaleOrders.Consumer.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "SaleOrders.Consumer.dll"]
