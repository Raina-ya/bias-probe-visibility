# Reading Notes on Key Sources

These notes record the passages of four sources that bear directly on the definitions and novelty claims of this project: Lipsitch et al. (2010), Imbens and Manski (2004), Armstrong and Kolesar (2020), and Scavino (2026). Each source is quoted from its original PDF or HTML, and only relevant passages are extracted.

Use of quotations. The English quotations below were extracted by a page-reading tool. Before any quotation enters the paper, it must be checked once more against the original PDF. The tool occasionally splits long sentences; the Imbens and Manski PDF is OCR text, so symbols such as theta and "element of" appear distorted.

Division of reading. Chen et al. (2023) and Imbens and Manski (2004) are also read in full by the project owner. These notes cover Lipsitch, Armstrong and Kolesar, and Scavino, and check whether the original definition in Imbens and Manski supports the form used in the research plan.

## 1. Lipsitch, Tchetgen Tchetgen and Cohen (2010)

Citation as printed. "Epidemiology • Volume 21, Number 3"; "(Epidemiology 2010;21: 383–388)"; "DOI: 10.1097/EDE.0b013e3181d61eeb".
Source: https://www.meb.ki.se/biostat/cc2024/papers/extras/Lipsitch%20EPI%202010%20neg%20controls%20for%20detecting%20confounding%20and%20bias.pdf

Original wording of the validity condition. All quotations are from the section "CHOICE OF NEGATIVE CONTROLS TO DETECT CONFOUNDING IN EPIDEMIOLOGY".

Negative control outcome:
  "Ideally, a negative control outcome (N) should be an outcome such that the set of common causes of exposure A and outcome Y" … "should be as identical as possible to the set of common causes of A and N (Fig. 2)."
  "To the extent that the set of unobserved common causes of A and Y overlaps with the set of unobserved common causes" … "(U) of A and N, we call the negative control outcome N "U-comparable" to Y."
  "If N and Y are U-comparable outcomes (ie, with an identical set of common causes that are associated with A)" … "assuming that N is not caused by A"

Negative control exposure:
  "A negative control exposure B should be an exposure such that the common causes of A and Y are as nearly" … "identical as possible to the common causes of B and Y (Fig. 3)."
  "If A and B are perfectly U-comparable and B does not cause Y,"

Figure captions:
  Fig. 2: "N should ideally have the same incoming arrows as Y, except that A does not cause N;"
  Fig. 3: "B should ideally have the same incoming arrows as A;"

Conclusions
  The original condition is called U-comparability and is defined on a causal graph: the negative control and the target have the same, or as nearly as possible the same, set of unobserved common causes, and the negative control is not affected by the exposure.
  The original text does not contain the phrases "same bias mechanism", "same incomplete set of causal mechanisms" or "same potential sources of bias". Describing the condition as a "shared bias mechanism" is inaccurate and is not used.
  Meaning for this project: U-comparability is a confounding condition from observational epidemiology. Applied to quantum probes, it can only be an analogy. The paper must write "by analogy with U-comparability (Lipsitch et al. 2010)" and give its own quantum condition, for example: the probe statistic and the target gap have nonzero sensitivity to the same noise parameters, and the probe's ideal value is known. This quantum condition is this project's definition and must be stated as such, never attributed to Lipsitch et al.

## 2. Imbens and Manski (2004): checking the form "ideal gap and noise jointly unknown"

Source: https://scholar.harvard.edu/sites/scholar.harvard.edu/files/imbens/files/confidence_intervals_for_partially_identified_parameters.pdf (OCR text; symbols distorted)

Original definitions (Section 2):
  "The distribution P is not known, but a random sample of size N is available, with empirical distribution PN."
  "Let A be a quantity that is known only to belong to a specified set A."
  "The object of interest is the real parameter 0 = f(P, A)." (the OCR reads theta as 0)
  "Then the identification region for f(P, A) is the set {f(P, A'), A' E A}." (E stands for "element of")
  Example (Section 3, means with missing data): "The distribution of Y given W = 0 is unknown; hence, A e [0, 1]."

Not found in the source
  The paper does not formally define "partially identified"; it refers to Manski (2003).
  The paper does not use wording such as "the set of parameter values consistent with the data distribution".
  Tamer (2010) does not use the phrase "observationally equivalent" and does not write a structure as a jointly unknown pair (theta, F).

