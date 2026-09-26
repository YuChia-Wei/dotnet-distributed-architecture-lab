FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish samples/SupplierMock/SupplierMock.WebApi/SupplierMock.WebApi.csproj -c Release -o /app/publish
FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /app/publish .
ENV ASPNETCORE_URLS=http://0.0.0.0:8080 SupplierMock__NativeListenUrl=http://0.0.0.0:9091 SupplierMock__AdminUrl=http://127.0.0.1:9091
EXPOSE 8080 9091
ENTRYPOINT ["dotnet", "SupplierMock.WebApi.dll"]
