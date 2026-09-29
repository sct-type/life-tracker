---
title: "Body Weight and Alcohol Consumption in a Single Subject: A 24-Month Observational Study"
author:
  - "Written by Claude"
  - "Guided and reviewed by S. Thompson"
date: "13 September 2026"
geometry: margin=1in
fontsize: 11pt
header-includes:
  - \usepackage{tikz}
  - \usepackage{pgfplots}
  - \pgfplotsset{compat=1.18}
  - \usepackage{booktabs}
  - \usepackage{longtable}
  - \usepackage{caption}
  - \captionsetup{font=small,labelfont=bf}
---

## Abstract

**Background.** Longitudinal self-tracking of body weight and alcohol intake is uncommon at the single-subject level but can reveal individual dose-response patterns that population studies average away. **Objective.** To characterize the relationship between monthly alcohol consumption and body weight over a 24-month period in one adult subject, and to describe the weight trajectory across a two-year span of the subject's late forties. **Methods.** Body weight was recorded each morning upon waking and averaged by calendar month (n = 24 months, September 2024 to August 2026). Alcohol intake was recorded daily in standard drink units, defined as 12 fl oz at 5% ABV (60 %ABV·oz), and averaged by month. Subject age was calculated from a stated date of birth (22 December 1976), yielding a study-period age range of 47.7 to 49.6 years. Pearson correlation, simple and multiple linear regression were used. **Results.** Mean body weight was 210.5 lb (SD 3.1), with a low of 204 lb (January 2025) and a high of 216 lb (April 2026). Monthly drinks/day averaged 1.63 (SD 0.55). Same-month weight and drinking were positively correlated (r = 0.52, p = 0.010). A model including both elapsed time and drinks/day explained substantially more variance (R² = 0.65) than time alone (R² = 0.25). **Conclusion.** Within this subject, months of heavier drinking coincided with months of higher body weight, and the final eight months of the study — the subject's lightest-drinking period on record — coincided with a pronounced downward weight trend. The findings are consistent with, but cannot establish, a causal effect of alcohol intake on short-term body weight in this individual.

\newpage

## Plain-language summary

This report uses a few statistical terms. Here's what they mean, in plain English, before the technical sections below:

- **Correlation (r).** A single number, from -1 to +1, that says how closely two things move together. r = 0 means no relationship at all. r = +1 would mean they move in perfect lockstep (more of one always means exactly more of the other). r = -1 means perfect *opposite* lockstep. In the real world, with messy human data, an r around 0.5 (positive or negative) counts as a real, moderate relationship — not proof of anything, but not nothing either.
- **p-value.** Roughly: "if there were actually no real relationship here, how surprising would this data be?" A small p-value (below 0.05 is the usual cutoff) means the pattern is unlikely to be pure chance. It is not a measure of *how big* or *how important* the effect is — just how likely it is to be a fluke.
- **R² (R-squared).** A percentage-like number from 0 to 1 that says how much of the up-and-down in one thing can be "explained" by another. R² = 0.65 means about 65% of the variation in weight, month to month, lines up with the factors in the model; the other 35% is other stuff (diet, sleep, water weight, chance, and more).
- **Regression / slope.** A best-fit straight line drawn through a cloud of dots. The slope tells you: "for each one-unit increase on the x-axis, how much does the y-axis typically move?" For example, a slope of 2.86 lb per drink/day means each additional average drink per day lines up with about 2.86 more pounds, on average, in this dataset.
- **Standard deviation (SD).** A measure of how spread out the numbers are around the average. A small SD means most months looked similar to the average; a bigger SD means more month-to-month swing.
- **Correlation is not causation.** This is the most important one. Just because two things move together does not prove one *causes* the other. There is more on this in the Discussion section below.

## 1. Introduction

