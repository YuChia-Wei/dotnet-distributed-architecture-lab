"""Supplemental Issue #17 HTTP checks against the fixed local supplier lab.

Requires an already initialized Inventory ProductId. The checks create supplier
orders and Procurement purchases, but never record a goods receipt or alter
stock. Run only while the local Compose lab is ready; this script controls
transient supplier modes and delay, and restores hybrid/zero in finally.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any

import test_contracts as core


INVENTORY = "http://127.0.0.1:8185/api/inventory"
VARIANTS = (("quantity", {"quantity": 3}),
            ("unitPrice", {"unitPrice": 101}),
            ("currency", {"currency": "USD"}),
            ("sku", {"sku": "REAL-001"}))


def stock(product_id: uuid.UUID) -> tuple[int, dict[str, Any]]:
    response = core.http("GET", f"{INVENTORY}/product/{product_id}")
    core.check(response["status"] == 200 and isinstance(response["body"], dict),
               "retained Inventory ProductId is not initialized")
    core.check(str(response["body"].get("productId", "")).lower() == str(product_id),
               "Inventory returned a different ProductId")
    amount = response["body"].get("availableQuantity")
    core.check(type(amount) is int and amount >= 0, "Inventory stock is not a nonnegative integer")
    return amount, response


def assert_no_receipts(order: dict[str, Any], label: str) -> None:
    core.check(order.get("receivedQuantity") == 0 and order.get("receipts") == [],
               f"{label}: Procurement recorded a receipt without physical receiving")


def p04_retained(case: dict[str, Any], product_id: uuid.UUID) -> None:
    before_stock, before_response = stock(product_id)
    core.observed(case, "Inventory before timeout", before_response)
    quote = core.observed(case, "direct real quote",
                          core.http("GET", core.PROCUREMENT + "/api/procurement/suppliers/direct/catalog/REAL-001"))
    core.check(quote["status"] == 200 and quote["body"].get("sku") == "REAL-001" and
               quote["body"].get("currency") == "TWD" and quote["body"].get("origin") == "sandbox",
               "P04 retained real quote was unavailable")
    delay = core.observed(case, "delay 4000",
                          core.http("PUT", core.SANDBOX + "/sandbox/control", {"delayAfterCommitMs": 4000}))
    core.check(delay["status"] == 200 and delay["body"].get("delayAfterCommitMs") == 4000,
               "P04 retained delay was not applied")
    try:
        client_id = str(uuid.uuid4())
        payload = core.purchase_payload(client_id, str(product_id), quantity=3,
                                        unitPrice=quote["body"]["unitPrice"])
        before = core.journal()
        created = core.observed(case, "unknown purchase after supplier commit",
                                core.http("POST", core.PROCUREMENT + "/api/procurement/purchase-orders", payload))
        core.check(created["status"] == 202 and isinstance(created["body"], dict) and
                   created["body"].get("state") == "SubmissionUnknown",
                   "P04 retained purchase did not preserve unknown outcome")
        purchase_id = str(uuid.UUID(created["body"]["id"]))
        case["observations"].append({"label": "identities", "productId": str(product_id),
                                      "clientRequestId": client_id, "purchaseOrderId": purchase_id})
        assert_no_receipts(created["body"], "unknown purchase")
        supplier = core.observed(case, "supplier committed order lookup",
                                 core.http("GET", core.SANDBOX +
                                           f"/supplier/orders/by-client-request/{client_id}"))
        core.check(supplier["status"] == 200 and supplier["body"].get("origin") == "sandbox",
                   "P04 retained supplier commit is absent")
        supplier_id = core.assert_order(supplier, client_id, "REAL-001", 3)
        reconciled = core.observed(case, "reconcile using original supplier key",
                                   core.http("POST", core.PROCUREMENT +
                                             f"/api/procurement/purchase-orders/{purchase_id}/reconcile"))
        core.check(reconciled["status"] == 200 and reconciled["body"].get("state") == "Accepted" and
                   str(reconciled["body"].get("supplierOrderId", "")).lower() == supplier_id.lower(),
                   "P04 retained reconcile did not recover the original supplier order")
        assert_no_receipts(reconciled["body"], "reconciled purchase")
        local = core.observed(case, "local purchase after reconcile",
                              core.http("GET", core.PROCUREMENT + f"/api/procurement/purchase-orders/{purchase_id}"))
        core.check(local["status"] == 200 and local["body"].get("state") == "Accepted",
                   "P04 retained local purchase was not accepted after reconcile")
        assert_no_receipts(local["body"], "local purchase")
        after = core.journal()
        added = core.new_entries(before, after)
        post_count = core.hits(added, "POST", "/supplier/orders", client_id)
        lookup_count = core.hits(added, "GET", f"/supplier/orders/by-client-request/{client_id}", client_id)
        case["observations"].append({"label": "sandbox journal after timeout/reconcile",
                                      "clientRequestId": client_id,
                                      "supplierPostDelta": post_count, "lookupDelta": lookup_count,
                                      "matched": [entry for entry in added if
                                                  str(entry.get("clientRequestId", "")).lower() == client_id]})
        core.check(post_count == 1 and lookup_count >= 2,
                   "P04 retained retried supplier POST or did not reconcile through supplier GET")
        after_stock, after_response = stock(product_id)
        core.observed(case, "Inventory after reconcile", after_response)
        core.check(after_stock == before_stock,
                   "P04 retained supplier acceptance/reconcile changed Inventory stock")
    finally:
        reset = core.observed(case, "delay reset",
                              core.http("PUT", core.SANDBOX + "/sandbox/control", {"delayAfterCommitMs": 0}))
        core.check(reset["status"] == 200 and reset["body"].get("delayAfterCommitMs") == 0,
                   "P04 retained delay reset failed")


def fixture_exact(case: dict[str, Any], engine: str) -> None:
    origin, base = ("wiremock" if engine == "wiremock" else "microcks"), core.engine_base(engine)
    case["observations"].append({"label": "mode", **core.set_mode(engine, "hybrid")})
    fixture = core.order_payload(core.FIXTURE_ID, "MOCK-001")
    core.check(fixture == {"clientRequestId": core.FIXTURE_ID, "sku": "MOCK-001",
                           "quantity": 2, "unitPrice": 100, "currency": "TWD"},
               "fixed fixture request fields differ")
    case["observations"].append({"label": "exact request", "payload": fixture})
    response = core.supplier_probe(case, "exact native POST", base, "POST", "/supplier/orders",
                                   fixture, origin, False, core.FIXTURE_ID)
    core.assert_order(response, core.FIXTURE_ID, "MOCK-001", 2, core.FIXTURE_ORDER_ID)
    lookup = core.supplier_probe(case, "exact native GET lookup", base, "GET",
                                 f"/supplier/orders/by-client-request/{core.FIXTURE_ID}",
                                 None, origin, False, core.FIXTURE_ID)
    core.assert_order(lookup, core.FIXTURE_ID, "MOCK-001", 2, core.FIXTURE_ORDER_ID)


def fixture_variant(case: dict[str, Any], engine: str, label: str,
                    changes: dict[str, Any]) -> None:
    mock_origin = "wiremock" if engine == "wiremock" else "microcks"
    case["observations"].append({"label": "mode", **core.set_mode(engine, "hybrid")})
    payload = {**core.order_payload(core.FIXTURE_ID, "MOCK-001"), **changes}
    case["observations"].append({"label": label + " request", "payload": payload})
    response = core.supplier_probe(case, label + " changed fixture", core.engine_base(engine),
                                   "POST", "/supplier/orders", payload, None, True, core.FIXTURE_ID)
    body = response["body"]
    core.check(isinstance(body, dict) and response["status"] in {200, 400, 404, 409},
               f"{engine} {label}: expected sandbox result/rejection, got {response['status']}")
    core.check(body.get("origin") != mock_origin and
               str(body.get("supplierOrderId", "")).lower() != core.FIXTURE_ORDER_ID and
               response["originHeader"] != mock_origin,
               f"{engine} {label}: variant received fixed mock acceptance")
    if response["status"] == 200:
        core.check(body.get("origin") == "sandbox" and
                   str(body.get("clientRequestId", "")).lower() == core.FIXTURE_ID and
                   body.get("sku") == payload["sku"] and body.get("quantity") == payload["quantity"] and
                   float(body.get("unitPrice", -1)) == payload["unitPrice"] and
                   body.get("currency") == payload["currency"],
                   f"{engine} {label}: sandbox response changed request fields")


def fixture_mock_only_variants(case: dict[str, Any], engine: str) -> None:
    mock_origin = "wiremock" if engine == "wiremock" else "microcks"
    case["observations"].append({"label": "mode", **core.set_mode(engine, "mock")})
    for label, changes in VARIANTS:
        payload = {**core.order_payload(core.FIXTURE_ID, "MOCK-001"), **changes}
        case["observations"].append({"label": label + " mock-only request", "payload": payload})
        response = core.supplier_probe(case, label + " mock-only changed fixture",
                                       core.engine_base(engine), "POST", "/supplier/orders",
                                       payload, None, False, core.FIXTURE_ID)
        body = response["body"] if isinstance(response["body"], dict) else {}
        fixed_acceptance = (200 <= response["status"] < 300 and
                            (str(body.get("supplierOrderId", "")).lower() == core.FIXTURE_ORDER_ID or
                             (body.get("origin") == mock_origin and
                              str(body.get("clientRequestId", "")).lower() == core.FIXTURE_ID)))
        core.check(not fixed_acceptance,
                   f"{engine} {label}: mock-only variant received fixed mock acceptance")
        core.check(body.get("origin") != "sandbox" and response["originHeader"] != "sandbox",
                   f"{engine} {label}: mock-only variant claimed sandbox origin")


def procurement_profile(case: dict[str, Any], engine: str, product_id: uuid.UUID) -> None:
    before_stock, before_response = stock(product_id)
    core.observed(case, "Inventory before provider purchase", before_response)
    case["observations"].append({"label": "mode", **core.set_mode(engine, "hybrid")})
    quote = core.supplier_probe(case, "Procurement real quote", core.PROCUREMENT, "GET",
                                f"/api/procurement/suppliers/{engine}/catalog/REAL-001", None,
                                "sandbox", True, upstream_path="/supplier/catalog/REAL-001")
    core.check(quote["body"].get("sku") == "REAL-001" and quote["body"].get("currency") == "TWD",
               "Procurement provider quote changed SKU/currency")
    client_id = str(uuid.uuid4())
    payload = core.purchase_payload(client_id, str(product_id), provider=engine,
                                    unitPrice=quote["body"]["unitPrice"])
    created = core.supplier_probe(case, "Procurement real purchase", core.PROCUREMENT, "POST",
                                  "/api/procurement/purchase-orders", payload, None, True,
                                  client_id, upstream_path="/supplier/orders")
    core.check(created["status"] == 201 and isinstance(created["body"], dict) and
               created["body"].get("state") == "Accepted", "Procurement provider purchase was not accepted")
    identity = created["body"].get("identity", {})
    core.check(str(identity.get("clientRequestId", "")).lower() == client_id and
               str(identity.get("productId", "")).lower() == str(product_id) and
               identity.get("provider") == engine and identity.get("supplierSku") == "REAL-001" and
               identity.get("quantity") == 2 and identity.get("currency") == "TWD" and
               float(identity.get("unitPrice", -1)) == float(quote["body"]["unitPrice"]),
               "Procurement provider purchase identity differs")
    assert_no_receipts(created["body"], "provider purchase")
    upstream = core.observed(case, "sandbox order lookup",
                             core.http("GET", core.SANDBOX +
                                       f"/supplier/orders/by-client-request/{client_id}"))
    core.check(upstream["status"] == 200 and upstream["body"].get("origin") == "sandbox",
               "Procurement provider purchase did not persist at sandbox")
    supplier_id = core.assert_order(upstream, client_id, "REAL-001", 2)
    core.check(str(created["body"].get("supplierOrderId", "")).lower() == supplier_id.lower(),
               "Procurement provider supplier order ID differs")
    after_stock, after_response = stock(product_id)
    core.observed(case, "Inventory after provider purchase", after_response)
    core.check(after_stock == before_stock, "Procurement provider quote/create changed Inventory stock")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product-id", type=uuid.UUID, required=True,
                        help="Existing initialized Inventory ProductId; stock is not reset")
    parser.add_argument("--output", type=Path,
                        default=Path("artifacts/procurement-lab/supplemental-http-contracts.json"))
    args = parser.parse_args()
    core.check(args.product_id.int != 0, "ProductId must not be empty")
    results: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {"workflow": "2026-09-26-procurement-supplier-lab",
                                "suite": "supplemental HTTP contracts", "productId": str(args.product_id),
                                "startedAt": core.utc_now(), "scenarioResults": results}
    try:
        core.run_case(results, "P04-retained-stock", lambda case: p04_retained(case, args.product_id))
        for engine in ("wiremock", "microcks"):
            core.run_case(results, f"FIXTURE-exact-{engine}",
                          lambda case, selected=engine: fixture_exact(case, selected))
            for label, changes in VARIANTS:
                core.run_case(results, f"FIXTURE-{label}-{engine}",
                              lambda case, selected=engine, variation=label, fields=changes:
                              fixture_variant(case, selected, variation, fields))
            core.run_case(results, f"FIXTURE-mock-only-altered-{engine}",
                          lambda case, selected=engine: fixture_mock_only_variants(case, selected))
            core.run_case(results, f"PROFILE-{engine}",
                          lambda case, selected=engine: procurement_profile(case, selected, args.product_id))
    finally:
        cleanup: list[dict[str, Any]] = []
        for label, operation in (("sandbox delay", lambda: core.http("PUT", core.SANDBOX + "/sandbox/control",
                                                                 {"delayAfterCommitMs": 0})),
                                 ("WireMock hybrid", lambda: core.set_mode("wiremock", "hybrid")),
                                 ("Microcks hybrid", lambda: core.set_mode("microcks", "hybrid"))):
            try:
                result = operation()
                if label == "sandbox delay":
                    core.check(result["status"] == 200 and result["body"].get("delayAfterCommitMs") == 0,
                               "sandbox delay reset was not confirmed")
                cleanup.append({"label": label, "status": "passed", "result": result})
            except Exception as error:
                cleanup.append({"label": label, "status": "failed", "error": str(error)})
        evidence["cleanup"] = cleanup
        evidence["endedAt"] = core.utc_now()
        evidence["passed"] = all(item["status"] == "passed" for item in results + cleanup)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Supplemental evidence: {args.output}", flush=True)
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
