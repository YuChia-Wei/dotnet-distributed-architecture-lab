# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY ["src/Product.Consumer/Product.Consumer.csproj", "Product.Consumer/"]
RUN dotnet restore "Product.Consumer/Product.Consumer.csproj"
COPY src/Product.Consumer/ .
WORKDIR "/src/Product.Consumer"
RUN dotnet build "Product.Consumer.csproj" -c Release -o /app/build

# Stage 2: Publish
FROM build AS publish
RUN dotnet publish "Product.Consumer.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Stage 3: Final
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Product.Consumer.dll"]