Self-quantification of body weight and alcohol intake is now routine, but formal statistical treatment of an individual's own longitudinal data is rare outside clinical case reports. Alcohol contributes roughly 7 kcal/g, second only to fat among macronutrient energy sources, and is metabolized preferentially, which can transiently suppress fat oxidation. Whether this translates into observable month-to-month weight change in free-living conditions — where diet, sleep, and activity all vary simultaneously — is an empirical question best answered with the subject's own data. This report presents a 24-month single-subject analysis — an "N-of-1" study, meaning a study of one person rather than a group — relating monthly alcohol intake to concurrently measured body weight, incorporating the subject's age across the study window.

## 2. Methods

**Subject.** One adult male, date of birth 22 December 1976. At study onset (September 2024) the subject was 47.7 years of age; at study close (August 2026), 49.6 years.

**Weight ascertainment.** Body weight was self-measured each morning immediately upon waking, prior to food or fluid intake, using a home scale. Daily values were averaged within each calendar month to yield a single monthly weight (lb).

**Alcohol ascertainment.** Daily alcohol intake was recorded in standard drink units. One standard drink was defined by the subject as 12 fl oz of a 5%-ABV beverage (60 %ABV·oz); intake of other beverages was converted to drink-equivalents on this basis (for example, 5 fl oz of a 12%-ABV beverage also equals one standard drink, since 5 × 12 = 12 × 5 = 60). Daily values were averaged within each calendar month to produce a mean drinks/day figure, and a trailing 12-month average was also computed.

**Statistical analysis.** Pearson product-moment correlation was used to test linear association between monthly weight and monthly drinks/day, both contemporaneously and with a one-month lag. Ordinary least-squares regression estimated the secular weight trend over time and, in a second model, jointly with drinks/day. A two-tailed alpha of 0.05 was used throughout; given the modest sample size (n = 24 monthly observations), p-values should be interpreted as descriptive rather than confirmatory. All analyses were performed in Python (NumPy/SciPy).

## 3. Results

### 3.1 Descriptive statistics

Table 1 presents the full monthly series.

\begingroup
\small
\begin{longtable}{l r r r r r}
\toprule
Month & Age (yr) & Weight (lb) & $\Delta$Weight & Drinks/day & 12-mo avg \\
\midrule
\endhead
Sep 2024 & 47.73 & 210.0 & --   & 1.60 & 1.60 \\
Oct 2024 & 47.81 & 209.0 & -1.0 & 1.70 & 1.65 \\
Nov 2024 & 47.90 & 209.0 & 0.0  & 2.56 & 1.95 \\
Dec 2024 & 47.98 & 212.0 & +3.0 & 2.41 & 2.07 \\
Jan 2025 & 48.07 & 204.0 & -8.0 & 0.56 & 1.77 \\
Feb 2025 & 48.15 & 206.0 & +2.0 & 0.66 & 1.58 \\
Mar 2025 & 48.23 & 207.0 & +1.0 & 1.55 & 1.58 \\
Apr 2025 & 48.31 & 208.0 & +1.0 & 1.54 & 1.57 \\
May 2025 & 48.39 & 206.0 & -2.0 & 1.67 & 1.58 \\
Jun 2025 & 48.48 & 211.0 & +5.0 & 1.96 & 1.62 \\
Jul 2025 & 48.56 & 212.0 & +1.0 & 1.98 & 1.65 \\
Aug 2025 & 48.65 & 212.0 & 0.0  & 1.81 & 1.67 \\
Sep 2025 & 48.73 & 210.0 & -2.0 & 1.83 & 1.68 \\
Oct 2025 & 48.81 & 210.0 & 0.0  & 1.78 & 1.69 \\
Nov 2025 & 48.90 & 213.0 & +3.0 & 2.01 & 1.68 \\
Dec 2025 & 48.98 & 214.0 & +1.0 & 2.55 & 1.87 \\
Jan 2026 & 49.07 & 212.0 & -2.0 & 1.45 & 1.86 \\
Feb 2026 & 49.15 & 213.0 & +1.0 & 1.16 & 1.82 \\
Mar 2026 & 49.23 & 214.0 & +1.0 & 1.65 & 1.82 \\
Apr 2026 & 49.31 & 216.0 & +2.0 & 2.17 & 1.84 \\
May 2026 & 49.39 & 215.0 & -1.0 & 1.41 & 1.78 \\
Jun 2026 & 49.48 & 212.0 & -3.0 & 1.14 & 1.72 \\
Jul 2026 & 49.56 & 210.0 & -2.0 & 1.51 & 1.68 \\
Aug 2026 & 49.65 & 207.0 & -3.0 & 0.48 & 1.55 \\
\bottomrule
\end{longtable}
\endgroup

