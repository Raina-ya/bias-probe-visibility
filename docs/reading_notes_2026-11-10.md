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

## 4. Scavino (2026)：最接近的前作（2026-11-10 第二次閱讀，含附錄 C 與第 10 節）

讀取範圍：arXiv PDF 全文 178,598 字元，分兩段讀完（0–100,000、100,000–結尾）。另外讀了 arXiv 摘要頁、arXiv HTML 頁、作者的 GitHub README。
讀取工具是摘錄式的，以下「據我們所讀」都是指這個範圍。

### 4.1 問題一：舊論文引的標題在 arXiv 版本紀錄裡存在過嗎？

**答：依 arXiv 版本紀錄，沒有存在過。所以舊論文的引用標題和 arXiv 紀錄不符，舊專案要改引用。**

觀察到的事實：
- arXiv 摘要頁 <https://arxiv.org/abs/2607.02888>：只列出一個版本，"This version: v1 2026-07-03"，沒有 v2 或更新版本。標題是 "Decision Kernels for Quantum Error Mitigation: Why Accuracy Gains Need Not Improve Downstream Decisions"，作者是 "Vicenzo Scavino"。
- arXiv PDF 與 HTML 頁實際讀取時，顯示的都是同一個新標題，日期 July 2, 2026。
- 舊標題 "Accuracy, Decision Risk, and Sampling Cost in Quantum Error Mitigation" 出現在兩個非 arXiv 版本紀錄的地方：
  1. 搜尋引擎索引裡 arxiv.org/html/2607.02888 的頁面標題（但實際讀取該頁時顯示的是新標題）；
  2. 作者的 GitHub repo README 標題（<https://github.com/vicenzoscavino1999/decision-aware-qem>）。README 提到的是作者自己的稿件版本號（"manuscript v45"、"The current manuscript (v47)"），不是 arXiv 版本。
- 結論依你給的二分法：arXiv 紀錄中從沒存在過，所以算引錯。但舊標題確實是作者在 GitHub 上用的標題，這可以說明舊論文的標題從哪裡來。
- 建議舊專案改成 arXiv 上的標題與作者名 "Vicenzo Scavino"，arXiv ID 2607.02888 不變。本 repo 的 references.bib 已經這樣寫。

### 4.2 問題二：全文有沒有說明怎麼取得偏差估計？

**答：據我們所讀，它未說明殘差偏差 a_m（或估計值 â_m）如何取得。**

依據（逐字摘錄）：
- 第 3 節，式 (8)：「$a_m$ denotes the deterministic, budget-independent residual bias of method m」。這是定義，不是估計方法。
- Algorithm 1 的輸入行把它列為已知輸入：「Candidate methods $m \in \{\text{Raw}, \text{ZNE}, \text{CDR}, \text{PEC}\}$ ; budget B; estimated residual bias $\widehat{a}_m$」……「estimated covariance $\widehat{K}_m$ ; contrast matrix L; estimated landscape $\widehat{f}$ ; decision rule $\delta$」。
- 第 8.2 節，Theorem 8.4：「or lower bounded by certified values $\underline{\mu}_i > 0$」。這是假設已有認證值，沒有給取得方法。
- 第 8.4 節（PEC）：「In the ideal scalar-overhead PEC model with correct noise characterization」，也就是假設 a_PEC = 0。
- 附錄 A 有兩處相關但不是偏差估計的文字：
  - 「In hardware practice, $G_r$ may」……「instead be obtained by subtracting a high-accuracy pilot estimate」，講的是差距樣本；
  - 式 (180)「using a high-accuracy reference for $\mu_m$」，講的是模擬中用高精度參考值當邊際。

### 4.3 問題三：逐欄比較表

