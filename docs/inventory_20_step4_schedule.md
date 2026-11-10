# 20 篇文獻盤點：第四步 條列式詳細進度（2026-11-10）

> 依據：
> - 第三步拍板：A2、A3–A6、A7 採用；A1 暫緩，2026-11-16 前定案，逾期視為不採用。
> - 面向：F1 可見性邊界（主要）、F2 資料決定上界的認證（次要）、F3 既有診斷比較（探索性）。
> - 痛點編號沿用 step2：痛點 1–6、次要 1–2。
>
> **期程**：A2 讓 Part 1a 增加約 4 天。依「延期只能順延、不能改內容」，原計畫 v0.4 第 14 節的日期整體往後移 4 天。
>
> | 階段 | v0.4 日期 | 本表日期 |
> |---|---|---|
> | Part 1a | 11-17 至 11-30 | 11-17 至 12-04 |
> | Part 1b | 12-01 至 12-14 | 12-05 至 12-18 |
> | Part 1c | 12-15 至 12-28 | 12-19 至 2027-01-01 |
> | Part 1d | 12-29 至 01-11 | 2027-01-02 至 01-15 |
> | Part 2 | 01-12 至 02-22 | 01-16 至 02-26 |
> | Part 3 | 02-23 至 03-22 | 02-27 至 03-26 |
> | Part 4 | 03-23 至 05-03 | 03-27 至 05-07 |
>
> Part 2 的開始條件不變：Part 1d 凍結完成，而且舊專案已結案。
> 預估天數是工作量估計。同一個 Part 內有些項目可以並行，所以加總可能超過該 Part 的日曆天數。

## 通用規則（每個 prompt 都已內含，這裡集中列出供核對）
- **G1**：不 commit、不 push、不 reset，只給指令讓使用者執行；不在使用者電腦上跑 git。
- **G2**：不用 ML；不跑硬體，除非使用者明確授權那一次。
- **G3**：不杜撰引用、數字或結果。新引用要上網查證作者、期刊、卷期、DOI，查不到就標「未查證」，不寫進 references.bib。
- **G4**：探針不讀目標電路的理想值；每個探針寫明電路數與 shots。
- **G5**：解析預測在有雜訊模擬之前凍結，模擬結果不回頭改理論。
- **G6**：每個「探針有效」的主張，都要同時列出它在哪些結構下無效。
- **G7**：證據類型分開標示：解析、無雜訊模擬、有雜訊模擬、裝置參數模擬、硬體。
- **G8**：交付前先問使用者要直接寫 repo、貼內容，還是給指令。
- **G9**：做完用 8 項格式回報：建立或修改的檔案、實驗網格、驗證結果、主要發現、負面或無定論、科學疑慮、下一組可否開始、commit hash。

---

## W0（2026-11-10 至 11-16）

**W0-1｜W0｜計畫 v0.5：套用 A2–A6 與期程順延**　〔2026-11-10 已完成，由 Claude 依協作規則直接套用；使用者複核即可〕
- 產出：`docs/project_plan_v0.md` v0.5；`docs/literature_review.md` 第 6 節更新
- 驗收：
  - 改動只限 A2–A6 的文字、第 14 節日期整體 +4 天、第 11 節記錄拍板結果；
  - 主要終點、次要終點、已決定事項全部不變；
  - 使用者逐段核對通過。
- 對應：A2–A6；痛點 1、5；次要 1
- 預估：0.5 天
- Prompt：
```
任務：把已拍板的調整套用到 bias-probe-visibility repo 的計畫文件，不做其他修改。
輸入：docs/project_plan_v0.md（v0.4）、docs/inventory_20_step3_facets.md 第 2、2b 節、docs/inventory_20_step2_painpoints.md C 節、docs/literature_review.md 第 6 節。
要做：
(1) 第 3 節加入「局部 vs 全域」命題作為 Part 1a 目標，寫明要和 Scavino Corollary C.1 對照並附兩個反例（A2）。
(2) P5 的敘述改成：盲點已由 Scavino Alfaro 2026（arXiv 2606.15464）以 residual undetectable-sector bias 指出，本專案的貢獻是放進固定預算、決策層、全域符號條件的同一張邊界圖（A3）。
(3) 第 0 節與 literature_review.md 第 6 節的新穎性，改成 step2 C.1 的四條件版本，並以「據我們所讀」限定（A4）。
(4) 第 9 節加一條：證據範圍窄是本專案也有的問題，不處理，結論限定在存在性（A5）。
(5) 第 10 節註明極限文獻照常引用，但不作為主要痛點或新穎性支柱（A6）。
(6) 第 14 節日期整體 +4 天；第 11 節記錄 2026-11-10 拍板結果；第 12 節記錄 A1 暫緩、2026-11-16 前定案。
輸出格式：修改後的完整檔案，加上一份逐段的「改了什麼」清單。
禁止：改主要或次要終點；改任何門檻；新增或刪除探針；改 Part 的數量或順序；commit 或 push；在使用者電腦上跑 git；未經詢問就交付。
做完回報：8 項格式；另列出所有改動的段落編號。交付前先問使用者要直接寫 repo、貼內容，還是給指令。
```

