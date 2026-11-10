# 文獻回顧 v1：偏差探針的可見性邊界

> 日期：2026-11-10。狀態：文獻庫第一版。2026-11-10 補充：已初讀 Lipsitch、Armstrong & Kolesár、Scavino 的相關段落，並核對 Imbens & Manski 的定義，見 [reading_notes_2026-11-10.md](reading_notes_2026-11-10.md)。
> 文獻庫：[literature/library.csv](literature/library.csv)（83 筆，含查證狀態與每篇 3 行筆記）。
> 參考文獻：[../paper/references.bib](../paper/references.bib)（77 筆，只收已查證者，可直接匯入 Zotero）。

## 1. 結論先講

1. 文獻庫從上一版的 32 篇擴充到 83 篇，其中 78 篇已查證可引用（Lipsitch 2010 已補齊），5 篇只查到部分書目資料，暫不放進參考文獻。
2. 文獻給了本專案四個現成的理論錨點，讓「探針看得到／看不到」可以用既有語言正式定義，不必自己發明：
   - **(A) 雜訊的可學性與規範自由**：Pauli 雜訊有一部分在原理上學不到（Chen et al. 2023），GST 有 gauge 自由（Nielsen et al. 2021）。
   - **(B) 部分識別**：偏差無法完全識別時，決策差距只被識別到一個集合（Imbens & Manski 2004；Tamer 2010）。
   - **(C) 負對照**：原文條件是 U-comparability，也就是負對照與目標的未觀測共同原因集合相同，且不受暴露影響（Lipsitch et al. 2010）。用在探針上只能當類比。
   - **(D) 考慮偏差的信賴區間**：用偏差上界調整臨界值以保證覆蓋率（Armstrong & Kolesár 2020）。
3. 這四個錨點促成計畫的修正（第 5 節）。最重要的是：Lemma 1 要定義在「(理想差距, 雜訊) 的組合」上，不能只定義在雜訊上。v0.2 的寫法有漏洞。
4. 在本次讀到的摘要範圍內，沒有看到有人把「探針可見性」對「會翻轉決策的差異偏差」在同一預算下畫成邊界。這不代表沒有人做過，精讀後要再確認（第 6 節）。

## 2. 查證方法與限制

- 每一篇都用網路搜尋找到書目紀錄，再讀取一個可公開取得的頁面核對：arXiv 摘要頁、DOAJ、Crossref、RePEc、出版社頁或機構典藏。核對到哪些欄位，記在 `library.csv` 的 `source_checked` 欄。
- 狀態分四類：
  - `verified`：作者、期刊、卷、DOI（若有）都對到線上紀錄，共 45 篇。部分 APS 與 Quantum 期刊的卷號和文章號是從 DOI 讀出的，已在 `source_checked` 註明。
  - `verified (previous project)`：沿用上一版已查證的 31 篇。
  - `verified-preprint`：只有 arXiv 版本，共 1 篇。
  - `partial`：缺卷期或 DOI，共 6 篇。這 6 篇不放進 `references.bib`。
- **限制一：沒有讀任何全文。** 筆記的依據記在 `note_basis` 欄：
  - 「摘要（本次讀取）」：本次讀過摘要或摘要級的介紹。
  - 「上一版專案」：沿用上一版的判斷。
  - 「背景知識，未讀摘要，待確認」：筆記只能當線索。
  
  因此所有新文獻的「能不能引它的數字」目前都是「否」，要等精讀後再更新。
- **限制二：自動 API 無法使用。** Crossref 和 arXiv API 都被工作環境的網路限制擋住，只能逐篇以網頁核對。所以沒有批次比對全部 DOI，只有逐篇比對。
- 上一版 `bultrini2021` 引的是 arXiv 版。本次查到它已在 *Quantum* 7, 1034 (2023) 正式發表，改用 `bultrini2023`。
- 規範 v2 第二部分第 6 條列為未查證的文獻，本次結果如下：

| 項目 | 結果 |
|---|---|
| TREX twirled readout | 已查證：van den Berg, Minev & Temme, PRA 105, 032620 (2022) |
| Zhou et al. 2020 (PRX) | 已查證 PRX 10, 021067；使用者已確認就是這篇 |
| Kim & Nelson | 已查證：Handbooks in OR&MS 13, 501–534 (2006) |
| OCBA (Chen et al.) | 已查證：DEDS 10, 251–270 (2000) |
| Kaufmann et al. 2016 | 已查證：JMLR 17, 1–42 |

## 3. 文獻地圖（六類）