Assessment: the form "ideal gap and noise jointly unknown" is supported by the source, provided it is written in the Imbens and Manski form and two conditions are stated.
  1. The Imbens and Manski form is theta = f(P, A): an observable distribution P plus an unknown quantity A known only to lie in a set. For this project, let A be the noise e and the set be E; then Delta = f(P, e). This is structurally the same as "ideal gap and noise jointly unknown". The paper should use this form and cite Section 2 of Imbens and Manski, rather than an ad hoc theta = (Delta, e) with a distribution Q_theta.
  2. Condition one: Delta = f(P, e) requires that, given the observable distribution and the noise model, the ideal gap is uniquely determined (the noise map is invertible on the relevant observables). This is an assumption the project must state; where it fails, the identification region must be defined differently.
  3. Condition two: in the source, the set of admissible A is fixed in advance. In this project, probes narrow the admissible noise through data. This is handled by including the probe outputs in P (P is the joint distribution of target and probe outputs), so that the admissible set stays the fixed set E and incompatible noise is excluded by the form of P itself. This step is our own derivation and must be written out, not attributed to the source.
  4. A further modelling choice that must be stated: in this project the circuits are known, so the ideal gap is in principle a fixed number. It is treated as unknown because probes may not read ideal values and the target circuits cannot be simulated classically in practice. This choice belongs in the definitions.
  The classical source for "observationally equivalent" may be Rothenberg (1971, Econometrica); it is unverified and must not be cited until verified.

Section 2 of the research plan follows this form.

## 3. Armstrong and Kolesar (2020)

