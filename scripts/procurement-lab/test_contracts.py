"""Run the Issue #17 HTTP contract checks against the selected local Compose lab.

This intentionally uses only the Python standard library and fixed localhost
ports. It does not start, stop, or reset containers or databases.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROCUREMENT = "http://127.0.0.1:8180"
SANDBOX = "http://127.0.0.1:8181"
WIREMOCK_CONTROL = "http://127.0.0.1:8182"
WIREMOCK_NATIVE = "http://127.0.0.1:8183"
MICROCKS = "http://127.0.0.1:8184"
MICROCKS_API = MICROCKS + "/rest/Supplier+API/1.0.0"
FIXTURE_ID = "9d4c99da-6517-46b2-baa7-7e81106d3d34"
FIXTURE_ORDER_ID = "00000000-0000-4000-8000-000000000017"
ARTIFACTS = Path(__file__).resolve().parents[2] / "samples/SupplierMock/microcks"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def http(method: str, url: str, payload: Any = None, content_type: str = "application/json") -> dict[str, Any]:
    headers: dict[str, str] = {}
    data = None
    if payload is not None:
        if isinstance(payload, bytes):
            data = payload
        else:
            data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        response = urllib.request.urlopen(request, timeout=20)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        raw = response.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            body = raw
        return {
            "status": response.status,
            "originHeader": response.headers.get("X-Supplier-Origin"),
            "body": body,
        }


def order_payload(client_id: str, sku: str = "REAL-001", quantity: int = 2) -> dict[str, Any]:
    return {"clientRequestId": client_id, "sku": sku, "quantity": quantity,
            "unitPrice": 100, "currency": "TWD"}


def purchase_payload(client_id: str, product_id: str, **changes: Any) -> dict[str, Any]:
    result = {"clientRequestId": client_id, "productId": product_id,
              "supplierSku": "REAL-001", "quantity": 2, "unitPrice": 100,
              "currency": "TWD", "provider": "direct"}
    result.update(changes)
    return result


def journal() -> list[dict[str, Any]]:
    response = http("GET", SANDBOX + "/sandbox/requests")
    check(response["status"] == 200 and isinstance(response["body"], list),
          "sandbox request journal unavailable")
    return response["body"]


def hits(entries: list[dict[str, Any]], method: str, path: str,
         client_id: str | None = None) -> int:
    return sum(1 for item in entries if item.get("method", "").upper() == method
               and item.get("path") == path
               and (client_id is None or str(item.get("clientRequestId", "")).lower() == client_id.lower()))


def new_entries(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find newly recorded requests even when the bounded journal drops old rows."""
    previous = Counter(json.dumps(item, sort_keys=True) for item in before)
    result = []
    for item in after:
        key = json.dumps(item, sort_keys=True)
        if previous[key]:
            previous[key] -= 1
        else:
            result.append(item)
    return result


def observed(case: dict[str, Any], label: str, response: dict[str, Any]) -> dict[str, Any]:
    case["observations"].append({"label": label, **response})
    return response


def supplier_probe(case: dict[str, Any], label: str, base: str, method: str,
                   path: str, payload: Any, expected_origin: str | None,
                   expected_upstream: bool, client_id: str | None = None,
                   upstream_path: str | None = None) -> dict[str, Any]:
    before = journal()
    target_path = upstream_path or path
    before_count = hits(before, method, target_path, client_id)
    response = observed(case, label, http(method, base + path, payload))
    after = journal()
    after_count = hits(after, method, target_path, client_id)
    delta = hits(new_entries(before, after), method, target_path, client_id)
    case["observations"].append({"label": label + " upstream journal", "method": method,
                                  "path": target_path, "clientRequestId": client_id,
                                  "before": before_count, "after": after_count, "delta": delta,
                                  "matchedAfter": [entry for entry in after
                                                   if entry.get("method", "").upper() == method
                                                   and entry.get("path") == target_path
                                                   and (client_id is None or str(entry.get("clientRequestId", "")).lower() == client_id.lower())]})
    check(delta == (1 if expected_upstream else 0),
          f"{label}: expected upstream delta {int(expected_upstream)}, observed {delta}")
    if expected_origin is not None:
        check(response["status"] == 200, f"{label}: expected 200, got {response['status']}")
        check(isinstance(response["body"], dict) and response["body"].get("origin") == expected_origin,
              f"{label}: expected body origin {expected_origin}")
        if expected_origin == "sandbox" and response["originHeader"] is not None:
            check(response["originHeader"] == "sandbox", f"{label}: unexpected proxy origin header")
        if expected_origin == "wiremock":
            check(response["originHeader"] == "wiremock", f"{label}: missing WireMock origin header")
    return response


