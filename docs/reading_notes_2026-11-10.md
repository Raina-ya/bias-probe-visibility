# 精讀筆記 2026-11-10（Claude 初讀，待使用者複核）

> 讀取方式：用網頁讀取工具開啟原文 PDF 或 HTML，只摘錄相關段落。
> 下列英文引文是工具回傳的逐字摘錄，**放進論文前要對照原始 PDF 再核對一次**。工具偶爾會把長句拆開，Imbens & Manski 的 PDF 也是 OCR 文字（θ、∈ 等符號會變形）。
> 分工依使用者 2026-11-10 指示：
> - Chen 2023、Imbens & Manski 全文由使用者精讀；
> - 本筆記負責 Lipsitch、Armstrong & Kolesár、Scavino；
> - 另外依使用者要求，先核對 Imbens & Manski 的原始定義是否支持 v0.3 的寫法。

## 1. Lipsitch, Tchetgen Tchetgen & Cohen (2010)：第一優先

**出處（印在原文上）**："Epidemiology • Volume 21, Number 3, May 2010"；"(Epidemiology 2010;21: 383–388)"；"DOI: 10.1097/EDE.0b013e3181d61eeb"。
來源：<https://www.meb.ki.se/biostat/cc2024/papers/extras/Lipsitch%20EPI%202010%20neg%20controls%20for%20detecting%20confounding%20and%20bias.pdf>

**有效條件的原文**（都在 "CHOICE OF NEGATIVE CONTROLS TO DETECT CONFOUNDING IN EPIDEMIOLOGY" 一節）：

- 負對照結果（negative control outcome）：
  - "Ideally, a negative control outcome (N) should be an outcome such that the set of common causes of exposure A and outcome Y" … "should be as identical as possible to the set of common causes of A and N (Fig. 2)."
  - "To the extent that the set of unobserved common causes of A and Y overlaps with the set of unobserved common causes" … "(U) of A and N, we call the negative control outcome N "U-comparable" to Y."
  - "If N and Y are U-comparable outcomes (ie, with an identical set of common causes that are associated with A)" … "assuming that N is not caused by A"
- 負對照暴露（negative control exposure）：
  - "A negative control exposure B should be an exposure such that the common causes of A and Y are as nearly" … "identical as possible to the common causes of B and Y (Fig. 3)."
  - "If A and B are perfectly U-comparable and B does not cause Y,"
- 圖說：
  - Fig. 2："N should ideally have the same incoming arrows as Y, except that A does not cause N;"
  - Fig. 3："B should ideally have the same incoming arrows as A;"

**結論**
- 原文的條件叫 **U-comparability**，定義在因果圖裡：負對照與目標的「未觀測共同原因集合」相同或盡量相同，而且負對照不受暴露影響。
- 原文**沒有**「same bias mechanism」、「same incomplete set of causal mechanisms」、「same potential sources of bias」這些說法。我之前在 literature_review.md 和計畫 v0.3 寫的「共享偏差機制」是我的轉述，**不準確，已改掉**。
- 對本專案的意義：U-comparability 是流行病學觀察研究的混淆條件。把它用在量子探針上**只能當類比**。論文中要寫成「類比於 U-comparability (Lipsitch et al. 2010)」，並由我們自己給出量子版的條件。例如：探針統計量與目標差距對同一組雜訊參數有非零敏感度，且探針的理想值已知。這個量子版條件是我們的定義，必須明說是我們的定義，不能說是 Lipsitch 的。

## 2. Imbens & Manski (2004)：核對 v0.3 的「(理想差距, 雜訊) 一起未知」寫法

來源：<https://scholar.harvard.edu/sites/scholar.harvard.edu/files/imbens/files/confidence_intervals_for_partially_identified_parameters.pdf>（OCR 文字，符號已變形）

**原文定義**（第 2 節）：
- "The distribution P is not known, but a random sample of size N is available, with empirical distribution PN."
- "Let A be a quantity that is known only to belong to a specified set A."
- "The object of interest is the real parameter 0 = f(P, A)."（OCR 把 θ 讀成 0）
- "Then the identification region for f(P, A) is the set {f(P, A'), A' E A}."（E 應為 ∈）
- 範例（第 3 節，缺失資料下的平均）："The distribution of Y given W = 0 is unknown; hence, A e [0, 1]."

**原文沒有的東西**
- 沒有正式定義 "partially identified"，而是指向 Manski (2003)。
- 沒有「與資料分布相容的參數值集合」這類措辭。
- Tamer (2010) 也沒有出現 "observationally equivalent"，也沒有把結構寫成 (θ, F) 聯合未知。