**W0-2｜W0｜精讀 Scavino 附錄 C：θ 的內容**
- 產出：`docs/reading_notes_2026-11-10.md` 第 4 節補記（或另開新日期的筆記檔）
- 驗收：用原文逐字引述回答「θ 是否包含雜訊參數」。若原文沒寫明，就寫「據我們所讀未寫明」，並附上讀過的段落範圍。
- 對應：F1、痛點 5、A2
- 預估：1 天
- Prompt：
```
任務：讀 arXiv 2607.02888（Scavino, Decision Kernels for QEM）的附錄 C 與第 9 節，回答一個問題：primitive laws p_{s,θ} 裡的 θ 包含哪些量？特別是有沒有包含雜訊參數。
輸入：https://arxiv.org/pdf/2607.02888；docs/reading_notes_2026-11-10.md 第 4 節。
輸出格式：
(a) 逐字引文，每段附章節或式號；
(b) 一句結論，只能是以下三者之一：「θ 包含雜訊參數」、「θ 不包含雜訊參數」、「據我們所讀未寫明」；
(c) 對 Corollary C.1 與本專案「盲」定義之關係的影響（若 θ 含雜訊參數，C.1 就是我們「可見」的局部點值版本）。
禁止：推測式措辭；把轉述寫成引文；說「它沒有做 X」（只能說「據我們所讀未說明」）；commit；未經詢問就交付。
做完回報：8 項格式。交付前先問交付方式。
```

**W0-3｜W0｜A1 定案（使用者決定）**
- 產出：計畫第 11 節的一行決定紀錄
- 驗收：使用者明確回覆「採用」或「不採用」；逾期視為不採用
- 對應：F3、痛點 6
- 預估：0 天（AI 只負責提醒）
- Prompt：
```
任務：在 2026-11-16 前提醒使用者決定 A1（是否把 Köster & Mauerer 的 W_neg 加入探針集作為 P1b，並以 Scavino 的 GVS 為對照基線）。
輸入：docs/inventory_20_step3_facets.md 第 2 節 A1 列。
輸出格式：一則訊息，列出 A1 的代價（Part 1b 多約 3–4 天；探針 7→9；砍範圍規則要重寫）與好處（直接支撐四條件新穎性），用選擇題請使用者回覆。
禁止：替使用者決定；在使用者回覆前修改計畫。
做完回報：使用者的決定原文，以及要寫進計畫第 11 節的一行文字。
```

---

## Part 1a 定義與 Lemma（2026-11-17 至 12-04，只做解析）

**1a-1｜Part 1a｜定義稿**
- 產出：`docs/theory/01_definitions.md`
- 驗收：
  - 識別區域、原理上盲、預算內盲、可見都有定義；
  - 每個定義標明出處（Imbens & Manski 第 2 節）或「本專案的定義」；
  - 兩個假設明寫：(i) 給定 P 與 e 時理想差距唯一確定；(ii) 理想差距在原理上是確定值，我們當它未知是建模選擇；
  - 已納入使用者對 Imbens & Manski 的複核結論。
- 對應：F1、痛點 5
- 預估：3 天
- Prompt：
```
任務：寫本專案的核心定義稿，只做解析。
輸入：docs/project_plan_v0.md 第 2 節；docs/reading_notes_2026-11-10.md 第 2 節（Imbens & Manski 核對）；使用者對 Imbens & Manski 與 Chen 2023 的複核筆記（向使用者索取，不自行假設內容）。
要做：用 Imbens & Manski 的形式 Δ = f(P, e) 定義識別區域 {f(P, e′): e′ ∈ 𝓔}，再定義原理上盲、預算內盲、可見。P 是目標加探針的聯合可觀測分布。
輸出格式：Markdown 加 LaTeX 數學。每個定義後附「出處：…」或「本專案的定義」。最後一節「必須明說的假設」列 (i)(ii)，並寫明探針讓 P 改變、𝓔 仍為固定集合，這一步是我們的推導。
禁止：把我們的推導寫成原文的；引用未查證文獻（例如 Rothenberg 1971 在查證前不得引用）；跑任何模擬；commit；未經詢問就交付。
做完回報：8 項格式；另列出所有「本專案的定義」，讓使用者逐條核可。交付前先問交付方式。
```

**1a-2｜Part 1a｜Lemma 1 與證明**
- 產出：`docs/theory/02_lemma1.md`
- 驗收：
  - 敘述與證明完整：若識別區域同時含異號點，任何規則都有 P₁(錯) + P₂(錯) ≥ 1；
  - 寫出推論：只看目標的 CI 認證，對 𝓔 允許的夠大偏差是盲的；
  - 兩點法的出處要查證後才引用。
