# Specs Portability Notes

`.dev/specs/` 是 domain truth 與 test truth 的容器，不是可直接套用的內容樣板集合。

## 可保留

- `SPEC-GUIDE.MD`
- `SPEC-ORGANIZATION-GUIDE.MD`
- `tests/README.MD`
- `tests/TEST-SPEC-GUIDE.MD`

## 應重寫

- `domains/<domain>/...`
- `tests/<domain>/...`
- `tests/cross-domain/...`
- `tests/e2e/...`

## 原則

- 保留 taxonomy 與命名規則
- 重寫 bounded context、aggregate、use case、scenario 與 assertion truth