**判斷：v0.3 的寫法有原文支持，但要加兩個條件，並改寫成 Imbens & Manski 的形式**
1. Imbens & Manski 的形式是 θ = f(P, A)：可觀測分布 P 加上一個只知道屬於某集合的未知量 A。對應到本專案，令 A = 雜訊 e、𝒜 = 𝓔，則 Δ = f(P, e)。這和「理想差距與雜訊一起未知」在結構上一致。論文中應該寫成這個形式，並引 Imbens & Manski 第 2 節，而不是寫成我們自創的 θ = (Δ, e) 加上 Q_θ。
2. **條件一**：要能寫成 Δ = f(P, e)，也就是給定可觀測分布與雜訊模型，理想差距就唯一確定（雜訊映射在相關觀測量上可逆）。這是我們要明說的假設；不成立時，識別區域要另外定義。
3. **條件二**：原文的 𝒜 是事先給定的固定集合。本專案的探針會根據資料縮小可容許的雜訊集合。處理方式是把探針輸出併入 P（P 是目標加探針的聯合分布），讓 𝒜 仍然是固定的 𝓔，由 P 的形式本身排除不相容的雜訊。這一步是我們的推導，要寫出來，不能說是原文的。
4. **另一個要明說的建模選擇**：在本專案中，電路已知，所以理想差距在原理上是確定的數。我們把它當成未知，是因為規則禁止探針讀理想值，而且目標電路在實務上無法經典模擬。這個選擇要寫進定義。
- 「observationally equivalent」的經典出處可能是 Rothenberg (1971, Econometrica)，但**未查證**，查證前不要引。

計畫 v0.3 第 2 節已依此改寫（見計畫 v0.4）。

## 3. Armstrong & Kolesár (2020)

來源：arXiv 1606.01200（<https://arxiv.org/abs/1606.01200v1>）、ar5iv HTML。
- 開頭："We consider the problem of constructing honest confidence intervals (CIs) for a scalar parameter of interest."
- 第 2 節：區間形式為 估計值 ± cv₁₋α(t) × 標準誤。cv₁₋α(t) 是 "1−α quantile of the folded normal distribution"，也就是 |N(t,1)|，t 是最壞偏差與標準誤之比。
- 第 2 節：函數類別 F(M) "consists of functions with" p 階導數受 M 限制。最壞偏差定義為在 F 上的上確界。
- 第 1 節：作者 "require that the CIs cover the true parameter asymptotically at the nominal level uniformly over the parameter space."

**結論**
- 偏差感知認證的區間形式可以直接引用。
- 但它的最壞偏差來自**先驗**函數類別，本專案的 B 來自**探針資料**。覆蓋率不能直接繼承，需要自己補一步，例如同時控制探針與目標兩個區間的聯合覆蓋。這要寫進 Part 1c 的推導目標。

## 4. Scavino (2026)：最接近的前作

來源：<https://arxiv.org/pdf/2607.02888>（2026-07-02 版本，作者 Vicenzo Scavino，獨立研究者）。

**書目問題（屬於舊專案，要另外處理）**
- 上一版參考文獻對 arXiv 2607.02888 寫的標題是 "Accuracy, Decision Risk, and Sampling Cost in Quantum Error Mitigation"，作者 "Scavino Alfaro, Vicenzo"。
- 現在 arXiv PDF 的標題是 "Decision Kernels for Quantum Error Mitigation: Why Accuracy Gains Need Not Improve Downstream Decisions"，作者 "Vicenzo Scavino"。
- 可能是改版改了標題，但沒有查到版本紀錄。本 repo 的 references.bib 已改用現行標題並加註。**舊論文 main_v2.tex 的這筆引用要在舊專案收尾時核對。**

**內容**（摘要級，加部分段落）
- 決策只取決於差距；定義 decision kernel Σ_m = L K_m Lᵀ；偏差經由有效邊際 μ_m = Δ + L a_m 進入。
- 明確區分 common-mode（被對比映射 L 消掉）與差異偏差。這和上一版 Proposition 1 的方向高度重疊。
- 固定總 shot 預算，非適應性分配。
- 有目標差距的可識別性條件（Corollary C.1："Then the target gaps are identifiable under the chosen primitive measurements."）。
- 有診斷量 DRI、GRI、GVS。關於 GVS："The ratio GVS is only a diagnostic of how much ambient covariance survives projection into the chosen gap contrasts."
- 有一個小型硬體壓力測試："A pre-registered hardware micro-cell stress test."；"The hardware run is not used to support the primary simulation claims."
- **沒有**執行時偵測偏差或認證決策的方法。它的 Algorithm 1 把估計的殘差偏差 â_m 當輸入，沒有說明怎麼取得。它也沒有信賴區間分析，只寫了 "pointwise marginals, variances, confidence intervals, and MSE do not suffice"。
- 它列出的未來工作包括："Sequential allocation, stopping rules, and best-arm-identification style fixed-confidence guarantees"。

**對本專案的意義**
- 好消息：「執行時能不能看到差異偏差」正是它留下的空白。它把 â_m 當已知輸入，本專案問的就是 â_m 能不能在同一預算內得到、什麼時候原理上得不到。
- 風險：它的 Corollary C.1（目標差距可識別性）和本專案的「盲」定義可能重疊；診斷量 DRI、GRI、GVS 也可能被視為探針。**必須讀它的附錄 C 和第 10 節全文**，在相關研究表中逐格寫清楚差異，不能寫「它沒有做 X」，除非原文可查證。
- 上一版 Proposition 1（Δ_m > √γ Δ_r）和它的有效邊際理論有重疊。下一篇延伸 Proposition 1 時要引用並比較它。
