# 20 篇文獻盤點：第一步（2026-11-10，Claude 草稿，待使用者確認挑選）

> 範圍：只從 library.csv 中 78 篇已查證文獻挑選。
> 閱讀深度依實際情況標示：
> - 「相關段落」：讀了原文中與本專案有關的段落。
> - 「全文（摘錄式）」：讀取工具掃過全文並摘錄，不等於逐字精讀。
> - 「摘要」：只讀摘要或摘要級頁面。
>
> 沒有任何一篇是逐字讀完全文的。Chen 2023 與 Imbens & Manski 的全文由使用者精讀中。
> 疑點欄只寫讀到的內容。「作者自承」表示原文明說的限制；「未見」表示在讀過的範圍內沒有看到，不等於原文沒有。

## 挑選標準
1. 直接支撐本專案的理論定義：可識別性、部分識別、偏差感知區間、負對照。
2. 每個探針（P1、P2、P3、P5，以及讀出 P4）的方法來源，因為要寫「它在什麼條件下失效」。
3. 最接近的競爭或對照研究，因為相關研究比較表必須逐格可查證。
4. 口試第 1 題必須回應的 QEM 極限文獻。

## 盤點表

| # | 篇名（作者＋年） | 類別 | 閱讀深度 | 疑點 | 可引用點 | 關係 |
|---|---|---|---|---|---|---|
| 1 | Chen et al. 2023, The learnability of Pauli noise | 評比與特性化 | 摘要（使用者精讀全文中） | 結果針對 Clifford 閘上的 Pauli 雜訊；摘要未說明能否推到非 Clifford 目標或 coherent 雜訊。摘要提到在完美 SPAM 假設下得到非物理結果，改成給出 SPAM 雜訊下界 | 可學部分 = pattern transfer graph 的 cycle space，不可學 = cut space（定理條件待全文確認） | 支撐 |
| 2 | Nielsen et al. 2021, Gate set tomography | 評比與特性化 | 摘要 | 摘要只說涵蓋 gauge 自由與規範固定；gauge 自由如何影響可觀測量與決策量，未讀，無法判斷 | gauge 自由的存在與 GST 的自洽特性化框架（章節待讀） | 支撐 |
| 3 | Imbens & Manski 2004 | 統計決策 | 相關段落（第 1–3 節） | 原文未正式定義 partially identified（指向 Manski 2003）；𝒜 是事先給定的集合；作者自承最簡版 CI 的覆蓋率不隨識別區域寬度一致收斂，因此提出修正版 | θ = f(P, A)；識別區域 {f(P, A′) : A′ ∈ 𝒜}；覆蓋真值而非整個區域的 CI | 支撐 |
| 4 | Armstrong & Kolesár 2020 | 統計決策 | 相關段落（第 1–2 節） | 最壞偏差來自先驗函數類別 F(M)，需要已知 M；設定是非參數回歸中的單一純量參數 | 區間 = 估計值 ± cv₁₋α(t)·se，cv 是 \|N(t,1)\| 的分位數；在參數空間上一致覆蓋 | 支撐 |
| 5 | Lipsitch et al. 2010 | 統計決策 | 相關段落（負對照選擇一節） | 條件是程度性的（"To the extent that … overlaps"、"as nearly identical as possible"），未見量化檢驗方法；設定是觀察性流行病學 | U-comparable 的原文定義；負對照不受暴露影響的要求 | 支撐（類比） |
| 6 | Takagi et al. 2022 | QEM 極限 | 摘要 | 摘要說界適用於「一般類別」的協定，但沒有定義該類別；只處理估計誤差與抽樣成本，不涉及決策 | 局部去極化分層電路中，達到固定精度的抽樣成本隨深度指數成長；局部 dephasing 下 PEC 在一大類策略中最優 | 對照（估計器層） |
| 7 | Quek et al. 2024 | QEM 極限 | 摘要級（arXiv HTML 前段） | 作者自承：最壞情況界；困難電路高度糾纏，主要構造用全連接；非 unital 情形用 2-design 簡化模型；不排除小雜訊下 QEM 有用；典型情況留待研究 | 區分 weak／strong mitigation；涵蓋 VD、CDR、ZNE、PEC；局部去極化下樣本成本隨量子位元數與深度超多項式成長（最壞情況） | 對照（估計器層） |
| 8 | Scavino Alfaro 2026, Certified Finite-Shot Operating Windows for VD and SV（2026-11-10 換入，取代 Tsubouchi 2023） | 評比與特性化 | 全文（摘錄式） | 認證主要針對抽樣誤差；偏差用局部一階展開處理，原文："The noisy state is assumed to admit the first-order expansion in Equation (4)"；偏差係數依賴理想態、可觀測量與雜訊模型；比較的是估計量 MSE，不是決策；未見通用的執行時模型誤設偵測。作者自承："The hardware layer is qualitative and budget-limited"，嚴格的全例驗證準則在一個 Level 1 族中未達成 | SV 結果明說報告 "residual undetectable-sector bias"；VD 分母可信的樣本量門檻；兩方法比較的選擇三分法 | 競爭（與 P5 盲點、「認證」直接相關；與 #9 同一作者系列） |
| 9 | Scavino 2026, Decision Kernels | 評比與特性化 | 全文（摘錄式） | 據我們所讀，未說明 â_m 如何取得；可識別性條件是局部的；θ 的內容未明確；硬體決策準則未達成；作者自列未來工作含序列分配、停止規則、BAI 型保證 | 決策只依差距；common-mode 被對比映射 L 消去；Corollary C.1 的條件原文 | 競爭（最接近） |
| 10 | Köster & Mauerer 2026 | 評比與特性化 | 全文（摘錄式） | 作者自承：硬體證據只有一台裝置、一個電路族；模擬假設理想去極化；W_neg 沒有正式門檻，只在研究的電路上驗證；起始深度與雜訊水準依裝置而異 | 訊號落在 floor 時 Richardson ZNE 退化為固定縮放 Ê(0) = (15/8)E(λ₁) − (7/8)f；W_neg 不需理想值；用 garbage-folding 當負對照 | 競爭／對照（現成的執行時診斷，P1 的近親） |
| 11 | Bultrini et al. 2023 | 評比與特性化 | 摘要 | 只比較估計準確度，未評估決策；雜訊模型是離子阱模型的模擬 | 各方法表現強烈依賴 shot 預算；UNITED 在最大預算下最準 | 對照 |
| 12 | Cirstoiu et al. 2023 | 評比與特性化 | 摘要 | 期刊頁未說明是否計入 shot 或資源成本；「何時有益」的建議如何驗證，未見 | 體積式評比方法與 Qermit；報告中位數與最差表現 | 對照 |
| 13 | Giurgica-Tiron et al. 2020 | QEM 方法 | 摘要＋相關段落 | 作者自承：folding 可能無法放大系統性與 coherent 誤差（逆閘會抵消）；不適合放大 SPAM；部分推導只對去極化雜訊與奇數倍成立；外推值可能超出物理界 | 上述限制的原文；unitary folding 的定義 | 支撐（P1 盲點的原始出處） |
| 14 | Czarnik et al. 2021 | QEM 方法 | 摘要 | 摘要未說明 Clifford 訓練資料何時不能代表非 Clifford 目標；主要示範只有一個基態能量問題 | 近 Clifford 訓練電路加線性擬合的方法定義；16 量子位元硬體上誤差降一個數量級（他人硬體證據） | 支撐（P2） |
| 15 | Wallman & Emerson 2016 | QEM 方法 | 摘要＋相關段落 | 作者自承：Theorem 1 需要 easy gates 的雜訊與閘無關；一般雜訊只「預期」能近似隨機化，完整證明留作開放問題；閘相依誤差的額外誤差界不緊 | 在定理條件下，RC 把雜訊轉成隨機 Pauli 誤差 | 支撐（P3 原理） |
| 16 | Hashim et al. 2021 | 硬體實驗 | 摘要 | 摘要未陳述限制；示範只有 4 量子位元 QFT 與隨機電路 | RC 在超導硬體上改善表現；cycle benchmarking 錯誤率可預測演算法表現（他人硬體證據） | 支撐 |
| 17 | Bonet-Monroig et al. 2018 | QEM 方法 | 摘要 | 只在 H₂ 模擬中示範；摘要未說明對「保持對稱的誤差」的效果（這是本專案要推導的，不是原文說的） | 量測守恆對稱性的緩解方法，含零成本後處理版本；H₂ 解離曲線誤差最多降一個數量級（模擬） | 支撐（P5） |
| 18 | Proctor et al. 2022, mirror RB | 評比與特性化 | 摘要 | 基準對象是 Clifford 閘；量的是層錯誤率，不是特定電路對的差異偏差 | mirror circuits 可估計多量子位元層錯誤並偵測 crosstalk；模擬到 225 量子位元、硬體到 16 量子位元 | 支撐（P1／P2 實作） |
| 19 | Maciejewski et al. 2021 | 讀出 | 摘要 | 作者自承：只校正邊際分布；殘差誤差只給上界；假設相關的局部性不太高；QAOA 結果只有數值 | k-local 讀出 crosstalk 用 O(k2^k log N) 個電路特性化；量測相關和實體佈局不一致（IBM 15 量子位元、Rigetti 23 量子位元） | 支撐（E5 與 Part 4 硬體動機） |
| 20 | Sarovar et al. 2020 | 評比與特性化 | 摘要 | 摘要只談偵測與定位 crosstalk，未談對決策的影響，也未談偵測成本與預算 | crosstalk 的嚴格操作定義；用觀測機率的條件相依性偵測 | 支撐／對照（E3 探針） |