def assert_order(response: dict[str, Any], client_id: str, sku: str,
                 quantity: int, supplier_order_id: str | None = None) -> str:
    body = response["body"]
    check(isinstance(body, dict), "supplier order response is not JSON object")
    check(str(body.get("clientRequestId", "")).lower() == client_id.lower(), "supplier client identity changed")
    check(body.get("sku") == sku and body.get("quantity") == quantity, "supplier order payload changed")
    check(float(body.get("unitPrice", -1)) == 100 and body.get("currency") == "TWD",
          "supplier price or currency changed")
    actual_id = str(body.get("supplierOrderId", ""))
    check(bool(actual_id), "supplier order ID missing")
    if supplier_order_id is not None:
        check(actual_id.lower() == supplier_order_id.lower(), "supplier order ID changed")
    return actual_id


def set_wiremock(mode: str) -> None:
    response = http("POST", WIREMOCK_CONTROL + "/control/mode", {"mode": mode})
    check(response["status"] == 200 and response["body"].get("mode") == mode,
          f"WireMock mode {mode} was not applied: {response}")


def set_microcks(mode: str) -> dict[str, Any]:
    artifact = ARTIFACTS / f"supplier-{mode}.yaml"
    check(artifact.is_file(), f"missing checked Microcks artifact: {artifact}")
    boundary = "codex-" + uuid.uuid4().hex
    data = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
            f"filename=\"{artifact.name}\"\r\nContent-Type: application/yaml\r\n\r\n").encode()
    data += artifact.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    upload = http("POST", MICROCKS + "/api/artifact/upload?mainArtifact=true",
                  data, f"multipart/form-data; boundary={boundary}")
    check(200 <= upload["status"] < 300, f"Microcks {mode} import failed: {upload}")
    deadline = time.monotonic() + 20
    while True:
        services = http("GET", MICROCKS + "/api/services?page=0&size=100")
        check(services["status"] == 200 and isinstance(services["body"], list),
              f"Microcks service read-back failed: {services}")
        matched = [item for item in services["body"] if item.get("name") == "Supplier API"
                   and item.get("version") == "1.0.0"]
        if matched:
            return {"mode": mode, "artifact": str(artifact), "upload": upload,
                    "service": matched[0]}
        check(time.monotonic() < deadline, "Microcks Supplier API 1.0.0 was not read back")
        time.sleep(1)


def set_mode(engine: str, mode: str) -> dict[str, Any]:
    if engine == "wiremock":
        set_wiremock(mode)
        return {"engine": engine, "mode": mode,
                "state": http("GET", WIREMOCK_CONTROL + "/control/state")}
    return {"engine": engine, **set_microcks(mode)}


def engine_base(engine: str) -> str:
    return WIREMOCK_NATIVE if engine == "wiremock" else MICROCKS_API


def run_case(results: list[dict[str, Any]], scenario: str, action: Any) -> None:
    case: dict[str, Any] = {"scenario": scenario, "startedAt": utc_now(), "observations": []}
    try:
        action(case)
        case["status"] = "passed"
    except Exception as error:  # Preserve failed evidence and run independent scenarios.
        case["status"] = "failed"
        case["error"] = f"{type(error).__name__}: {error}"
    case["endedAt"] = utc_now()
    results.append(case)
    print(f"{scenario}: {case['status']}", flush=True)