- 對應：F1、痛點 3、痛點 5
- 預估：3 天
- Prompt：
```
任務：寫 Lemma 1 的敘述與完整證明。
輸入：docs/theory/01_definitions.md；docs/project_plan_v0.md 第 3 節第 1 點。
要做：證明當識別區域同時含 Δ > 0 與 Δ ≤ 0 的點時，任何決策或認證規則都滿足 P_{θ₁}(錯) + P_{θ₂}(錯) ≥ 1；再推出 CI-only 認證的盲性推論。
輸出格式：Markdown 加 LaTeX；結構為敘述、證明、推論、適用條件、不適用的情況。
禁止：引用 Le Cam 1973 的頁碼或任何未查證來源（若要引兩點法，先上網查證出處；查不到就標「未查證」，並只寫成「標準兩點論證」）；用模擬結果支撐證明；commit；未經詢問就交付。
做完回報：8 項格式；另列出證明中每個用到的假設。交付前先問交付方式。
```

**1a-3｜Part 1a｜有限 shots 下界**
- 產出：`docs/theory/03_finite_shot_bound.md`
- 驗收：用 TV 或 Hellinger 距離寫出「區分兩個 θ 所需 shots」的下界；明確區分距離為 0（原理上盲）與距離很小（預算內盲）
- 對應：F1
- 預估：3 天
- Prompt：
```
任務：把 Lemma 1 推廣到有限 shots，給出分辨兩組參數所需的 shot 數下界。
輸入：docs/theory/01_definitions.md、02_lemma1.md。
要做：用 total variation 或 Hellinger 距離，對 N 個獨立 shot 的乘積分布推出錯誤機率下界，並換算成「預算內盲」的條件。
輸出格式：Markdown 加 LaTeX；附一個解析小例子（例如兩個單量子位元 Pauli 通道），標為「解析」證據。
禁止：跑有雜訊模擬；引用未查證的不等式出處（教科書不等式若要引用，需先查證）；commit；未經詢問就交付。
做完回報：8 項格式。交付前先問交付方式。
```

**1a-4｜Part 1a｜局部 vs 全域命題與兩個反例（A2）**
- 產出：`docs/theory/04_local_vs_global.md`
- 驗收：
  - 命題敘述兩者「互不包含」；
  - 反例一：局部可識別但全域盲；
  - 反例二：局部不可識別但全域不盲；
  - 兩個反例都能用解析或無雜訊計算驗證，並標證據類型；
  - 和 Scavino Corollary C.1 的關係，依 W0-2 的結論寫。
- 對應：F1、痛點 5、A2
- 預估：4 天
- Prompt：
```
任務：證明「局部可識別性（Scavino Corollary C.1 型的 Fisher 零空間條件）」與本專案的「全域符號判準（識別區域是否含異號點）」互不包含，並各給一個反例。
輸入：docs/theory/01_definitions.md；docs/reading_notes_2026-11-10.md 第 4 節與 W0-2 的補記；Corollary C.1 的原文引文。
輸出格式：Markdown 加 LaTeX：命題、證明、反例一（局部可識別但全域盲）、反例二（局部不可識別但全域不盲）、小邊際極限下兩者的關係。每個反例附可重算的解析式；若用數值驗證，只能用無雜訊計算，並標「無雜訊模擬」。
禁止：在 W0-2 未定案前宣稱 θ 含雜訊參數；把 Scavino 的條件改寫成原文沒有的形式；跑有雜訊模擬；commit；未經詢問就交付。
做完回報：8 項格式；另寫一段可放進相關研究表的比較文字，每句都標原文出處。交付前先問交付方式。
```

**1a-5｜Part 1a｜可學性判準草稿**
- 產出：`docs/theory/05_learnability.md`
- 驗收：依使用者的 Chen 2023 精讀結論，寫出「差異偏差對 cut space 的投影」判準，或寫明「Chen 2023 的定理條件不適用本專案的目標電路」。兩種結論都算完成。
- 對應：F1、痛點 5
- 預估：3 天
- Prompt：
```
任務：把 Chen et al. 2023（The learnability of Pauli noise）的不可學分量，接到本專案的識別區域定義。
輸入：使用者對 Chen 2023 的精讀筆記（必須向使用者索取）；docs/theory/01_definitions.md；docs/project_plan_v0.md 第 3 節 1b。
輸出格式：Markdown 加 LaTeX：(a) Chen 2023「學不到」的精確意義，引原文；(b) 能否寫成識別區域的特例；(c) 若能，寫出判準；若不能，寫出不能的理由。
禁止：在沒有使用者精讀筆記的情況下自行推定定理條件；把只讀過摘要的內容寫成定理；commit；未經詢問就交付。
做完回報：8 項格式；明確寫出結論是「可接上」還是「不可接上」。交付前先問交付方式。
```

---

## Part 1b 矩陣推導（2026-12-05 至 12-18，只做解析）

**1b-1｜Part 1b｜探針 × 結構矩陣（P0–P5 × E0–E6）**
- 產出：`docs/theory/06_matrix.md`；`docs/theory/06_matrix.csv`（欄位：探針、結構、預測、推導摘要、失效條件、信心）
- 驗收：
  - 每一格都有不變性證明、敏感度 κ 推導，或明確寫「?」及原因；
  - 每個 ✓ 都附它的 ✗ 格（G6）；
  - 有效條件用本專案定義的、類比於 U-comparability 的量子版條件，並寫明是類比。
