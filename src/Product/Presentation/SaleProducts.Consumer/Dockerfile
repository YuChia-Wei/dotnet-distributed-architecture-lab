FROM mcr.microsoft.com/dotnet/runtime:10.0 AS base
USER $APP_UID
WORKDIR /app
EXPOSE 8080
EXPOSE 8443

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/Product/Presentation/SaleProducts.Consumer/SaleProducts.Consumer.csproj", "Product/Presentation/SaleProducts.Consumer/"]
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
