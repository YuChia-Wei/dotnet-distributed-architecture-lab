# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY ["src/Orders.Api/Orders.Api.csproj", "Orders.Api/"]
RUN dotnet restore "Orders.Api/Orders.Api.csproj"
COPY src/Orders.Api/ .
WORKDIR "/src/Orders.Api"
RUN dotnet build "Orders.Api.csproj" -c Release -o /app/build

# Stage 2: Publish
FROM build AS publish
RUN dotnet publish "Orders.Api.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Stage 3: Final
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Orders.Api.dll"]