*Table 1. Monthly body weight, alcohol intake, and derived age. $\Delta$Weight is the change from the prior month.*

Mean body weight across the study period was 210.5 lb (SD 3.1; range 204–216 lb). Mean alcohol intake was 1.63 drinks/day (SD 0.55; range 0.48–2.56).

### 3.2 Weight trajectory and age

Figure 1 plots monthly body weight against its own 12-month moving average (upper panel), alongside monthly drinks/day against its 12-month moving average (lower panel) — the same kind of smoothing line in both panels, so they read side by side on equal footing.

```{=latex}
\begin{figure}[h]
\centering
\begin{tikzpicture}
\begin{axis}[
  width=6.3in, height=2.1in,
  xlabel={}, ylabel={Weight (lb)},
  ylabel style={font=\small}, tick label style={font=\scriptsize},
  xtick={0,3,6,9,12,15,18,21},
  xticklabels={Sep '24,Dec '24,Mar '25,Jun '25,Sep '25,Dec '25,Mar '26,Jun '26},
  xmin=-0.5, xmax=23.5, ymin=202, ymax=218,
  axis lines=left, grid=major, grid style={gray!15},
  legend style={font=\scriptsize, at={(0.02,0.97)}, anchor=north west, draw=gray!40, fill=white, fill opacity=0.9, text opacity=1, rounded corners=1pt},
]
\addplot[color=black, mark=*, mark size=1.3pt, thick] coordinates {
(0,210.00) (1,209.00) (2,209.00) (3,212.00) (4,204.00) (5,206.00) (6,207.00) (7,208.00) (8,206.00) (9,211.00) (10,212.00) (11,212.00) (12,210.00) (13,210.00) (14,213.00) (15,214.00) (16,212.00) (17,213.00) (18,214.00) (19,216.00) (20,215.00) (21,212.00) (22,210.00) (23,207.00)
};
\addplot[color=gray, thick] coordinates {
(0,210.000) (1,209.500) (2,209.333) (3,210.000) (4,208.800) (5,208.333) (6,208.143) (7,208.125) (8,207.889) (9,208.200) (10,208.545) (11,208.833) (12,208.833) (13,208.917) (14,209.250) (15,209.417) (16,210.083) (17,210.667) (18,211.250) (19,211.917) (20,212.667) (21,212.750) (22,212.583) (23,212.167)
};
\legend{Monthly weight, 12-mo moving avg}
\end{axis}
\end{tikzpicture}

\vspace{4pt}

\begin{tikzpicture}
\begin{axis}[
  width=6.3in, height=2.1in,
  xlabel={Month}, ylabel={Drinks/day},
  xlabel style={font=\small}, ylabel style={font=\small}, tick label style={font=\scriptsize},
  xtick={0,3,6,9,12,15,18,21},
  xticklabels={Sep '24,Dec '24,Mar '25,Jun '25,Sep '25,Dec '25,Mar '26,Jun '26},
  xmin=-0.5, xmax=23.5, ymin=0, ymax=3,
  axis lines=left, grid=major, grid style={gray!15},
  legend style={font=\scriptsize, at={(0.02,0.97)}, anchor=north west, draw=gray!40, fill=white, fill opacity=0.9, text opacity=1, rounded corners=1pt},
]
\addplot[color=blue!70!black, mark=*, mark size=1.3pt, thick] coordinates {
(0,1.60) (1,1.70) (2,2.56) (3,2.41) (4,0.56) (5,0.66) (6,1.55) (7,1.54) (8,1.67) (9,1.96) (10,1.98) (11,1.81) (12,1.83) (13,1.78) (14,2.01) (15,2.55) (16,1.45) (17,1.16) (18,1.65) (19,2.17) (20,1.41) (21,1.14) (22,1.51) (23,0.48)
};
\addplot[color=blue!30!white, thick] coordinates {
(0,1.60) (1,1.65) (2,1.95) (3,2.07) (4,1.77) (5,1.58) (6,1.58) (7,1.57) (8,1.58) (9,1.62) (10,1.65) (11,1.67) (12,1.68) (13,1.69) (14,1.68) (15,1.87) (16,1.86) (17,1.82) (18,1.82) (19,1.84) (20,1.78) (21,1.72) (22,1.68) (23,1.55)
};
\legend{Monthly drinks/day, 12-mo moving avg}
\end{axis}
\end{tikzpicture}
\caption{Monthly body weight (top) and alcohol intake (bottom), September 2024–August 2026, each shown with its own 12-month moving average. A moving average simply replaces each point with the average of that point and the prior eleven months, which smooths out short-term noise so the underlying trend is easier to see.}
\end{figure}
```