def procurement_cases(results: list[dict[str, Any]]) -> None:
    shared: dict[str, str] = {}

    def p02(case: dict[str, Any]) -> None:
        client_id, product_id = str(uuid.uuid4()), str(uuid.uuid4())
        payload = purchase_payload(client_id, product_id)
        before = journal()
        first = observed(case, "create", http("POST", PROCUREMENT + "/api/procurement/purchase-orders", payload))
        check(first["status"] == 201 and first["body"]["state"] == "Accepted", "P02 initial purchase not accepted")
        replay = observed(case, "replay", http("POST", PROCUREMENT + "/api/procurement/purchase-orders", payload))
        check(replay["status"] == 200 and replay["body"]["id"] == first["body"]["id"], "P02 replay identity differs")
        check(replay["body"].get("supplierOrderId") == first["body"].get("supplierOrderId"),
              "P02 supplier identity differs")
        after = journal()
        count = hits(new_entries(before, after), "POST", "/supplier/orders", client_id)
        case["observations"].append({"label": "supplier POST delta", "clientRequestId": client_id, "delta": count})
        check(count == 1, "P02 generated more than one supplier POST")
        upstream = observed(case, "supplier lookup", http("GET", SANDBOX + f"/supplier/orders/by-client-request/{client_id}"))
        check(upstream["status"] == 200, "P02 supplier lookup missing")
        assert_order(upstream, client_id, "REAL-001", 2, first["body"].get("supplierOrderId"))
        shared.update(client_id=client_id, product_id=product_id, purchase_id=first["body"]["id"])

    def p03(case: dict[str, Any]) -> None:
        check(bool(shared), "P03 requires P02 accepted purchase")
        client_id = shared["client_id"]
        original = observed(case, "stored original", http("GET", PROCUREMENT + f"/api/procurement/purchase-orders/{shared['purchase_id']}"))
        before = journal()
        for label, changes in (("quantity", {"quantity": 3}),
                               ("provider", {"provider": "wiremock"}),
                               ("product", {"productId": str(uuid.uuid4())})):
            response = observed(case, "conflict " + label,
                                http("POST", PROCUREMENT + "/api/procurement/purchase-orders",
                                     purchase_payload(client_id, shared["product_id"], **changes)))
            check(response["status"] == 409 and response["body"].get("code") == "purchase_identity_conflict",
                  f"P03 {label} did not report identity conflict")
        after = journal()
        check(hits(new_entries(before, after), "POST", "/supplier/orders", client_id) == 0,
              "P03 sent a second supplier POST")
        stored = observed(case, "stored after conflicts", http("GET", PROCUREMENT + f"/api/procurement/purchase-orders/{shared['purchase_id']}"))
        check(stored["status"] == 200 and stored["body"] == original["body"], "P03 changed stored purchase")

    def p04(case: dict[str, Any]) -> None:
        client_id, product_id = str(uuid.uuid4()), str(uuid.uuid4())
        control = observed(case, "delay 4000", http("PUT", SANDBOX + "/sandbox/control", {"delayAfterCommitMs": 4000}))
        check(control["status"] == 200 and control["body"].get("delayAfterCommitMs") == 4000, "delay not set")
        before = journal()
        try:
            purchase = observed(case, "unknown submission",
                                http("POST", PROCUREMENT + "/api/procurement/purchase-orders",
                                     purchase_payload(client_id, product_id)))
            check(purchase["status"] == 202 and purchase["body"].get("state") == "SubmissionUnknown",
                  "P04 did not retain unknown outcome")
            supplier = observed(case, "committed supplier lookup",
                                http("GET", SANDBOX + f"/supplier/orders/by-client-request/{client_id}"))
            check(supplier["status"] == 200, "P04 supplier commit missing")
            assert_order(supplier, client_id, "REAL-001", 2)
            reconciled = observed(case, "reconcile by original key",
                                  http("POST", PROCUREMENT + f"/api/procurement/purchase-orders/{purchase['body']['id']}/reconcile"))
            check(reconciled["status"] == 200 and reconciled["body"].get("state") == "Accepted",
                  "P04 reconcile did not recover accepted state")
            check(reconciled["body"].get("supplierOrderId") == supplier["body"].get("supplierOrderId"),
                  "P04 supplier identity changed")
            after = journal()
            added = new_entries(before, after)
            post_count = hits(added, "POST", "/supplier/orders", client_id)
            get_count = hits(added, "GET", f"/supplier/orders/by-client-request/{client_id}", client_id)
            case["observations"].append({"label": "upstream calls", "postDelta": post_count,
                                          "reconcileLookupCount": get_count, "clientRequestId": client_id})
            check(post_count == 1 and get_count >= 2, "P04 retried POST or did not query original supplier key")
        finally:
            reset = observed(case, "delay reset", http("PUT", SANDBOX + "/sandbox/control", {"delayAfterCommitMs": 0}))
            check(reset["status"] == 200 and reset["body"].get("delayAfterCommitMs") == 0, "delay reset failed")

    def p07(case: dict[str, Any]) -> None:
        product_id = str(uuid.uuid4())
        empty = "00000000-0000-0000-0000-000000000000"
        bad = (("empty client ID", purchase_payload(empty, product_id)),
               ("empty product ID", purchase_payload(str(uuid.uuid4()), empty)),
               ("invalid SKU", purchase_payload(str(uuid.uuid4()), product_id, supplierSku="bad sku")),
               ("zero quantity", purchase_payload(str(uuid.uuid4()), product_id, quantity=0)),
               ("negative price", purchase_payload(str(uuid.uuid4()), product_id, unitPrice=-1)),
               ("non-TWD", purchase_payload(str(uuid.uuid4()), product_id, currency="USD")))
        before = journal()
        existing = observed(case, "purchase list before", http("GET", PROCUREMENT + "/api/procurement/purchase-orders"))
        check(existing["status"] == 200, "purchase list unavailable")
        for label, payload in bad:
            response = observed(case, label, http("POST", PROCUREMENT + "/api/procurement/purchase-orders", payload))
            check(response["status"] == 400, f"P07 {label} was not rejected")
            check(response["body"].get("code") in {"invalid_identity", "invalid_sku", "invalid_purchase"},
                  f"P07 {label} returned unexpected error code")
        after = journal()
        post_delta = hits(new_entries(before, after), "POST", "/supplier/orders")
        case["observations"].append({"label": "supplier POST delta", "delta": post_delta})
        check(post_delta == 0, "P07 invalid payload reached supplier")
        listed = observed(case, "purchase list after", http("GET", PROCUREMENT + "/api/procurement/purchase-orders"))
        ids = {str(item.get("identity", {}).get("clientRequestId", "")).lower() for item in listed["body"]}
        check(all(payload["clientRequestId"].lower() not in ids for _, payload in bad),
              "P07 invalid purchase was stored")

    for scenario, action in (("P02", p02), ("P03", p03), ("P04", p04), ("P07", p07)):
        run_case(results, scenario, action)