- 對應：F1、痛點 1
- 預估：8 天
- Prompt：
```
任務：推導探針 P0–P5 在誤差結構 E0–E6 下的可見性預測，只做解析。
輸入：docs/project_plan_v0.md 第 4 節；docs/theory/01–05；docs/reading_notes_2026-11-10.md 第 1 節（Lipsitch 原文）；Giurgica-Tiron 2020 與 Wallman & Emerson 2016 的作者自承限制（見 docs/inventory_20_step1.md）。
輸出格式：
(1) 06_matrix.md：每格一小節，含預測（✓／✗／△／?）、推導、失效條件；
(2) 06_matrix.csv，欄位：probe, structure, prediction, derivation_summary, failure_condition, confidence。
有效條件要寫成「本專案的量子版條件，類比於 Lipsitch et al. 2010 的 U-comparability」。
禁止：用模擬結果決定預測；把 Lipsitch 的條件說成「共享偏差機制」；把任何格子寫成 ✓ 卻不列出對應的 ✗；commit；未經詢問就交付。
做完回報：8 項格式；另列出所有「?」格與原因。交付前先問交付方式。
```

**1b-2｜Part 1b｜P5 對稱性探針重新定位與盲點推導（A3）**
- 產出：`docs/theory/06_matrix.md` 的 P5 小節
- 驗收：引用 2606.15464 的 "residual undetectable-sector bias"；說明本專案的差別在固定預算、決策層、全域符號；推導 P5 對保持對稱之誤差的盲性
- 對應：F1、A3
- 預估：2 天（可和 1b-1 並行）
- Prompt：
```
任務：寫 P5（對稱性檢查）的可見性推導，並依 A3 重新定位其新穎性。
輸入：docs/inventory_20_step1.md #8、#17；docs/inventory_20_step2_painpoints.md C.1；arXiv 2606.15464 的相關段落（如需引文，重新讀取並逐字引述）。
輸出格式：Markdown 小節：定位（一段，先寫前人已指出什麼）、推導、預測、失效條件。
禁止：宣稱本專案首先發現 P5 的盲點；把 2606.15464 寫成「執行時偵測」（它的殘差偏差是用模型與理想態算出的）；commit；未經詢問就交付。
做完回報：8 項格式。交付前先問交付方式。
```

**1b-3｜Part 1b｜既有診斷的文字層比較（A1 不採用時執行）**
- 產出：`docs/related_work_table.md`
- 驗收：W_neg、GVS、DRI／GRI、SV clip 監控逐欄比較（是否需理想值、針對什麼、是否計費、門檻、是否針對差異偏差）；每格可查證到原文；不確定就不寫「沒有」
- 對應：F3、痛點 6
- 預估：2 天
- Prompt：
```
任務：建立既有執行時診斷的比較表（文字層，不做模擬）。
輸入：docs/inventory_20_step2_painpoints.md C.1；Köster & Mauerer 2026（arXiv 2607.09360）、Scavino 2026（2607.02888）、Scavino Alfaro 2026（2606.15464）原文。
輸出格式：Markdown 表格，欄位：診斷名、出處、是否需理想值、針對的失效模式、是否在固定預算內計費、門檻是否凍結、是否針對候選間差異偏差、引文。
禁止：寫「沒有」而無原文依據（改寫「據我們所讀未見」）；commit；未經詢問就交付。
做完回報：8 項格式。交付前先問交付方式。
```

---

## Part 1c Proposition 2 與認證（2026-12-19 至 2027-01-01，只做解析）

**1c-1｜Part 1c｜偏差感知認證與聯合覆蓋**
- 產出：`docs/theory/07_certificate.md`
- 驗收：
  - 認證規則：差距的信賴下界 > B，B 由探針資料決定；
  - 聯合覆蓋的推導（例如以聯合界同時控制探針區間與目標區間）；
  - 寫明和 Armstrong & Kolesár（先驗偏差上界）的差別；
  - 在盲方向上，證明規則永遠不認證。
- 對應：F2、痛點 2、痛點 3
- 預估：5 天
- Prompt：
```
任務：推導資料決定偏差上界 B 的偏差感知認證，並證明其聯合覆蓋。
輸入：docs/theory/01–03；docs/reading_notes_2026-11-10.md 第 3 節（Armstrong & Kolesár 原文）、第 2 節（Imbens & Manski）。
輸出格式：Markdown 加 LaTeX：規則、覆蓋定理與證明、與 Armstrong & Kolesár 的差異（逐點，附原文引文）、盲方向不認證的證明、一個解析例子。
禁止：宣稱直接繼承 Armstrong & Kolesár 的覆蓋率；用模擬取代證明；commit；未經詢問就交付。
做完回報：8 項格式；另列出覆蓋證明中的所有條件。交付前先問交付方式。
```

