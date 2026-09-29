# REST API Resource Path Rationale

## Decision Pattern

The default is:

- nested paths for create endpoints;
- flat paths for resource operations.

For example:

- `POST /products/{productId}/pbis`
- `GET /pbis/{pbiId}`
- `PATCH /pbis/{pbiId}`

## Why

### 1. Creation Needs to Express Ownership Context

A create operation usually needs to state explicitly which parent collection receives the new resource.
A nested path expresses this context directly in the URL instead of hiding it only in the body.

### 2. A Created Resource Should Have an Independent Identity

Once a resource exists, it should be addressed by its own identity rather than remain permanently attached to its parent's path.
This better reflects the independent lifecycle of an aggregate root in DDD.

### 3. Path Semantics Are More Stable

If a resource might later move, be reorganized, or no longer belong to the same parent, a flat resource path is less likely to be affected.

## Why Not

### Nest Every Path

Drawbacks:

- Treats the resource as subordinate to its parent.
- Weakens the aggregate root's independent identity.
- Produces increasingly long and deep paths.

### Flatten Every Path

Drawbacks:

- Loses the semantics of which collection receives a newly created resource.
- Makes error handling less intuitive when the parent resource does not exist.

## Practical Rule

- create: prefer a nested path;
- read/update/delete by ID: prefer a flat path;
- collection query: provide global and parent-scoped variants when needed.
