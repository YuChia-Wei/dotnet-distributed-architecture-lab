# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Copy solution file and source code
COPY MQArchLab.slnx .
COPY src/ ./src/

# Restore dependencies for the entire solution
RUN dotnet restore MQArchLab.slnx

# Stage 2: Publish
FROM build AS publish
RUN dotnet publish src/Product/Presentation/SaleProducts.WebApi/SaleProducts.WebApi.csproj -c Release -o /app/publish /p:UseAppHost=false

# Stage 3: Final
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "SaleProducts.WebApi.dll"]