**1c-2｜Part 1c｜Proposition 2：探針預算比例何時划算**
- 產出：`docs/theory/08_prop2.md`
- 驗收：以 Proposition 1 為範本，推出探針比例 f 的划算條件；預算分配語言引用 Kaufmann 2016、Garivier & Kaufmann 2016、Chen et al. 2000（已查證）
- 對應：F2、次要 2
- 預估：3 天
- Prompt：
```
任務：推導 Proposition 2：總預算 N 中拿 fN 做探針、(1−f)N 做決策，在什麼條件下整體決策錯誤率會下降。
輸入：上一版 Proposition 1（adaptive-qem-benchmark 的 paper/main_v2.tex 第 2 節，只讀不改）；docs/project_plan_v0.md 第 3 節第 4 點；docs/theory/07_certificate.md。
輸出格式：Markdown 加 LaTeX：命題、證明、和 Proposition 1 的對照、適用條件；預算分配相關的引用只能用 library.csv 中已查證的條目。
禁止：修改舊 repo；引用未查證文獻；commit；未經詢問就交付。
做完回報：8 項格式。交付前先問交付方式。
```

**1c-3｜Part 1c｜Proposition 1 延伸（K 個候選、γ 需估計、與極限文獻接軌）**
- 產出：`docs/theory/09_prop1_ext.md`
- 驗收：
  - K 候選版本；
  - γ 與 a 用估計值代入時的修正；
  - 小樣本或非常態下的界或修正；
  - 說明 γ 是 Takagi、Quek 下界在單一估計器上的實例；
  - 引用 Scavino 2026 的有效邊際並比較。
- 對應：次要終點（Proposition 1 事前預測測試）、次要 1
- 預估：4 天
- Prompt：
```
任務：延伸上一版 Proposition 1（Δ_m > √γ Δ_r），處理 K 個候選、γ 與 a 需要估計、小樣本修正，並說明它和 QEM 極限文獻的關係。
輸入：舊 repo paper/main_v2.tex 中的 Proposition 1（只讀）；Takagi 2022、Quek 2024 的摘要與（若已讀）相關段落；Scavino 2026 的有效邊際 μ_m = Δ + L a_m 定義與引文。
輸出格式：Markdown 加 LaTeX：延伸命題、證明、與 Scavino 有效邊際的比較、與 Takagi／Quek 的接軌段落（每句標出處與閱讀深度）。另附 Part 3 事前預測測試要用的 pilot 估計式與判定規則草稿，標「待 Part 1d 凍結」。
禁止：宣稱 Takagi／Quek 的定理細節（只讀過摘要的部分不得寫成定理內容）；改主要或次要終點；commit；未經詢問就交付。
做完回報：8 項格式。交付前先問交付方式。
```

**1c-4｜Part 1c｜文獻補到 90 篇以上**
- 產出：`docs/literature/library.csv`；`paper/references.bib`
- 驗收：已查證 ≥ 90 篇；每篇 3 行筆記；5 篇 partial 補齊或維持排除；cluster bootstrap 與 mixed-effects 的原始出處查證完成
- 對應：規範第二部分第 1、2、7 條
- 預估：3 天（可並行）
- Prompt：
```
任務：把 library.csv 的已查證文獻補到 90 篇以上。
輸入：docs/literature/library.csv；docs/literature_review.md 第 8 節的待補主題（biased／misspecified bandits、QEM 模型不確定性、cluster bootstrap 與 mixed-effects 原始出處）。
要做：逐篇上網查證作者、期刊、卷期、DOI，記錄 source_checked；查不到就標 partial，不放進 references.bib。
輸出格式：更新後的 library.csv 與 references.bib，加上一份新增清單（每篇：查證來源、閱讀深度、3 行筆記）。
禁止：用記憶補書目；把 partial 放進 bib；用 API 以外的方式繞過被拒的網站；commit；未經詢問就交付。
做完回報：8 項格式；另附 bib 與 library 的一致性檢查結果。交付前先問交付方式。
```

---

## Part 1d 凍結（2027-01-02 至 01-15）

**1d-1｜Part 1d｜檢定力模擬（預測凍結後才跑）**
- 產出：`experiments/power/`（程式、raw rows、run log）；`docs/freeze/power_analysis.md`
- 驗收：
  - 只在 06_matrix 預測已 commit 之後才執行；
  - 決定 holdout ≥ 100 個電路、QAOA ≥ 50 張圖與 ≥ 3 種圖族、每個寬度與深度至少 2 個電路；
  - run log 記錄 numpy 版本與 BLAS 設定；
  - 依凍結的砍範圍規則決定範圍。