各類篇數：統計決策 3、評比與特性化 9（含 3 篇競爭）、QEM 極限 2、QEM 方法 4、硬體實驗 1、讀出 1，合計 20 篇。

**計數規則（使用者 2026-11-10 決定）**：第二步計算「出現 3 次以上的共通痛點」時，同一作者的系列作合併計為 1 個來源。#8 與 #9（Scavino／Scavino Alfaro）合併計 1。

## 被排除的接近篇目與理由

| 排除 | 接近的入選篇 | 理由 |
|---|---|---|
| Tamer 2010 | Imbens & Manski 2004 | 兩篇都提供識別集合語言，Tamer 是綜述；本專案直接套用的是 I&M 的 θ = f(P, A) 形式 |
| Takagi, Tajima & Gu 2023 | Takagi et al. 2022 | 同一團隊的下界系列；口試回應只需要一篇代表，另有 Quek 補不同角度 |
| Tsubouchi et al. 2023（原入選，2026-11-10 換出） | Takagi 2022、Quek 2024 | 口試第 1 題有 Takagi、Quek 即可；換入的 Certified Operating Windows 同時涉及「認證」與 P5 的不可偵測殘差偏差，對本專案更直接 |
| Scavino 2026 PEC/CDR windows（2606.21686） | Czarnik 2021、#8／#9 | 只進 library。可支持 P2 失效條件（仿射響應），但與 #8／#9 同一作者系列，計數時本來就會合併 |
| Köster & Mauerer 2026, Claim against Measurement（2605.29872） | Köster & Mauerer 2026（#10） | 只進 library。它是評估方法學的審查，不是診斷方法；可在痛點分析中作為佐證引用 |
| Temme et al. 2017 | Giurgica-Tiron 2020 | Temme 是 ZNE 原始出處，但 P1 的盲點（coherent 誤差不被 folding 放大）原文寫在 Giurgica-Tiron |
| Lowe 2021、Strikis 2021 | Czarnik 2021 | 都是 Clifford 訓練路線的變體；P2 的方法來源與失效條件以原始 CDR 為準 |
| Kueng 2016、Sanders 2016 | Wallman & Emerson 2016、Hashim 2021 | coherent 誤差與平均指標的理論很重要，但本輪聚焦探針方法；E2 的推導階段會再用到 |
| van den Berg 2022（TREX）、Chen 2019 | Maciejewski 2021 | TREX 是不依賴模型的緩解，不是偵測；E5（相關讀出）的直接證據以 Maciejewski 較完整 |
| Kaufmann 2016、Garivier & Kaufmann 2016、Chen 2000（OCBA） | 無 | 預算分配屬於規範 [宜] 項，等 Proposition 2 推導時再盤點 |
| Rosenbaum 1987、VanderWeele & Ding 2017 | Lipsitch 2010 | 屬於報告格式（翻轉所需最小偏差），不是本輪痛點分析的核心 |
| McArdle 2019、Sagastizabal 2019 | Bonet-Monroig 2018 | 對稱性驗證以 Bonet-Monroig 為方法代表 |
| Erhard 2019、Gambetta 2012 | Proctor 2022、Sarovar 2020 | 同屬特性化協定；Gambetta 2012 還是 partial，不在 78 篇內 |
| Kim 2023（Nature）、Kandala 2019 | Hashim 2021 | 大規模 ZNE 硬體證據是背景；本專案的硬體部分只做讀出 |

## 搜尋時看到的 3 篇候選（2026-11-10 已查證，加入 library 為 preprint）
- arXiv 2606.15464，Scavino Alfaro，Certified Finite-Shot Operating Windows for VD and SV：換入 20 篇（#8）。
- arXiv 2606.21686，Scavino，Finite-shot operating windows for PEC and CDR：只進 library。
- arXiv 2605.29872，Köster & Mauerer，Claim against Measurement：只進 library。
