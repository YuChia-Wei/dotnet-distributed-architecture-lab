"""R08: verify a durable Procurement receipt survives this lab's Kafka outage.

This script intentionally stops and restarts only the Kafka service in the
fixed mqarchlab-pr5-integration Compose project. It never initializes stock,
deletes data, or touches other Compose projects. Run only with an existing
Inventory ProductId whose stock can be observed before the test.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ["docker", "compose", "-p", "mqarchlab-pr5-integration",
           "--profile", "procurement-lab", "--profile", "verification"]
COMPOSE += [part for path in (
    "docker-compose/docker-compose.yml",
    "docker-compose/docker-compose.override.yml",
    "docker-compose/docker-compose.verification.yml",
    "docker-compose/docker-compose.procurement.yml",
) for part in ("-f", str(ROOT / path))]
PROCUREMENT = "http://127.0.0.1:8180/api/procurement"
INVENTORY = "http://127.0.0.1:8185/api/inventory"
PROJECT = "mqarchlab-pr5-integration"
SERVICE = "kafka"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def command(parts: list[str], timeout: int = 30) -> str:
    result = subprocess.run(parts, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(parts[:5])}; "
                           f"stderr={result.stderr.strip()[:1000]}")
    return result.stdout.strip()


def compose(*args: str, timeout: int = 30) -> str:
    return command(COMPOSE + list(args), timeout=timeout)


def broker_id() -> str:
    ids = compose("ps", "-a", "-q", SERVICE).splitlines()
    check(len(ids) == 1 and bool(ids[0]), "expected exactly one Kafka container in the fixed Compose project")
    return ids[0]


def broker_snapshot(expected_id: str | None = None) -> dict[str, Any]:
    container_id = broker_id()
    if expected_id:
        check(container_id == expected_id, "the selected Kafka container changed during verification")
    labels = json.loads(command(["docker", "inspect", "--format", "{{json .Config.Labels}}", container_id]))
    state = json.loads(command(["docker", "inspect", "--format", "{{json .State}}", container_id]))
    name = command(["docker", "inspect", "--format", "{{.Name}}", container_id])
    check(labels.get("com.docker.compose.project") == PROJECT and
          labels.get("com.docker.compose.service") == SERVICE and name == "/kafka",
          "Kafka container labels/name do not match the authorized integration project")
    return {"containerId": container_id, "name": name,
            "projectLabel": labels["com.docker.compose.project"],
            "serviceLabel": labels["com.docker.compose.service"],
            "running": state.get("Running"), "status": state.get("Status")}


def http(method: str, url: str, payload: dict[str, Any] | None = None,
         timeout: float = 10) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        response = urllib.request.urlopen(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        raw = response.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            body = raw
        return {"status": response.status, "body": body}


def stock(product_id: uuid.UUID, timeout: float = 10) -> tuple[int, dict[str, Any]]:
    response = http("GET", f"{INVENTORY}/product/{product_id}", timeout=timeout)
    check(response["status"] == 200 and isinstance(response["body"], dict),
          "Inventory ProductId is not initialized or its stock endpoint is unavailable")
    check(str(response["body"].get("productId", "")).lower() == str(product_id),
          "Inventory returned a different ProductId")
    amount = response["body"].get("availableQuantity")
    check(type(amount) is int and 0 <= amount <= 2_147_483_644,
          "Inventory stock is missing, invalid, or cannot safely increase by three")
    return amount, response


def pg_json(service: str, database: str, sql: str) -> Any:
    check(service in {"postgres-procurement", "postgres-inventory"}, "unexpected PostgreSQL service")
    check(database in {"procurement_db", "inventory_db"}, "unexpected PostgreSQL database")
    output = compose("exec", "-T", service, "psql", "-U", "user", "-d", database,
                     "-X", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-c", sql)
    return json.loads(output)


def procurement_receipt(receipt_id: uuid.UUID) -> dict[str, Any] | None:
    sql = f"""
    SELECT coalesce((SELECT json_build_object(
      'receiptId',receipt_id,'purchaseOrderId',purchase_order_id,
      'productId',product_id,'quantity',quantity,'receivedAt',received_at)
      FROM procurement_receipts WHERE receipt_id='{receipt_id}'::uuid), 'null'::json);
    """
    return pg_json("postgres-procurement", "procurement_db", sql)


def source_outbox(receipt_id: uuid.UUID) -> dict[str, Any] | None:
    sql = f"""
    SELECT coalesce((SELECT json_build_object(
      'id',id,'partitionKey',partition_key,'payload',payload,
      'publishedAt',published_at,'parkedAt',parked_at,
      'attempts',attempts,'lastError',last_error)
      FROM procurement_outbox WHERE id='{receipt_id}'::uuid), 'null'::json);
    """
    return pg_json("postgres-procurement", "procurement_db", sql)


def outgoing_envelopes(receipt_id: uuid.UUID) -> list[dict[str, Any]]:
    # The fixed application config uses procurement_wolverine. Wolverine's
    # message store names this table wolverine_outgoing_envelopes. Its body may
    # be bytea, so search both textual UUID and hex-encoded JSON body bytes.
    canonical, compact = str(receipt_id), receipt_id.hex
    encoded = canonical.encode("ascii").hex()
    sql = f"""
    SELECT coalesce(json_agg(json_build_object(
      'id',envelope_json->>'id','destination',envelope_json->>'destination',
      'ownerId',envelope_json->>'owner_id','deduplicationId',envelope_json->>'deduplication_id')),
      '[]'::json)
    FROM (SELECT to_jsonb(e) AS envelope_json
          FROM procurement_wolverine.wolverine_outgoing_envelopes e) AS envelopes
    WHERE lower(envelope_json::text) LIKE '%{canonical}%'
       OR lower(envelope_json::text) LIKE '%{compact}%'
       OR lower(envelope_json::text) LIKE '%{encoded}%';
    """
    return pg_json("postgres-procurement", "procurement_db", sql)


def inventory_receipt(receipt_id: uuid.UUID) -> dict[str, Any] | None:
    sql = f"""
    SELECT coalesce((SELECT json_build_object(
      'receiptId',receiptid,'purchaseOrderId',purchaseorderid,
      'productId',productid,'quantity',quantity,
      'resultingStock',resultingstock,'completedAt',completedat)
      FROM inventorygoodsreceipts WHERE receiptid='{receipt_id}'::uuid), 'null'::json);
    """
    return pg_json("postgres-inventory", "inventory_db", sql)


def observe(evidence: dict[str, Any], label: str, value: Any) -> Any:
    evidence["observations"].append({"at": now(), "label": label, "value": value})
    return value


def run(product_id: uuid.UUID, evidence: dict[str, Any]) -> None:
    compose("config", "--quiet")
    schema = pg_json("postgres-procurement", "procurement_db",
                     "SELECT to_json(coalesce(to_regclass('procurement_wolverine.wolverine_outgoing_envelopes')::text, ''));" )
    check(schema == "procurement_wolverine.wolverine_outgoing_envelopes",
          "Procurement Wolverine outgoing envelope table is absent")
    initial, initial_response = stock(product_id)
    observe(evidence, "initial Inventory stock", initial_response)
    before = broker_snapshot()
    observe(evidence, "Kafka before", before)
    check(before["running"] is True, "Kafka must be running before R08 begins")
    evidence["brokerContainerId"] = before["containerId"]

    quote = observe(evidence, "direct quote", http("GET", PROCUREMENT + "/suppliers/direct/catalog/REAL-001"))
    check(quote["status"] == 200 and quote["body"].get("sku") == "REAL-001" and
          quote["body"].get("currency") == "TWD" and quote["body"].get("origin") == "sandbox",
          "direct supplier quote is unavailable or unexpected")
    client_id = uuid.uuid4()
    purchase = observe(evidence, "accepted purchase", http("POST", PROCUREMENT + "/purchase-orders", {
        "clientRequestId": str(client_id), "productId": str(product_id),
        "supplierSku": "REAL-001", "quantity": 3, "unitPrice": quote["body"]["unitPrice"],
        "currency": "TWD", "provider": "direct"}))
    check(purchase["status"] == 201 and purchase["body"].get("state") == "Accepted",
          "three-unit direct purchase was not accepted")
    purchase_id = uuid.UUID(purchase["body"]["id"])
    check(purchase["body"]["identity"].get("clientRequestId", "").lower() == str(client_id),
          "purchase response changed client identity")
    evidence["identities"] = {"productId": str(product_id), "clientRequestId": str(client_id),
                              "purchaseOrderId": str(purchase_id)}
    pre_stop, pre_stop_response = stock(product_id)
    observe(evidence, "stock after supplier acceptance", pre_stop_response)
    check(pre_stop == initial, "supplier acceptance changed Inventory stock")

    # stopAttempted is set before invoking Docker so finally can recover even
    # if Docker reports a partial failure after stopping the broker.
    evidence["stopAttempted"] = True
    compose("stop", SERVICE, timeout=60)
    stopped = broker_snapshot(before["containerId"])
    observe(evidence, "Kafka stopped", stopped)
    check(stopped["running"] is False, "Kafka remained running after scoped stop")

    receipt_id = uuid.uuid4()
    evidence["identities"]["receiptId"] = str(receipt_id)
    receipt = observe(evidence, "receipt committed while Kafka stopped",
                      http("POST", PROCUREMENT + f"/purchase-orders/{purchase_id}/receipts",
                           {"receiptId": str(receipt_id), "quantity": 3}))
    check(receipt["status"] == 201 and receipt["body"].get("created") is True,
          "receipt did not commit as a new durable business fact")
    item = receipt["body"].get("receipt", {})
    check(str(item.get("receiptId", "")).lower() == str(receipt_id) and
          str(item.get("purchaseOrderId", "")).lower() == str(purchase_id) and
          str(item.get("productId", "")).lower() == str(product_id) and
          item.get("quantity") == 3, "receipt response identity or quantity differs")
    offline_stock, offline_response = stock(product_id)
    observe(evidence, "stock with Kafka stopped", offline_response)
    check(offline_stock == pre_stop, "Inventory stock changed while Kafka was stopped")

    stored_receipt = observe(evidence, "Procurement receipt row", procurement_receipt(receipt_id))
    source = observe(evidence, "Procurement source outbox", source_outbox(receipt_id))
    outgoing = observe(evidence, "Procurement Wolverine outgoing envelopes", outgoing_envelopes(receipt_id))
    check(stored_receipt is not None and str(stored_receipt["receiptId"]) == str(receipt_id) and
          str(stored_receipt["purchaseOrderId"]) == str(purchase_id) and
          str(stored_receipt["productId"]) == str(product_id) and
          stored_receipt["quantity"] == 3, "Procurement receipt row is absent or changed")
    check(source is not None and str(source["id"]) == str(receipt_id) and
          source["partitionKey"] == product_id.hex and
          source["payload"].get("receiptId", "").lower() == str(receipt_id) and
          source["payload"].get("purchaseOrderId", "").lower() == str(purchase_id) and
          source["payload"].get("productId", "").lower() == str(product_id) and
          source["payload"].get("quantity") == 3 and source["parkedAt"] is None,
          "source outbox row/payload is absent, changed, or parked")
    check(source["publishedAt"] is None or bool(outgoing),
          "source outbox claims Wolverine handoff but no pending outgoing envelope was found")

    compose("start", SERVICE, timeout=60)
    restarted = broker_snapshot(before["containerId"])
    observe(evidence, "Kafka restarted", restarted)
    check(restarted["running"] is True, "Kafka did not restart in the selected container")
    deadline = time.monotonic() + 120
    history: list[dict[str, Any]] = []
    while True:
        remaining = deadline - time.monotonic()
        check(remaining > 0, "Inventory did not apply the one receipt within 120 seconds")
        try:
            current, response = stock(product_id, timeout=min(10, remaining))
            history.append({"at": now(), "stock": current, "status": response["status"]})
            if current == pre_stop + 3:
                break
            check(current <= pre_stop + 3, "Inventory stock overshot the expected receipt increment")
        except (urllib.error.URLError, TimeoutError):
            history.append({"at": now(), "error": "Inventory HTTP unavailable during recovery"})
        time.sleep(min(2, max(0, deadline - time.monotonic())))
    observe(evidence, "Inventory recovery polling", history)
    ledger = observe(evidence, "Inventory receipt ledger", inventory_receipt(receipt_id))
    check(ledger is not None and str(ledger["receiptId"]) == str(receipt_id) and
          str(ledger["productId"]) == str(product_id) and ledger["quantity"] == 3 and
          ledger["resultingStock"] == pre_stop + 3 and ledger["completedAt"] is not None,
          "Inventory receipt ledger does not prove a completed single increment")
    replay = observe(evidence, "receipt replay after recovery",
                     http("POST", PROCUREMENT + f"/purchase-orders/{purchase_id}/receipts",
                          {"receiptId": str(receipt_id), "quantity": 3}))
    check(replay["status"] == 200 and replay["body"].get("created") is False,
          "matching receipt replay was not outcome-only")
    time.sleep(3)
    final_stock, final_response = stock(product_id)
    observe(evidence, "Inventory stock after replay", final_response)
    check(final_stock == pre_stop + 3, "receipt replay caused a duplicate stock increment")
    observe(evidence, "source outbox after recovery", source_outbox(receipt_id))
    observe(evidence, "Wolverine envelopes after recovery", outgoing_envelopes(receipt_id))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product-id", required=True, type=uuid.UUID,
                        help="Existing initialized Inventory ProductId; stock is never reset")
    parser.add_argument("--output", type=Path,
                        default=Path("artifacts/procurement-lab/broker-recovery.json"))
    args = parser.parse_args()
    check(args.product_id.int != 0, "ProductId must not be the empty UUID")
    evidence: dict[str, Any] = {"scenario": "R08", "workflow": "2026-09-26-procurement-supplier-lab",
                                "startedAt": now(), "status": "failed", "observations": [],
                                "stopAttempted": False}
    try:
        run(args.product_id, evidence)
        evidence["status"] = "passed"
    except Exception as error:
        evidence["error"] = f"{type(error).__name__}: {error}"
    finally:
        if evidence["stopAttempted"]:
            try:
                expected = evidence["brokerContainerId"]
                current = broker_snapshot(expected)
                if current["running"] is not True:
                    compose("start", SERVICE, timeout=60)
                final = broker_snapshot(expected)
                check(final["running"] is True, "Kafka was not running after finally recovery")
                evidence["brokerAfter"] = final
                evidence["cleanup"] = "Kafka running in the same verified Compose container"
            except Exception as error:
                evidence["cleanup"] = f"FAILED: {type(error).__name__}: {error}"
                evidence["status"] = "failed"
        evidence["endedAt"] = now()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"R08 {evidence['status']}; evidence: {args.output}", flush=True)
        if evidence.get("error"):
            print(evidence["error"], file=sys.stderr)
        if str(evidence.get("cleanup", "")).startswith("FAILED:"):
            print(evidence["cleanup"], file=sys.stderr)
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