def sandbox_case(results: list[dict[str, Any]]) -> None:
    def s01(case: dict[str, Any]) -> None:
        client_id = str(uuid.uuid4())
        payload = order_payload(client_id)
        before = journal()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            responses = list(pool.map(lambda _: http("POST", SANDBOX + "/supplier/orders", payload), range(4)))
        for index, response in enumerate(responses):
            observed(case, f"concurrent POST {index + 1}", response)
            check(response["status"] == 200 and response["body"].get("origin") == "sandbox",
                  "S01 concurrent submission failed")
        ids = {assert_order(response, client_id, "REAL-001", 2) for response in responses}
        check(len(ids) == 1, "S01 concurrent POST created differing supplier identities")
        replay = observed(case, "replay", http("POST", SANDBOX + "/supplier/orders", payload))
        check(replay["status"] == 200, "S01 replay failed")
        assert_order(replay, client_id, "REAL-001", 2, next(iter(ids)))
        changed = observed(case, "changed payload", http("POST", SANDBOX + "/supplier/orders",
                                                       order_payload(client_id, quantity=3)))
        check(changed["status"] == 409 and changed["body"].get("code") == "idempotency_conflict",
              "S01 changed payload did not conflict")
        lookup = observed(case, "supplier lookup", http("GET", SANDBOX + f"/supplier/orders/by-client-request/{client_id}"))
        check(lookup["status"] == 200, "S01 stored supplier order missing")
        assert_order(lookup, client_id, "REAL-001", 2, next(iter(ids)))
        after = journal()
        post_delta = hits(new_entries(before, after), "POST", "/supplier/orders", client_id)
        case["observations"].append({"label": "upstream supplier POST journal", "clientRequestId": client_id,
                                      "before": hits(before, "POST", "/supplier/orders", client_id),
                                      "after": hits(after, "POST", "/supplier/orders", client_id), "delta": post_delta})
        check(post_delta == 6, "S01 request journal did not retain all concurrent/replay/conflict calls")
    run_case(results, "S01", s01)


