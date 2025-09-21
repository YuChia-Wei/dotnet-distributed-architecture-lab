# 任務：[功能名稱]

**輸入**：來自 `/specs/[###-功能名稱]/` 的設計文件
**先決條件**：plan.md (必要)、research.md、data-model.md、contracts/

## 執行流程 (主要)
```
1. 從功能目錄載入 plan.md
   → 如果找不到：錯誤 "找不到實作計畫"
   → 提取：技術堆疊、函式庫、結構
2. 載入可選的設計文件：
   → data-model.md：提取實體 → 模型任務
   → contracts/：每個檔案 → 合約測試任務
   → research.md：提取決策 → 設定任務
3. 按類別產生任務：
   → 設定：專案初始化、相依性、程式碼風格檢查
   → 測試：合約測試、整合測試
   → 核心：模型、服務、CLI 指令
   → 整合：資料庫、中介軟體、日誌記錄
   → 優化：單元測試、效能、文件
4. 套用任務規則：
   → 不同檔案 = 標記 [P] 表示可並行
   → 相同檔案 = 循序 (無 [P])
   → 測試先於實作 (TDD)
5. 循序編號任務 (T001, T002...)
6. 產生相依關係圖
7. 建立並行執行範例
8. 驗證任務完整性：
   → 所有合約都有測試嗎？
   → 所有實體都有模型嗎？
   → 所有端點都已實作嗎？
9. 返回：成功 (任務已準備好執行)
```

## 格式：`[ID] [P?] 描述`
- **[P]**：可以並行執行 (不同檔案，無相依性)
- 在描述中包含確切的檔案路徑

## 路徑慣例
- **單一專案**：`src/`、`tests/` 位於儲存庫根目錄
- **Web 應用程式**：`backend/src/`、`frontend/src/`
- **行動裝置**：`api/src/`、`ios/src/` 或 `android/src/`
- 下方顯示的路徑假設為單一專案 - 根據 plan.md 結構進行調整

## 階段 3.1：設定
- [ ] T001 根據實作計畫建立專案結構
- [ ] T002 使用 [framework] 相依性初始化 [language] 專案
- [ ] T003 [P] 設定程式碼風格檢查和格式化工具

## 階段 3.2：測試優先 (TDD) ⚠️ 必須在 3.3 之前完成
**關鍵：這些測試必須在任何實作之前撰寫並且必須失敗**
- [ ] T004 [P] 在 tests/contract/test_users_post.py 中進行 POST /api/users 的合約測試
- [ ] T005 [P] 在 tests/contract/test_users_get.py 中進行 GET /api/users/{id} 的合約測試
- [ ] T006 [P] 在 tests/integration/test_registration.py 中進行使用者註冊的整合測試
- [ ] T007 [P] 在 tests/integration/test_auth.py 中進行驗證流程的整合測試

## 階段 3.3：核心實作 (僅在測試失敗後)
- [ ] T008 [P] src/models/user.py 中的使用者模型
- [ ] T009 [P] src/services/user_service.py 中的 UserService CRUD
- [ ] T010 [P] src/cli/user_commands.py 中的 CLI --create-user
- [ ] T011 POST /api/users 端點
- [ ] T012 GET /api/users/{id} 端點
- [ ] T013 輸入驗證
- [ ] T014 錯誤處理和日誌記錄

## 階段 3.4：整合
- [ ] T015 將 UserService 連接到資料庫
- [ ] T016 驗證中介軟體
- [ ] T017 請求/回應日誌記錄
- [ ] T018 CORS 和安全性標頭

## 階段 3.5：優化
- [ ] T019 [P] 在 tests/unit/test_validation.py 中進行驗證的單元測試
- [ ] T020 效能測試 (<200ms)
- [ ] T021 [P] 更新 docs/api.md
- [ ] T022 移除重複
- [ ] T023 執行 manual-testing.md

## 相依性
- 測試 (T004-T007) 先於實作 (T008-T014)
- T008 封鎖 T009、T015
- T016 封鎖 T018
- 實作先於優化 (T019-T023)

## 並行範例
```
# 一起啟動 T004-T007：
任務："在 tests/contract/test_users_post.py 中進行 POST /api/users 的合約測試"
任務："在 tests/contract/test_users_get.py 中進行 GET /api/users/{id} 的合約測試"
任務："在 tests/integration/test_registration.py 中進行註冊的整合測試"
任務："在 tests/integration/test_auth.py 中進行驗證的整合測試"
```

## 備註
- [P] 任務 = 不同檔案，無相依性
- 在實作前驗證測試失敗
- 每個任務後提交
- 避免：模糊的任務、相同檔案衝突

## 任務產生規則
*在 main() 執行期間套用*

1. **從合約**：
   - 每個合約檔案 → 合約測試任務 [P]
   - 每個端點 → 實作任務
   
2. **從資料模型**：
   - 每個實體 → 模型建立任務 [P]
   - 關聯 → 服務層任務
   
3. **從使用者故事**：
   - 每個故事 → 整合測試 [P]
   - 快速入門情境 → 驗證任務

4. **排序**：
   - 設定 → 測試 → 模型 → 服務 → 端點 → 優化
   - 相依性會阻礙並行執行

## 驗證檢查清單
*閘道：由 main() 在返回前檢查*

- [ ] 所有合約都有對應的測試
- [ ] 所有實體都有模型任務
- [ ] 所有測試都在實作之前
- [ ] 並行任務真正獨立
- [ ] 每個任務都指定確切的檔案路徑
- [ ] 沒有任務會修改與另一個 [P] 任務相同的檔案