Source: arXiv 1606.01200 (https://arxiv.org/abs/1606.01200v1) and its ar5iv HTML.
  Opening: "We consider the problem of constructing honest confidence intervals (CIs) for a scalar parameter of interest."
  Section 2: the interval has the form estimate plus or minus cv_{1-alpha}(t) times the standard error, where cv_{1-alpha}(t) is the "1−α quantile of the folded normal distribution", that is, of |N(t,1)|, and t is the ratio of the worst-case bias to the standard error.
  Section 2: the function class F(M) "consists of functions with" a p-th derivative bounded by M; the worst-case bias is the supremum over F.
  Section 1: the authors "require that the CIs cover the true parameter asymptotically at the nominal level uniformly over the parameter space."

Conclusions
  The interval form of the bias-aware certificate can be cited directly.
  Its worst-case bias, however, comes from a function class fixed in advance, whereas B in this project comes from probe data. Coverage cannot be inherited directly; an extra step is needed, for example joint coverage of the probe interval and the target interval. This is a derivation goal of Part 1c.

## 4. Scavino (2026): the closest earlier work

Scope of reading: the full arXiv PDF (178,598 characters, read in two segments), the arXiv abstract page, the arXiv HTML page, and the author's GitHub README. The reading tool extracts passages, so "in what we read" refers to this scope.

### 4.1 Did the title cited by the previous paper ever exist in the arXiv version record?

Answer: according to the arXiv version record, no. The title cited by the previous paper does not match the arXiv record, and the previous project must correct the citation.

Observed facts
  The arXiv abstract page (https://arxiv.org/abs/2607.02888) lists a single version, v1, with no v2 or later. The title is "Decision Kernels for Quantum Error Mitigation: Why Accuracy Gains Need Not Improve Downstream Decisions", and the author is "Vicenzo Scavino".
  The arXiv PDF and HTML pages, when read, both show the same title.
  The earlier title, "Accuracy, Decision Risk, and Sampling Cost in Quantum Error Mitigation", appears in two places outside the arXiv version record:
    1. the page title of arxiv.org/html/2607.02888 in a search-engine index (the page itself, when read, shows the current title);
    2. the title of the author's GitHub README (https://github.com/vicenzoscavino1999/decision-aware-qem). The README refers to the author's own manuscript versions ("manuscript v45", "The current manuscript (v47)"), not to arXiv versions.
  The earlier title never existed in the arXiv record, so the citation counts as incorrect. It is, however, the title the author uses on GitHub, which explains where it came from.
  The previous project should use the arXiv title and the author name "Vicenzo Scavino", keeping arXiv ID 2607.02888. The references.bib of this repository already does so.

### 4.2 Does the full text explain how the bias estimate is obtained?

Answer: in what we read, the paper does not state how the residual bias a_m (or its estimate â_m) is obtained.

Basis (verbatim):
  Section 3, Eq. (8): "$a_m$ denotes the deterministic, budget-independent residual bias of method m". This is a definition, not an estimation method.
  The input line of Algorithm 1 lists it as a given input: "Candidate methods $m \in \{\text{Raw}, \text{ZNE}, \text{CDR}, \text{PEC}\}$ ; budget B; estimated residual bias $\widehat{a}_m$" … "estimated covariance $\widehat{K}_m$ ; contrast matrix L; estimated landscape $\widehat{f}$ ; decision rule $\delta$".
  Section 8.2, Theorem 8.4: "or lower bounded by certified values $\underline{\mu}_i > 0$". This assumes certified values are available and gives no method for obtaining them.
  Section 8.4 (PEC): "In the ideal scalar-overhead PEC model with correct noise characterization", that is, a_PEC = 0 is assumed.
  Appendix A contains two related passages that are not bias estimation:
    "In hardware practice, $G_r$ may" … "instead be obtained by subtracting a high-accuracy pilot estimate", which concerns gap samples;
    Eq. (180), "using a high-accuracy reference for $\mu_m$", which concerns using a high-accuracy reference as the margin in simulation.

### 4.3 Column-by-column comparison

| Aspect | Scavino (2026), in what we read | This project (as planned, not yet executed) |
|---|---|---|
| Fixed budget | Yes. Total shot budget B, fixed allocation fractions, non-adaptive allocation. Adaptive allocation is listed as future work: "Sequential allocation, stopping rules, and best-arm-identification style fixed-confidence guarantees" (Section 13) | Yes. Target, probes, calibration and folding are all charged to one total budget |
| Decision evaluation | Yes. Gap-based decisions (argmin, ranking, top-k), decision error probability R_m(B); the diagnostic GRI is the probability that some gap changes sign | Yes. Top-1 decisions; the primary endpoint, however, is agreement between visibility predictions and observations, not the decision error rate itself |
| Runtime bias detection | In what we read, how â_m is obtained is not stated (section 4.2). Of the three diagnostics, DRI and GRI need the margins mu_m, which in simulation come from high-accuracy references; GVS needs only K_m and L, and the paper says it "does not include the margins $\mu_m$" | The core question: whether probes can detect differential bias without reading ideal values and with their cost charged to the budget, and when they cannot in principle |
| Identifiability condition | Corollary C.1: assuming "the primitive laws $p_{s,\theta}$ are smooth", if "Gh = 0 for every $h \in \ker \overline{\mathcal{I}}(w, \theta)$", then "the target gaps are identifiable under the chosen primitive measurements"; scope "in the locally efficient, identifiable, small-margin, and realizable case"; used to derive the shot-level exponent $\min_i \mu_i^2/(2\Sigma_{\text{eff},ii}(w))$. Primitive measurements are not formally defined; what theta contains is not stated in what we read | Identification region {f(P, e') : e' in E} (Imbens and Manski form); the noise e is unknown, E is a model class, and P includes probe outputs |
| Difference from this project's "blind" | The condition is local: near a given theta, the Fisher-information null space decides whether the gap can be estimated, in order to compute an error exponent | The definition is global and about sign: whether the whole identification region contains both positive and non-positive values. It also treats the noise explicitly as an unknown nuisance and lets probes change P |

Two inferences beyond the table, labelled as ours
  If Scavino's theta includes noise parameters, the null-space condition of Corollary C.1 can be read as a local version of our "visible" condition. The paper must then cite it and explain how our global sign version differs. What theta contains can be settled only by reading the full derivation in Appendix C; so far only extracts have been read.
  GVS does not include the margins, so by its definition it cannot see bias; DRI and GRI need the margins (the true gaps). Under this project's rule that probes may not read ideal values, DRI and GRI cannot serve as runtime probes, and GVS can be computed but carries no bias information. This follows from the definitions in the paper; the paper itself does not say so.

### 4.4 Other facts

Hardware: the paper reports that the decision criterion of its small hardware stress test was not met: "projected ranking error below 0.25 times the predicted risk margin, at an upper 95% cluster-bootstrap bound" (not met). The hardware result supports "the pullback prediction $\Sigma^{pred}$ versus the directly estimated covariance $\widehat{\Sigma}$, not decision advantage". See also: "The hardware run is not used to support the primary simulation claims."
Overlap with Proposition 1 of the previous project: the effective margin mu_m = Delta + L a_m and the cancellation of common-mode shifts by L closely match the gap formulation of Proposition 1. Extending Proposition 1 must cite and compare this paper.

### 4.5 Novelty

In what we read, Scavino treats bias as a given input and does not state how it is obtained at runtime; its identifiability condition is local and concerns the efficiency of gap estimation.
This project's question, whether probes within the same budget and without reading ideal values can see differential bias, and when they are blind in principle in the global sense, lies outside that scope.
The paper may not write "it does not perform runtime detection"; it may write only "in what we read, it does not state how the bias estimate is obtained".