def mock_cases(results: list[dict[str, Any]], engine: str) -> None:
    base = engine_base(engine)
    mock_origin = "wiremock" if engine == "wiremock" else "microcks"

    def m01(case: dict[str, Any]) -> None:
        case["observations"].append({"label": "mode", **set_mode(engine, "hybrid")})
        quote = supplier_probe(case, "fixture quote", base, "GET", "/supplier/catalog/MOCK-001", None,
                               mock_origin, False)
        check(quote["body"].get("sku") == "MOCK-001", "M01 quote SKU changed")

    def m02(case: dict[str, Any]) -> None:
        case["observations"].append({"label": "mode", **set_mode(engine, "hybrid")})
        quote = supplier_probe(case, "real quote", base, "GET", "/supplier/catalog/REAL-001", None,
                               "sandbox", True)
        check(quote["body"].get("sku") == "REAL-001", "M02 quote path changed")
        client_id = str(uuid.uuid4())
        payload = order_payload(client_id)
        order = supplier_probe(case, "real order", base, "POST", "/supplier/orders", payload,
                               "sandbox", True, client_id)
        order_id = assert_order(order, client_id, "REAL-001", 2)
        lookup = supplier_probe(case, "real lookup", base, "GET",
                                f"/supplier/orders/by-client-request/{client_id}", None,
                                "sandbox", True, client_id)
        assert_order(lookup, client_id, "REAL-001", 2, order_id)

    def m03(case: dict[str, Any]) -> None:
        case["observations"].append({"label": "mode", **set_mode(engine, "hybrid")})
        fixture = order_payload(FIXTURE_ID, "MOCK-001")
        order = supplier_probe(case, "fixture order", base, "POST", "/supplier/orders", fixture,
                               mock_origin, False, FIXTURE_ID)
        assert_order(order, FIXTURE_ID, "MOCK-001", 2, FIXTURE_ORDER_ID)
        lookup = supplier_probe(case, "fixture lookup", base, "GET",
                                f"/supplier/orders/by-client-request/{FIXTURE_ID}", None,
                                mock_origin, False, FIXTURE_ID)
        assert_order(lookup, FIXTURE_ID, "MOCK-001", 2, FIXTURE_ORDER_ID)

    def m04(case: dict[str, Any]) -> None:
        case["observations"].append({"label": "mode", **set_mode(engine, "hybrid")})
        client_id = str(uuid.uuid4())
        payload = order_payload(client_id)
        order = supplier_probe(case, "unmatched known POST", base, "POST", "/supplier/orders", payload,
                               "sandbox", True, client_id)
        order_id = assert_order(order, client_id, "REAL-001", 2)
        lookup = supplier_probe(case, "unmatched known GET", base, "GET",
                                f"/supplier/orders/by-client-request/{client_id}", None,
                                "sandbox", True, client_id)
        assert_order(lookup, client_id, "REAL-001", 2, order_id)

    def m05(case: dict[str, Any]) -> None:
        case["observations"].append({"label": "mode", **set_mode(engine, "proxy")})
        quote = supplier_probe(case, "formerly mocked quote", base, "GET", "/supplier/catalog/MOCK-001",
                               None, "sandbox", True)
        check(quote["body"].get("sku") == "MOCK-001", "M05 quote SKU changed")
        client_id = str(uuid.uuid4())
        order = supplier_probe(case, "proxy order", base, "POST", "/supplier/orders",
                               order_payload(client_id, "MOCK-001"), "sandbox", True, client_id)
        order_id = assert_order(order, client_id, "MOCK-001", 2)
        lookup = supplier_probe(case, "proxy lookup", base, "GET",
                                f"/supplier/orders/by-client-request/{client_id}", None,
                                "sandbox", True, client_id)
        assert_order(lookup, client_id, "MOCK-001", 2, order_id)

    def m06(case: dict[str, Any]) -> None:
        case["observations"].append({"label": "mode", **set_mode(engine, "mock")})
        miss = supplier_probe(case, "mock-only unmatched known quote", base, "GET",
                              "/supplier/catalog/REAL-001", None, None, False)
        check(miss["originHeader"] != "sandbox" and
              (not isinstance(miss["body"], dict) or miss["body"].get("origin") != "sandbox"),
              "M06 mock-only response claims sandbox origin")
        case["observations"].append({"label": "mock miss classification", "status": miss["status"],
                                      "body": miss["body"]})
        unknown = supplier_probe(case, "mock-only unknown route", base, "GET",
                                 "/supplier/unknown/" + uuid.uuid4().hex, None, None, False)
        check(unknown["originHeader"] != "sandbox", "M06 unknown route reached sandbox")
        case["observations"].append({"label": "unknown route classification",
                                      "status": unknown["status"], "body": unknown["body"]})

    for scenario, action in (("M01", m01), ("M02", m02), ("M03", m03),
                             ("M04", m04), ("M05", m05), ("M06", m06)):
        run_case(results, f"{scenario}-{engine}", action)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path("artifacts/procurement-lab/http-contracts.json"))
    args = parser.parse_args()
    results: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {"workflow": "2026-09-26-procurement-supplier-lab",
                                "startedAt": utc_now(), "scenarioResults": results}
    try:
        procurement_cases(results)
        sandbox_case(results)
        for engine in ("wiremock", "microcks"):
            mock_cases(results, engine)
    finally:
        cleanup: list[dict[str, Any]] = []
        for label, operation in (("sandbox delay", lambda: http("PUT", SANDBOX + "/sandbox/control",
                                                            {"delayAfterCommitMs": 0})),
                                 ("WireMock hybrid", lambda: set_mode("wiremock", "hybrid")),
                                 ("Microcks hybrid", lambda: set_mode("microcks", "hybrid"))):
            try:
                outcome = operation()
                if label == "sandbox delay":
                    check(outcome["status"] == 200 and outcome["body"].get("delayAfterCommitMs") == 0,
                          "sandbox delay reset was not confirmed")
                cleanup.append({"label": label, "status": "passed", "outcome": outcome})
            except Exception as error:
                cleanup.append({"label": label, "status": "failed", "error": str(error)})
        evidence["cleanup"] = cleanup
        evidence["endedAt"] = utc_now()
        evidence["passed"] = all(item["status"] == "passed" for item in results + cleanup)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Evidence: {args.output}", flush=True)
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
