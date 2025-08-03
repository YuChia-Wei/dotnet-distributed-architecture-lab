# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY ["src/Order.Consumer/Order.Consumer.csproj", "Order.Consumer/"]
RUN dotnet restore "Order.Consumer/Order.Consumer.csproj"
COPY src/Order.Consumer/ .
WORKDIR "/src/Order.Consumer"
RUN dotnet build "Order.Consumer.csproj" -c Release -o /app/build

# Stage 2: Publish
FROM build AS publish
RUN dotnet publish "Order.Consumer.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Stage 3: Final
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Order.Consumer.dll"]