| 項目 | Scavino (2026)，據我們所讀 | 本專案（計畫 v0.4，尚未執行） |
|---|---|---|
| 固定預算 | 有。總 shot 預算 B、固定分配比例、非適應性分配。原文把適應性分配列為範圍外："Sequential allocation, stopping rules, and best-arm-identification style fixed-confidence guarantees"（第 13 節，列為未來工作） | 有。目標、探針、校準、folding 全部從同一總預算扣除 |
| 評估決策 | 有。gap-based 決策（argmin、ranking、top-k），決策錯誤機率 R_m(B)，診斷量 GRI 是「存在某個差距翻號」的機率 | 有。top-1 決策；但主要終點是「可見性預測與觀測是否一致」，不是決策錯誤率本身 |
| 執行時偵測偏差 | 據我們所讀，未說明 â_m 如何取得（見 4.2）。三個診斷量中：DRI 與 GRI 需要邊際 μ_m，模擬中來自高精度參考值；GVS 只需要 K_m 與 L，原文說它 "does not include the margins $\mu_m$" | 核心問題：在不讀理想值、且計入預算的前提下，探針能否偵測差異偏差，以及何時原理上不能 |
| 可識別性條件 | Corollary C.1：假設 "the primitive laws $p_{s,\theta}$ are smooth"，若 "Gh = 0 for every $h \in \ker \overline{\mathcal{I}}(w, \theta)$"，則 "the target gaps are identifiable under the chosen primitive measurements"；適用範圍 "in the locally efficient, identifiable, small-margin, and realizable case"；用途是推出 shot 層級的指數 $\min_i \mu_i^2/(2\Sigma_{\text{eff},ii}(w))$。primitive measurements 原文未正式定義；θ 包含哪些量，據我們所讀未明確 | 識別區域 {f(P, e′) : e′ ∈ 𝓔}（Imbens & Manski 形式）；雜訊 e 是未知量，𝓔 是模型類別，P 含探針輸出 |
| 和我們的「盲」定義差在哪 | 它的條件是**局部**的：在給定 θ 附近，用 Fisher 資訊的零空間判斷差距能否被估計，目的是算錯誤指數 | 我們的定義是**全域、看符號**的：整個識別區域是否同時含正值與非正值。另外明確把雜訊當未知擾動量，並讓探針改變 P |

**表格以外、需要標明是我們推論的兩點**
- 如果 Scavino 的 θ 包含雜訊參數，那麼 Corollary C.1 的零空間條件可以看成我們「可見」的局部版本。到時候論文要引用它，並說明我們的全域符號版本和它的差別。θ 的內容要讀附錄 C 的完整推導才能確定，目前只讀到摘錄。
- GVS 不含邊際，所以依其定義看不到偏差；DRI、GRI 需要邊際（真實差距）。照本專案「探針不能讀理想值」的規則，DRI、GRI 不能當執行時探針，GVS 可以算但不含偏差資訊。這是我們從原文定義推出來的，不是原文的說法。

### 4.4 其他事實
- 硬體部分：原文說小型硬體壓力測試的決策準則沒有達成："projected ranking error below 0.25 times the predicted risk margin, at an upper 95% cluster-bootstrap bound"（未達成），硬體結果支持的是 "the pullback prediction $\Sigma^{pred}$ versus the directly estimated covariance $\widehat{\Sigma}$, not decision advantage"。另見 "The hardware run is not used to support the primary simulation claims."
- 和上一版 Proposition 1 的重疊：有效邊際 μ_m = Δ + L a_m 與 common-mode 被 L 消掉，和 Proposition 1 的差距寫法高度一致。延伸 Proposition 1 時要引用它並比較。

### 4.5 新穎性（表格填完後才談）
- 據我們所讀，Scavino 把偏差當成已給定的輸入，沒有說明執行時怎麼取得；它的可識別性條件是局部的、針對差距估計效率。
- 本專案的「同一預算內、不讀理想值的探針能否看到差異偏差，以及全域意義上何時原理上看不到」，在它的範圍之外。
- 但不能寫「它沒有做執行時偵測」，只能寫「據我們所讀，它未說明偏差估計的取得方式」。
