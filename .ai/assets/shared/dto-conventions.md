# DTO Conventions (Dotnet)

## Location
- `src/Api/Contracts/<Aggregate>/Requests`
- `src/Api/Contracts/<Aggregate>/Responses`
- Common: `src/Api/Contracts/Common`

## Naming
- Requests: `CreateXxxRequest`, `UpdateXxxRequest`, `DeleteXxxRequest`
- Responses: `XxxResponse`, `XxxListResponse`, `ApiErrorResponse`

## Rules
- DTOs are separate files (no inner classes)
- DTOs must not expose domain entities
- Validate request DTOs with data annotations