| 類別 | 篇數 | 對本專案最關鍵的幾篇 |
|---|---|---|
| QEM 方法 | 23 | Temme 2017、Giurgica-Tiron 2020（P1 folding）；Wallman & Emerson 2016（P3 RC）；Czarnik 2021、Lowe 2021（P2 Clifford）；Bonet-Monroig 2018（對稱性檢查） |
| 統計決策 | 20 | Imbens & Manski 2004、Tamer 2010（部分識別）；Armstrong & Kolesár 2020（偏差感知區間）；Lipsitch 2010（負對照）；Kaufmann 2016、Chen 2000（預算分配） |
| 評比與特性化 | 18 | Chen 2023（可學性）、Nielsen 2021（GST gauge）；Proctor 2022（mirror circuits）；Sarovar 2020（crosstalk 偵測）；Kueng 2016、Sanders 2016（coherent 誤差與平均指標） |
| 硬體實驗 | 9 | Hashim 2021（RC 硬體）；Kim 2023 Nat Phys（大規模 ZNE）；Sagastizabal 2019（對稱性硬體） |
| 讀出 | 7 | van den Berg 2022（TREX）；Maciejewski 2021（讀出 crosstalk）；Chen 2019（量測器斷層掃描） |
| QEM 極限 | 6 | Takagi 2022/2023、Quek 2024、Tsubouchi 2023 |

## 4. 從文獻得到的研究方向錨點

### (A) 可學性與規範自由：讓「原理上盲」有物理內容
- Chen et al. (2023) 的摘要指出：在 Clifford 閘上，Pauli 雜訊的可學部分對應 pattern transfer graph 的 cycle space，cut space 部分「完全學不到」。Nielsen et al. (2021) 也把 gauge 自由當成 GST 的核心議題。
- **借用方式**：探針的資料只能識別雜訊中可學的部分。如果某個決策的差異偏差對「不可學分量」有敏感度，而且這個敏感度大到足以抵消 Δ，那麼任何探針組合都看不到。這是「原理上盲」的第一類實例。它來自雜訊本身的不可識別性，而不是探針設計得不好。
- **可證偽的預測**（Part 1 要推導，現在只是假設）：「差異偏差 β 對 cut-space 分量的投影」可以作為盲的判準。
- 精讀優先順序：第 1。

### (B) 部分識別：讓「看得到／看不到」有統計定義
- 把參數寫成 (Δ, e)，其中 Δ 是理想差距，e 是雜訊。資料（目標加探針）只能把 (Δ, e) 限制在一個「識別集合」裡。
- **盲的定義**：識別集合中同時有 Δ > 0 和 Δ ≤ 0 的點。探針的作用就是加入對 e 的限制，把識別集合縮小。
- 這個定義比 v0.2 的 Lemma 1 正確。v0.2 寫成「存在 e₁、e₂ 使觀測同分布但 sign(Δ+β) 不同」，但觀測分布本身就決定了 Δ+β 的分布，所以那個條件永遠不會成立。真正要問的是：能否把 Δ+β 和 Δ 分開，也就是在 Δ 未知時能否識別 β。
- Imbens & Manski (2004) 提供對識別集合做信賴區間的方法，可以直接用在「偏差感知認證」上。

### (C) 負對照：每個探針格子的有效條件
- 負對照的邏輯是：找一個「真實效果已知為零」的對照。若對照顯示非零，就表示有偏差。
- **2026-11-10 更正**：原文的條件叫 U-comparability。它的意思是負對照與目標的「未觀測共同原因集合」相同或盡量相同，而且負對照不受暴露影響。原文沒有「共享偏差機制」這種說法，前一版是我的轉述，不準確。原文措辭見 reading_notes_2026-11-10.md 第 1 節。套到量子探針只能當類比。
- **對應到本專案**：
  - P2 Clifford 孿生就是負對照，它的理想值已知；
  - P1 folding 和 P3 twirl 是「改變偏差、但不改變理想值」的操作，可以看成另一種對照；
  - P5 對稱性檢查用的是「理想值已知為零的分量」。
- 每個探針×誤差結構格子的 ✓/✗ 預測，可以用一個我們自己定義、類比於 U-comparability 的量子版條件統一表述（見計畫 v0.4 第 3 節第 3 點）。
- Rosenbaum (1987) 與 VanderWeele & Ding (2017) 的敏感度分析，提供「偏差要多大才會推翻結論」的報告格式。本專案可以對每個決策報告「翻轉所需的最小差異偏差」。

### (D) 偏差感知區間：認證要有覆蓋率保證
- Armstrong & Kolesár (2020) 的摘要說：當估計量可能有偏差時，用偏差上界調整臨界值，就能保證覆蓋率。
- 本專案 v0.2 的「偏差感知認證」（差距的 CI 下界 > 與探針相容的最大偏差 B）正是這個形式。現在可以引用它，並繼承覆蓋率論證，不必從頭證明。

### (E) 預算分配：Proposition 2 的語言
- 最佳臂辨識（Kaufmann et al. 2016；Garivier & Kaufmann 2016）與 OCBA（Chen et al. 2000）處理「有限樣本怎麼分給候選」。本專案多了一個維度：分給探針還是分給目標。
- 這是規範 v2 第 11 條 [宜] 的內容，現在有查證過的出處可以用。