- 對應：F1、規範第 14 條
- 預估：4 天
- Prompt：
```
任務：用模擬做檢定力分析，決定 holdout 與重複次數。
前提：先確認 docs/theory/06_matrix.csv 已由使用者 commit；若沒有，立即停止並回報。
輸入：docs/theory/06_matrix.csv；docs/project_plan_v0.md 第 5–6 節（終點與門檻）。
輸出格式：experiments/power/ 下的程式（seed 從 ROOT_SEED 推導）、raw rows CSV、run log（含 numpy 版本與 np.show_config 輸出）；docs/freeze/power_analysis.md 寫明每個設計參數的決定與檢定力，並報告每個「數值 vs 門檻」離門檻多近。
禁止：看到檢定力結果後修改 06_matrix 的預測；用 ML；跑硬體；覆蓋 raw rows；commit；未經詢問就交付。
做完回報：8 項格式；實驗網格要完整列出。交付前先問交付方式。
```

**1d-2｜Part 1d｜凍結文件**
- 產出：`docs/freeze/frozen_protocol_v1.md`（含內容雜湊）
- 驗收：結構與參數網格、探針規格與成本公式、門檻與敏感度表、dev/holdout seed 切分、主要終點、砍範圍規則、Proposition 1 測試的 pilot 程序與判定規則，全部寫死；並列出「可調但需記錄」的項目
- 對應：痛點 6、全部面向
- 預估：3 天
- Prompt：
```
任務：彙整凍結文件。
輸入：docs/theory/01–09、06_matrix.csv、docs/freeze/power_analysis.md、docs/project_plan_v0.md。
輸出格式：docs/freeze/frozen_protocol_v1.md，章節依序為：範圍、定義、預測矩陣（引用 06_matrix.csv 的雜湊）、探針規格與成本、門檻與敏感度表、資料切分與 seed、主要與次要終點、砍範圍規則、Proposition 1 事前預測程序、可調但需記錄的項目、變更規則（延期只能順延）。文末附檔案內容雜湊的計算指令。
禁止：新增未經拍板的探針或終點；寫入任何模擬結果作為預測依據；commit；未經詢問就交付。
做完回報：8 項格式。交付前先問交付方式。
```

**1d-3｜Part 1d｜OSF／AsPredicted 登記草稿**
- 產出：`docs/freeze/registration_draft.md`
- 驗收：內容與凍結文件一致；由使用者自己提交，並把時間戳記回 repo
- 對應：規範第 12 條
- 預估：1 天
- Prompt：
```
任務：依 docs/freeze/frozen_protocol_v1.md 寫 OSF（或 AsPredicted）登記表的草稿。
輸出格式：依登記平台的欄位順序逐欄填寫；每欄註明對應凍結文件的章節。
禁止：代替使用者提交；在沒有獨立時間戳之前使用「preregistration」一詞（改寫「在 repository 中先凍結並 commit」）。
做完回報：8 項格式；提醒使用者提交後把時間戳寫回 repo。
```

---

## Part 2 實作與開發集（2027-01-16 至 02-26；開始條件：Part 1d 完成且舊專案結案）

**2-1｜Part 2｜探針實作與成本帳本**
- 產出：`src/probes/`、`tests/test_probes.py`
- 驗收：P0–P5（A1 採用時加 P1b、GVS）都有實作；測試確認每次執行的總 shots 等於預算；探針不讀目標理想值（用測試守住）
- 對應：F1、F2
- 預估：8 天
- Prompt：
```
任務：依凍結文件實作探針與成本帳本。
輸入：docs/freeze/frozen_protocol_v1.md 的探針規格與成本公式。
輸出格式：src/probes/ 模組（每個探針一個函式，回傳統計量與實際花費的電路數與 shots）；tests/test_probes.py，至少包含：總 shots 等於預算、探針函式不接收理想值參數、seed 可重現。
禁止：改動凍結文件中的任何規格；用 ML；只格式化新檔，不對整個 repo 跑 ruff format；commit；在使用者電腦上跑 git；未經詢問就交付。
做完回報：8 項格式；另附 pytest 指令（Windows 要加 --basetemp="$env:TEMP\qem-pytest"）。交付前先問交付方式。
```

**2-2｜Part 2｜正負對照與交叉驗證**
- 產出：`experiments/dev_controls/`；`docs/dev/controls_report.md`
- 驗收：解析上已知 β 的案例必須觸發警報；E0 的假警報率約等於 α；P1 用 Mitiq folding 交叉驗證；P2 的 Clifford 理想值用兩套 stabilizer 程式交叉驗證
- 對應：痛點 6、規範第 23 條
- 預估：5 天
- Prompt：
```
任務：在開發集上跑正負對照與交叉驗證。
輸入：docs/freeze/frozen_protocol_v1.md；src/probes/。
輸出格式：experiments/dev_controls/ 下的程式、raw rows、run log；docs/dev/controls_report.md 逐項列出通過或失敗與數值，以及離門檻的距離。
禁止：讀 holdout seed 的任何資料；失敗時修改探針規格或放寬容差；刪除失敗的 run；commit；未經詢問就交付。
做完回報：8 項格式，失敗項目要按成因分類（方法、資源、模型、設計）。交付前先問交付方式。
```

