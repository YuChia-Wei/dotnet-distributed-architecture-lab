workspace "Distributed commerce - Structurizr pilot" "Code-backed localhost Kafka + frontend-lab + procurement-lab views; supplier acceptance does not increase stock." {
    configuration {
        scope softwaresystem
    }
    !impliedRelationships false
    model {
        supplier = softwareSystem "External supplier" "Owns quotes and supplier order acceptance. The direct profile uses SupplierSandbox; acceptance is not physical receipt." {
            tags "External"
        }
        commerce = softwareSystem "Distributed commerce lab" "Owns product catalog, orders, inventory, purchases and actual goods receipts." {
            web = container "Vue storefront" "Browser UI for catalog, orders, stock, procurement and explicit receipt entry; assets served by web-frontend." "Vue 3 / TypeScript / Nginx"
            admin = container "Vue administration" "Browser UI for lab administration and supplier controls; assets served by admin-frontend." "Vue 3 / TypeScript / Nginx"
            gateway = container "YARP gateway" "Routes /web, /admin and four context API prefixes; exposes bounded supplier admin facades." "YARP / ASP.NET Core"
            productsApi = container "Products API" "Manages catalog commands and queries; enabled diagnostic publication is not a product business event stream." "ASP.NET Core / Dapper / Npgsql / Wolverine"
            productsConsumer = container "Products Consumer" "Hosts configured orders.integration.events subscription; business reaction is unresolved." ".NET Generic Host / Wolverine Kafka"
            ordersApi = container "Orders API" "Owns order lifecycle, event-sourced persistence, source-outbox relay and inventory reservation request/reply." "ASP.NET Core / Dapper / Npgsql / Wolverine"
            ordersConsumer = container "Orders Consumer" "Hosts products.integration.events diagnostic handlers and parallel-work examples; no confirmed business projection." ".NET Generic Host / Wolverine Kafka"
            inventoryApi = container "Inventory API" "Owns stock queries/commands, reservation request handling and enabled Inventory source-outbox relay." "ASP.NET Core / EF Core / Npgsql / Wolverine"
            inventoryConsumer = container "Inventory Consumer" "Handles GoodsReceived via receipt use case and atomic idempotent stock application; also has an orders topic listener." ".NET Generic Host / EF Core / Npgsql / Wolverine Kafka"
            procurementApi = container "Procurement API + receipt relay" "Owns supplier submission/reconciliation and actual receipt commands; hosts ProcurementOutboxRelay and Wolverine durable delivery in this process." "ASP.NET Core / Dapper / Npgsql / Wolverine Kafka"
            productsDb = container "Products database" "Stores product catalog state for Products." "PostgreSQL 16" {
                tags "Database"
            }
            ordersDb = container "Orders database" "Stores order events, read state, source outbox and Wolverine messaging state." "PostgreSQL 16" {
                tags "Database"
            }
            inventoryDb = container "Inventory database" "Stores stock, reservations, receipt deduplication/results, stock source outbox and messaging state." "PostgreSQL 16" {
                tags "Database"
            }
            procurementDb = container "Procurement database" "Stores purchases, unique receipts, source outbox and procurement_wolverine durable transport state." "PostgreSQL 16" {
                tags "Database"
            }
            kafka = container "Kafka" "Transports context events and inventory reservation requests/replies; asynchronous delivery may repeat." "Apache Kafka 4 / KRaft" {
                tags "Broker"
            }
        }
        web -> gateway "Calls same-origin commerce APIs from browser" "HTTP / JSON"
        admin -> gateway "Calls same-origin lab/admin APIs from browser" "HTTP / JSON"
        gateway -> web "Routes /web to Nginx assets and SPA fallback" "HTTP"
        gateway -> admin "Routes /admin to Nginx assets and SPA fallback" "HTTP"
        gateway -> productsApi "Forwards /api/products" "HTTP / JSON"
        gateway -> ordersApi "Forwards /api/orders" "HTTP / JSON"
        gateway -> inventoryApi "Forwards /api/inventory" "HTTP / JSON"
        gateway -> procurementApi "Forwards /api/procurement" "HTTP / JSON"
        gateway -> supplier "Forwards bounded supplier-sandbox admin facade (direct profile)" "HTTP / JSON"
        productsApi -> productsDb "Reads and writes catalog" "PostgreSQL wire protocol / Dapper + Npgsql"
        ordersApi -> ordersDb "Commits order events, read state and outbox; persists messaging state" "PostgreSQL wire protocol / Dapper + Npgsql"
        inventoryApi -> inventoryDb "Queries stock; commits stock/reservation outbox; relays stock events" "PostgreSQL wire protocol / EF Core + Npgsql"
        inventoryConsumer -> inventoryDb "Atomically deduplicates receipt, increases stock and stages stock event; persists inbox" "PostgreSQL wire protocol / EF Core + Npgsql"
        procurementApi -> procurementDb "Commits purchases/receipts/outbox and manages relay/durable transport state" "PostgreSQL wire protocol / Dapper + Npgsql"
        procurementApi -> supplier "Quotes, submits purchases and reconciles original clientRequestId (direct profile)" "HTTP / JSON"
        supplier -> procurementApi "Returns synchronous supplier order outcome; no stock mutation" "HTTP response / JSON"
        productsApi -> kafka "Publishes enabled diagnostics on products.integration.events; business events deferred" "Kafka protocol / Wolverine"
        ordersApi -> kafka "Publishes orders.integration.events and inventory.requests" "Kafka protocol / Wolverine"
        kafka -> ordersApi "Delivers reservation replies on orders.outbound.replies" "Kafka protocol / Wolverine"
        kafka -> inventoryApi "Delivers inventory.requests for reservation" "Kafka protocol / Wolverine"
        inventoryApi -> kafka "Publishes inventory.integration.events and reservation replies" "Kafka protocol / Wolverine"
        kafka -> productsConsumer "Delivers configured orders.integration.events subscription; business intent unresolved" "Kafka protocol / Wolverine"
        kafka -> ordersConsumer "Delivers products.integration.events diagnostics" "Kafka protocol / Wolverine"
        kafka -> inventoryConsumer "Delivers GoodsReceived on procurement.integration.events; also configured orders listener" "Kafka protocol / Wolverine"
        procurementApi -> kafka "Publishes GoodsReceived via hosted relay and durable transport outbox" "Kafka protocol / Wolverine"
    }
    views {
        container commerce "CoreContainers" "Current configured core topology; Kafka profile plus frontend/procurement overlays; no assumed business reactions." {
            include *
            autoLayout lr
        }
        dynamic commerce "GoodsReceipt" "Direct supplier success path then explicit receipt: supplier acceptance alone never increases Inventory stock." {
            web -> gateway "Submit purchase with stable clientRequestId"
            gateway -> procurementApi "POST /api/procurement/purchase-orders"
            procurementApi -> procurementDb "CreateOrGet unique purchase identity before external HTTP"
            procurementApi -> supplier "POST /supplier/orders using original clientRequestId (direct)"
            supplier -> procurementApi "Return accepted supplier order; this is NOT goods receipt"
            procurementApi -> procurementDb "Commit Accepted state only: no receipt, no GoodsReceived, no stock increase"
            web -> gateway "Later, after physical arrival, explicitly submit ReceiptId and quantity"
            gateway -> procurementApi "POST /api/procurement/purchase-orders/{id}/receipts"
            procurementApi -> procurementDb "T1: lock purchase; validate; commit purchase state + receipt + GoodsReceived source outbox atomically"
            procurementApi -> procurementDb "Hosted Relay leases committed procurement_outbox rows (SKIP LOCKED)"
            procurementApi -> procurementDb "Await Wolverine durable-outbox handoff into procurement_wolverine; then mark source published_at (NOT consumer completion)"
            procurementApi -> kafka "Durable transport publishes GoodsReceived to procurement.integration.events; key=ProductId N; stable ReceiptId; may redeliver"
            kafka -> inventoryConsumer "Deliver GoodsReceived through durable inbox; handler delegates receipt application"
            inventoryConsumer -> inventoryDb "T2: claim ReceiptId; lock existing stock; commit dedup result + increase + StockIncreased outbox atomically; matching replay has no new effect"
            autoLayout lr
        }
        styles {
            element "Element" {
                color #ffffff
                background #245b78
            }
            element "Database" {
                shape Cylinder
                background #507548
            }
            element "Broker" {
                shape Pipe
                background #84562d
            }
            element "External" {
                background #666666
            }
            relationship "Relationship" {
                color #52616b
            }
        }
    }
}