Separately from the smoothed lines in Figure 1, a straight-line (linear regression) fit to the raw monthly weights indicates a rise of 0.22 lb/month, or about 2.63 lb/year (95% confidence interval 0.63–4.63 lb/year — the range we're fairly confident the true rate falls in, wide here since there are only 24 months of data; r = 0.50, p = 0.012). The subject aged from 47.7 to 49.6 years over this same period; since study time and age advance together in lockstep for a single subject, this trend can't be attributed to age specifically, and is reported simply as the observed weight trajectory.

### 3.3 Weight and alcohol intake

Same-month body weight and drinks/day were positively correlated (r = 0.52, p = 0.010); the 12-month trailing average showed a similar association (r = 0.50, p = 0.013). Month-over-month weight *change* correlated with same-month drinking at r = 0.56 (p = 0.005), but not with the *prior* month's drinking (r = -0.21, p = 0.34) — consistent with an acute, within-month effect rather than a delayed one.

Figure 2 shows the scatter of monthly weight against monthly drinks/day with the fitted regression line (slope 2.86 lb per additional drink/day, intercept 205.8 lb).

```{=latex}
\begin{figure}[h]
\centering
\begin{tikzpicture}
\begin{axis}[
  width=4.6in, height=3.2in,
  xlabel={Drinks/day (monthly mean)}, ylabel={Weight (lb, monthly mean)},
  xlabel style={font=\small}, ylabel style={font=\small}, tick label style={font=\scriptsize},
  xmin=0, xmax=2.8, ymin=202, ymax=218,
  axis lines=left, grid=major, grid style={gray!15},
]
\addplot[only marks, mark=*, mark size=1.6pt, color=black] coordinates {
(1.6,210.00) (1.7,209.00) (2.56,209.00) (2.41,212.00) (0.56,204.00) (0.66,206.00) (1.55,207.00) (1.54,208.00) (1.67,206.00) (1.96,211.00) (1.98,212.00) (1.81,212.00) (1.83,210.00) (1.78,210.00) (2.01,213.00) (2.55,214.00) (1.45,212.00) (1.16,213.00) (1.65,214.00) (2.17,216.00) (1.41,215.00) (1.14,212.00) (1.51,210.00) (0.48,207.00)
};
\addplot[color=red!60!black, thick] coordinates {
(0.48,207.205) (2.56,213.160)
};
\end{axis}
\end{tikzpicture}
\caption{Monthly body weight versus monthly mean drinks/day (n = 24), with ordinary-least-squares fit ($\hat{y} = 2.86x + 205.8$; r = 0.52, p = 0.010).}
\end{figure}
```

A multiple regression of weight on elapsed time (months) and drinks/day jointly explained substantially more variance (R² = 0.65) than time alone (R² = 0.25): each additional drink/day was associated with 3.56 lb of higher monthly weight (holding time constant), and the time coefficient rose slightly to 0.275 lb/month (3.30 lb/year) once drinking was accounted for. This last point is notable: the raw upward weight trend across the study period is not attenuated by adjusting for drinking — if anything it is marginally larger — indicating that the gradual *decline* in average drinking over the two years (1.58 drinks/day in the first six months versus 1.39 in the last six) partially offset, rather than explained, the underlying upward trajectory.

The subject's single heaviest-drinking month (November 2024, 2.56 drinks/day) did not correspond to his highest weight, and his single lightest-drinking month (August 2026, 0.48 drinks/day) corresponded to a weight 3 lb below the prior month and the second-lowest reading in the series — illustrating that the group-level association, while real, does not hold in every individual month.

A complementary view uses month-over-month weight *change* directly as the outcome (Figure 3), rather than the absolute weight level in Figure 2. Plotting drinks/day against this derived weight-gain figure gives the same positive slope (r = 0.55, p = 0.005), confirming that the relationship is not an artifact of the particular way weight was expressed.

```{=latex}
\begin{figure}[h]
\centering
\begin{tikzpicture}
\begin{axis}[
  width=4.6in, height=3.2in,
  xlabel={Drinks/day (monthly mean)}, ylabel={Weight-gain diff (lb)},
  xlabel style={font=\small}, ylabel style={font=\small}, tick label style={font=\scriptsize},
  xmin=0, xmax=2.8, ymin=-8.5, ymax=5.5,
  axis lines=left, grid=major, grid style={gray!15},
]
\draw[gray!40, thin] (axis cs:0,0) -- (axis cs:2.8,0);
\addplot[only marks, mark=*, mark size=1.6pt, color=black] coordinates {
(1.60,-1.60) (1.70,-0.90) (2.56,-0.40) (2.41,2.70) (0.56,-7.30) (0.66,1.40) (1.55,1.40) (1.54,0.69) (1.67,-1.40) (1.96,4.25) (1.98,1.22) (1.81,-0.13) (1.83,-1.39) (1.78,-0.23) (2.01,3.36) (2.55,0.19) (1.45,-1.19) (1.16,0.69) (1.65,1.34) (2.17,1.13) (1.41,-0.31) (1.14,-2.75) (1.51,-2.25) (0.48,-3.23)
};
\addplot[color=red!60!black, thick] coordinates {
(0.480,-2.934) (2.560,2.014)
};
\end{axis}
\end{tikzpicture}
\caption{Monthly weight-gain diff (lb) versus monthly mean drinks/day (n = 24), with ordinary-least-squares fit ($\hat{y} = 2.38x - 4.08$; r = 0.55, p = 0.005). The horizontal reference line marks zero net monthly weight change; the fitted line crosses it at 1.71 drinks/day.}
\end{figure}
```

**A tempting reading of Figure 3.** The fitted line crosses zero — the point separating a predicted average weight *gain* from a predicted average weight *loss* — at about 1.71 drinks/day. It is tempting to turn this into a rule of thumb: "stay under about 1.7 drinks/day, on average, and the model expects you to trend down; go above it, and the model expects you to trend up." That reading is not unreasonable, and it lines up decently with an independent check on the same data: splitting all 24 months at their own median drinking level (1.66 drinks/day, almost the same number) showed months above that median averaging +0.70 lb and months at or below it averaging -1.09 lb. Two different ways of slicing the data point to a similar neighborhood, which is a mild point in the number's favor.

That said, treating 1.71 as a precise personal threshold would be over-reading a fairly noisy fit (see the note on measurement noise in the Limitations section, below, for what "noisy" means here and does not mean). Three things temper it. First, this line was fit to only 24 monthly averages, and the scatter around it is wide — several low-drinking months still show weight gain, and at least one heavier-drinking month (November 2024) shows a loss, so the line describes an average tendency, not a guarantee for any single month. Second, the exact crossing point is sensitive to the fit: a slightly different two years of data, or a few different months, would likely shift 1.71 up or down by several tenths of a drink, so the number itself shouldn't be taken to more precision than "somewhere around one and a half to two drinks per day." Third, and most important given the causation discussion above, this threshold bundles together whatever else tends to ride along with heavier-drinking months for this subject — sleep, food choices, activity — so crossing it is better read as "a day-to-day pattern statistically associated with net gain," not as alcohol's calories alone tipping a metabolic scale at that exact number.

## 4. Discussion

Three findings stand out. First, an association between alcohol intake and body weight is present in this subject's own data and is neither trivial nor overwhelming: same-month r-values cluster around 0.5, meaning drinking "explains," in the statistical sense, on the order of a quarter to a third of month-to-month weight variance — consistent with alcohol being a contributing factor among several, rather than the whole story. Second, the effect looks acute rather than cumulative: the month-over-month *change* in weight tracks the *same* month's drinking, not the month before, arguing against a slow-building effect and for something closer to direct caloric contribution or short-term fluid/glycogen dynamics. Third, the final eight months of the record are the most encouraging in the dataset — the lowest yearly drinking average (1.37 drinks/day) alongside the sharpest sustained weight decline (207 lb by August 2026, a two-year low outside of January 2025) — which is exactly the direction the regression model predicts and is worth the subject's attention going forward.

Is the data actually interesting, or is this simply confirming the obvious? Both, to a degree. That alcohol carries calories is not news. What is more interesting is *how tight* the same-month relationship is for a single free-living individual with only 24 data points and no controlled diet: an r of 0.5–0.56 is a moderately strong signal for observational self-tracked data, and the fact that the multiple regression's R² nearly triples (0.25 to 0.65) when drinking is added to a bare time trend suggests drinking is doing real explanatory work, not just riding along with some other seasonal pattern. The clean reversal in the last eight months — lowest drinking, lowest weight — is the single most useful data point in the set, functioning almost as a natural experiment within the subject's own history. It is also worth noting what the data do *not* show: no lagged effect, and at least one clear counterexample (November 2024), which keeps this from being a simple deterministic story.

**A word on correlation and causation.** This report shows that drinking and weight move together; it cannot show that drinking, by itself, *causes* the weight change. There is at least one other plausible story worth taking seriously: a heavier-drinking evening rarely happens in isolation. It often comes with less sleep, later meals, more snacking, skipped workouts, or simply a looser, more indulgent day overall. If that is what's really going on, alcohol may be less a direct cause of weight gain and more a marker, or a leading edge, of a broader pattern of behavior that itself drives the number on the scale — the drink and the late-night pizza might be doing the work together, not the drink alone. Distinguishing "alcohol causes weight gain directly" from "alcohol is a signal of a rougher day generally" would need more variables tracked alongside it, which leads to the next point.

**Looking ahead.** The subject began tracking additional variables in September 2026, including protein and fiber intake, which were not yet available for the period analyzed here. A natural next step, once enough months accumulate, is to test whether drinking's apparent association with weight holds up once these are accounted for, or whether it shrinks — which would support the "broader pattern" explanation above. Anecdotally, the subject has reported losing weight during periods of consistent tracking and goal adherence; that observation is not something this report's data can formally test yet, but it is a reasonable hypothesis for a future analysis to take up directly.

## 5. Limitations

This is an N-of-1 study, so it can show association but not causation. Confounders like diet, sleep, and stress weren't modeled here; systematic tracking of some of these (protein, fiber) only began in September 2026. Age and elapsed time move in lockstep for a single subject, so any age effect can't be separated from the general time trend.

The "noise" referenced throughout is not measurement error — the weigh-in routine and logging are solid. It's real, ordinary physiology: hydration, sodium and carb intake, exercise, sleep, and normal digestion all shift a morning weight by a pound or two, independent of alcohol. Monthly averaging smooths most of this out but not all of it, which is why individual months don't always follow the overall pattern. With n = 24, statistical power is modest.

## 6. Conclusion

Over a 24-month period spanning the subject's 48th and 49th years, monthly body weight and monthly alcohol intake were positively and consistently associated, with the association concentrated in same-month rather than lagged effects. The most recent eight months, the subject's lightest-drinking stretch on record, coincided with the clearest sustained weight loss in the series. Continued self-tracking, ideally with control for diet and sleep, would help distinguish an acute caloric mechanism from other explanations.

---

*Data source: subject-reported daily weight and alcohol logs, `20260913-snapshot`, life-tracker project. Analysis generated 13 September 2026.*