**2-3｜Part 2｜警報門檻校準（只用 E0 虛無分布）並 commit**
- 產出：`docs/dev/thresholds_v1.md`；開發集不一致清單
- 驗收：門檻依凍結程序從 E0 校準；開發集和預測不一致的格子照實列出；不回頭改理論
- 對應：痛點 6、F1
- 預估：4 天
- Prompt：
```
任務：依凍結程序，只用 E0（common-mode）虛無分布校準警報門檻，並列出開發集上的不一致格子。
輸入：docs/freeze/frozen_protocol_v1.md；experiments/dev_controls/ 的 raw rows。
輸出格式：docs/dev/thresholds_v1.md（每個探針的門檻、校準樣本數、敏感度）；docs/dev/dev_mismatch.md（每個不一致格子：預測、觀測、可能成因）。
禁止：依不一致結果修改 06_matrix 的預測或理論文件；讀 holdout；commit；未經詢問就交付。
做完回報：8 項格式；提醒使用者在 Part 3 前 commit 門檻檔。交付前先問交付方式。
```

---

## Part 3 驗證性 holdout（2027-02-27 至 03-26）

**3-1｜Part 3｜holdout 一次性評分（主要終點）**
- 產出：`results/holdout/`（raw rows、summary、run log）；`docs/results/primary_endpoint.md`
- 驗收：只執行一次；可見性預測一致率附 Wilson 區間；可以從 raw rows 獨立重算；Windows 與 Linux 兩個平台都跑並比較
- 對應：F1（主要）
- 預估：6 天
- Prompt：
```
任務：在 holdout 上計算主要終點，只做一次。
前提：確認門檻檔與凍結文件已 commit；若沒有，停止並回報。
輸入：docs/freeze/frozen_protocol_v1.md；docs/dev/thresholds_v1.md；src/probes/。
輸出格式：results/holdout/ raw rows（永不覆蓋）、summary（可由 raw rows 重算的腳本）、run log（numpy 版本與 BLAS 設定）；docs/results/primary_endpoint.md（一致率、Wilson 區間、每格結果、離門檻距離）。
禁止：看到結果後修改任何規則或門檻；重跑 holdout；刪除不合格的 row；commit；未經詢問就交付。
做完回報：8 項格式；不利結果照實寫。交付前先問交付方式。
```

**3-2｜Part 3｜偏差感知認證 vs CI-only（次要，F2）**
- 產出：`docs/results/secondary_certificate.md`
- 驗收：相同總預算下的錯誤認證率與未決率，附區間
- 對應：F2
- 預估：3 天
- Prompt：
```
任務：在 holdout 資料上比較偏差感知認證與 CI-only 認證（次要終點）。
輸入：results/holdout/ raw rows；docs/theory/07_certificate.md 的規則（已凍結）。
輸出格式：docs/results/secondary_certificate.md：兩種規則的錯誤認證率、未決率、Wilson 區間，標明是次要終點。
禁止：修改認證規則；把次要結果寫成主要結論；commit；未經詢問就交付。
做完回報：8 項格式。交付前先問交付方式。
```

**3-3｜Part 3｜Proposition 1 事前預測測試（次要，只做一次）**
- 產出：`docs/results/prop1_prediction_test.md`；預測值檔案（先 commit 並登記，再跑評分資料）
- 驗收：流程依序為 pilot、預測值寫檔、使用者 commit 並登記、評分資料、命中率只報告一次
- 對應：次要終點
- 預估：4 天
- Prompt：
```
任務：執行 Proposition 1 的事前預測測試，只做一次。
步驟一（停點）：跑 pilot，依凍結的估計式算出每張新圖的 a 與 γ，並依判定規則寫出 raw 或 ZNE 較好的預測，存成 results/prop1/predictions.csv。然後停止，請使用者 commit 並登記。
步驟二：使用者回報 commit hash 與登記時間戳後，才跑評分資料並計算命中率。
輸出格式：predictions.csv；docs/results/prop1_prediction_test.md（命中率、區間、逐圖結果）。
禁止：步驟一之後在使用者回報前跑評分資料；修改預測；重跑；commit；未經詢問就交付。
做完回報：8 項格式。交付前先問交付方式。
```

---

## Part 4 整合與論文（2027-03-27 至 05-07）

**4-1｜Part 4｜邊界圖與失敗成因分類**
- 產出：`figures/boundary_map.*`；`docs/results/boundary_synthesis.md`
- 驗收：結構 × β/Δ × f* 的邊界圖；每個失敗按成因分類（方法、資源、模型、設計）；F3 的比較依 A1 決定為模擬層或文字層
- 對應：F1、F3
- 預估：5 天
- Prompt：
```
任務：彙整可見性邊界圖與失敗成因分類。
輸入：results/holdout/、docs/results/*.md、docs/theory/06_matrix.csv。
輸出格式：figures/boundary_map.png（圖說第一句是結論）；docs/results/boundary_synthesis.md（每格：預測、觀測、成因分類、證據類型）。圖檔一致性用像素層級比對，provenance --write 放在所有產生步驟之後。
禁止：把探索性結果寫成驗證性；隱藏不一致的格子；commit；未經詢問就交付。
做完回報：8 項格式。交付前先問交付方式。
```

