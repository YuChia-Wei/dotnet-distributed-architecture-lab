# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY ["src/Orders.Consumer/Orders.Consumer.csproj", "Orders.Consumer/"]
RUN dotnet restore "Orders.Consumer/Orders.Consumer.csproj"
COPY src/Orders.Consumer/ .
WORKDIR "/src/Orders.Consumer"
RUN dotnet build "Orders.Consumer.csproj" -c Release -o /app/build

# Stage 2: Publish
FROM build AS publish
RUN dotnet publish "Orders.Consumer.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Stage 3: Final
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Orders.Consumer.dll"]