### 其他直接影響探針設計的發現
- **Coherent 誤差藏在平均值裡**：Kueng et al. (2016)、Sanders et al. (2016) 指出平均保真度無法約束 coherent 誤差的最壞情況。這支持 E2 是關鍵結構，也支持 P3（RC 對比）有存在的理由。
- **Crosstalk 可以用條件相依性偵測**：Sarovar et al. (2020) 用觀測機率的條件相依性偵測 crosstalk。這可以作為 E3（ZZ）探針的設計參考。v0.2 對 E3 的預測最不確定，這篇可以幫忙收斂。
- **對稱性檢查是現成的零成本探針**：Bonet-Monroig et al. (2018) 有零成本後處理版本。它對保持對稱的誤差原理上盲，是「不變性造成盲點」最乾淨的例子。建議加為 P5（第 5 節）。
- **相關讀出在真實裝置上可能存在**：Chen et al. (2019) 在 IBM 5 量子位元裝置上觀察到疑似量測 crosstalk，並建議聯合建模（他人硬體證據，只讀摘要）。這支持 Part 4 硬體實驗的動機，但不能當成本專案的證據。

## 5. 對研究計畫 v0.2 的修正建議（已寫入 v0.3）

1. **Lemma 1 改寫成部分識別形式**（錨點 B）。原本的寫法在數學上不成立，見 4(B)。v0.4 再依 Imbens & Manski 原文改成 Δ = f(P, e) 的形式。
2. **新增 P5 對稱性檢查**：零額外 shots，作為「零成本探針」的基準。若 Part 1 的檢定力分析顯示範圍太大，依凍結的砍範圍規則處理。
3. **探針有效條件用自訂、類比於 U-comparability 的量子版條件表述**（錨點 C）；偏差感知認證採用 honest CI 的形式（錨點 D），但覆蓋率需要自己補推導。
4. **新增理論目標**：可學性判準（錨點 A），作為「原理上盲」的第一類實例。它和 Takagi、Quek、Tsubouchi 的估計器層下界並列，回答口試第 1 題時，可以說明本專案在決策層補了什麼。

## 6. 新穎性：目前能說和不能說的

- **能說**：在本次讀到的摘要中，前人分別處理了以下幾件事：
  - 雜訊能否學到（Chen 2023）；
  - crosstalk 能否偵測（Sarovar 2020）；
  - 緩解在固定預算下準不準（Bultrini 2023、Cirstoiu 2023）；
  - 緩解的成本下界（Takagi、Quek、Tsubouchi）。
  
  沒有看到有人把這些接到「決策會不會因差異偏差翻轉、執行時能否在同一預算內看到」。
- **不能說**：「沒有人做過」。原因有三：
  - 只讀了摘要；
  - 有 2 篇 2026 年的預印本（Scavino Alfaro；Köster & Mauerer）和本專案最接近，必須精讀比較；
  - 統計學中「有偏差臂的最佳臂辨識」可能已有直接相關的結果，本次沒有專門搜尋。

## 7. 精讀清單（建議順序）

| 順序 | 文獻 | 要回答的問題 |
|---|---|---|
| 1 | Chen et al. 2023（可學性） | cut space 的定義；能否把差異偏差投影到 cut space |
| 2 | Imbens & Manski 2004 | 識別集合 CI 的構造與條件 |
| 3 | Armstrong & Kolesár 2020 | 偏差上界如何進入臨界值；能否直接套用到差距 |
| 4 | Lipsitch et al. 2010 | 負對照有效條件的原文陳述 |
| 5 | Scavino Alfaro 2026 | 和本專案的差異（決策風險） |
| 6 | Köster & Mauerer 2026 | ZNE 的人為改善是否等於 P1 的盲點 |
| 7 | Nielsen et al. 2021（GST） | gauge 自由對探針的意義 |
| 8 | Wallman & Emerson 2016 | twirl 不變性的精確條件（P3 盲點） |
| 9 | Proctor et al. 2022（mirror） | mirror 結構能否作為 P1/P2 的實作 |
| 10 | Sarovar et al. 2020 | 條件相依性檢定能否改成 E3 探針 |
| 11 | Czarnik 2021、Lowe 2021 | Clifford 訓練電路何時不具代表性（P2 失效） |
| 12 | Bonet-Monroig 2018 | 零成本對稱性檢查的確切形式（P5） |
| 13 | Kueng 2016 | coherent 誤差的平方根關係，可否用在 E2 敏感度 |
| 14 | Takagi 2022、Tsubouchi 2023 | 下界與本專案 shot 下界的關係 |
| 15 | Kaufmann 2016 | 樣本複雜度下界的形式，能否用在 Proposition 2 |

## 8. 待補
- 5 篇 partial 需要補卷期或 DOI：Le Cam 1973、Kim 2023 (Nat Phys)、Russo 2023、Gambetta 2012、Magesan 2011。
- 尚未搜尋的主題：有偏差臂的最佳臂辨識（biased / misspecified bandits）；QEM 的模型不確定性或 robust 推論；cluster bootstrap 與 mixed-effects 的原始出處（規範 v2 第 2 條）。
- 目標：Part 1 結束前達到 90 篇以上，並完成前 15 篇精讀，更新「能不能引數字」欄。