**4-2｜Part 4｜硬體 go/no-go 審查**
- 產出：`docs/hardware/review_v1.md`
- 驗收：依計畫第 13 節的時間預算與降級規則；查 IBM 當下的方案說明；證據不足時判定 no-go；go 時需要使用者另外明確授權
- 對應：規範第一部分第 11 條、第 22 條
- 預估：2 天
- Prompt：
```
任務：做讀出硬體實驗（P4a、P4b）的 go/no-go 審查，不跑任何硬體。
輸入：docs/project_plan_v0.md 第 13 節；上網查 IBM Quantum 方案的當下官方說明（記錄查詢日期與網址）。
輸出格式：docs/hardware/review_v1.md：go 條件逐條勾核、no-go 觸發條件、時間預算估計（不得用未量測的每 shot 時間）、結論。
禁止：送出任何 job；要求、貼出或寫入 API key；在沒有使用者明確授權的情況下判定可執行；commit；未經詢問就交付。
做完回報：8 項格式。交付前先問交付方式。
```

**4-3｜Part 4｜宣稱清單與論文初稿**
- 產出：`paper/claims.md`（先寫）；`paper/main.tex`
- 驗收：先完成宣稱清單（每條標證據類型與強度）；摘要最多 3 個數字；每節第一句是結論；新穎性用四條件版本並以「據我們所讀」限定；限制段含原痛點 7；每個 \cite 都在 bib 裡，反之亦然
- 對應：全部面向；A4、A5、A6
- 預估：10 天
- Prompt：
```
任務：先寫宣稱清單，再寫論文初稿。
輸入：docs/results/*.md、docs/theory/*.md、paper/references.bib、docs/inventory_20_step2_painpoints.md、docs/inventory_20_step3_facets.md。
輸出格式：
(1) paper/claims.md：每條宣稱附證據類型（解析、無雜訊模擬、有雜訊模擬、裝置參數模擬、硬體）、強度、出處檔案；
(2) paper/main.tex：沿用上一篇報告格式，摘要最多 3 個數字，每節第一句是結論，一個數字只在一處給出。
禁止：宣稱普遍規律（只寫存在性）；寫「前人沒有做 X」（只寫「據我們所讀未見」）；引用 bib 以外的文獻；commit；未經詢問就交付。
做完回報：8 項格式；另附 \cite 與 bib 的雙向一致性檢查結果。交付前先問交付方式。
```

---

## (a) 凍結規則

**必須在跑任何有雜訊模擬之前寫死**（Part 1d，凍結文件加 OSF 登記）：
- 誤差結構與參數網格、β/Δ 網格；
- 每個探針的規格、成本公式、警報規則的形式；
- 門檻主值與敏感度範圍（計畫第 6 節）；
- dev/holdout 的 seed 切分；holdout 只讀一次；
- 唯一的主要終點（可見性預測一致率）與成功門檻；次要與探索性的分類；
- 06_matrix 的全部預測；
- 砍範圍規則與砍的優先順序；
- Proposition 1 事前預測的 pilot 程序、估計式、判定規則（預測值本身在 Part 3 步驟一寫檔並登記）；
- 硬體實驗的時間上限與降級順序（若進行）。

**可調，但每次都要記錄在 run log 和變更紀錄裡**：
- 不影響結果的工程細節：檔案結構、函式拆分、效能優化；
- 開發集上的實作錯誤修正，必須在讀 holdout 之前完成，並記錄修正前後的差異；
- 圖表的版面與配色，不得改變呈現的數值。

**變更規則**：
- 延期只能往後順延，不能改 Part 的內容或順序；
- 看到 holdout 結果後，不得修改任何規則或門檻；
- 理論與模擬不一致時，記為「預測失敗」，不回頭改理論。

## (b) 本輪不做的清單

| 不做 | 理由 |
|---|---|
| 原痛點 7：證據範圍窄，外推性不明 | 本專案以模擬為主，自身也有同樣問題；只在限制段承認，結論限定為存在性（使用者 2026-11-10 決定） |
| 痛點 4 不另立面向 | Scavino 2026 已處理「準確度不等於決策」；只作背景，由 Proposition 1 次要終點承接 |
| 次要 1：極限理論缺決策層 | 支撐只有 2 篇；只在寫作時回應口試第 1 題 |
| A1：W_neg 進探針集（暫緩） | 2026-11-16 前定案；不採用時，F3 只做文字層比較（1b-3） |
| 讀出相關的完整校正 | 本專案偵測偏差，不做緩解 |
| RC 一般雜訊的完整證明 | 屬於 RC 理論本身 |
| 極限理論的最壞情況 vs 典型情況 | 屬於估計器層 |
| 特性化協定的可擴展性 | 已有專門研究 |
| 評比方法學的統計嚴謹性 | 已被 Köster & Mauerer 2605.29872 處理；本專案只採用其建議做法 |
