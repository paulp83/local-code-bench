# club-3090 agent tasks: 20 tasks, configs: thinkingcap-dualfast, thinkingcap-dualfast-xhigh, thinkingcap-dualfast-omp, thinkingcap-dualfast-omp-xhigh, strata-iq4xs, strata-iq4xs-xhigh, strata-iq4xs-omp, strata-iq4xs-omp-xhigh, glm-avar6, glm-avar6-xhigh, glm-avar6-omp, glm-avar6-omp-xhigh

| Config | Draws | Solved | Solve rate (95% CI) | Mean partial | Mean localization | Regressions | Median steps | Median agent min | Tasks/hour | Exit statuses |
|---|---|---|---|---|---|---|---|---|---|---|
| thinkingcap-dualfast | 2 | 23/40 | 57% (42%–71%) | 0.68 | 0.87 | 0 | 36 | 4.4 | 6.97 | Submitted 40 |
| thinkingcap-dualfast-xhigh | 1 | 12/20 | 60% (39%–78%) | 0.71 | 0.89 | 0 | 51 | 7.1 | 4.27 | Submitted 19, LimitsExceeded 1 |
| thinkingcap-dualfast-omp | 2 | 26/40 | 65% (50%–78%) | 0.77 | 0.89 | 0 | 52 | 8.9 | 4.26 | Submitted 40 |
| thinkingcap-dualfast-omp-xhigh | 1 | 12/20 | 60% (39%–78%) | 0.72 | 0.88 | 0 | 70 | 10.1 | 3.17 | Submitted 20 |
| strata-iq4xs | 2 | 31/40 | 78% (62%–88%) | 0.85 | 0.93 | 0 | 38 | 9.7 | 4.26 | Submitted 39, LimitsExceeded 1 |
| strata-iq4xs-xhigh | 1 | 17/20 | 85% (64%–95%) | 0.88 | 0.97 | 0 | 65 | 24.3 | 1.98 | Submitted 19, LimitsExceeded 1 |
| strata-iq4xs-omp | 1 | 14/20 | 70% (48%–85%) | 0.81 | 0.93 | 0 | 46 | 11.3 | 2.68 | Submitted 19, omp-rc-1 1 |
| strata-iq4xs-omp-xhigh | 1 | 13/20 | 65% (43%–82%) | 0.73 | 0.97 | 0 | 47 | 14.9 | 2.24 | Submitted 20 |
| glm-avar6 | 1 | 13/20 | 65% (43%–82%) | 0.72 | 0.96 | 0 | 38 | 12.6 | 2.51 | Submitted 20 |
| glm-avar6-xhigh | 1 | 13/20 | 65% (43%–82%) | 0.78 | 0.89 | 0 | 79 | 51.1 | 0.83 | Submitted 9, TimeExceeded 7, LimitsExceeded 4 |
| glm-avar6-omp | 1 | 11/20 | 55% (34%–74%) | 0.66 | 0.82 | 0 | 37 | 12.9 | 2.15 | Submitted 20 |
| glm-avar6-omp-xhigh | 1 | 11/20 | 55% (34%–74%) | 0.62 | 0.88 | 0 | 72 | 45.6 | 0.76 | Submitted 16, omp-rc-1 4 |

## Pairwise (same tasks)

| A vs B | Tasks both ran | Only A solved | Only B solved | McNemar p (draw 1) | Mean per-task solve-rate diff A−B |
|---|---|---|---|---|---|
| thinkingcap-dualfast vs thinkingcap-dualfast-xhigh | 20 | 0 | 0 | 1.00 | -0.03 |
| thinkingcap-dualfast vs thinkingcap-dualfast-omp | 20 | 1 | 3 | 0.62 | -0.07 |
| thinkingcap-dualfast vs thinkingcap-dualfast-omp-xhigh | 20 | 2 | 2 | 1.00 | -0.03 |
| thinkingcap-dualfast vs strata-iq4xs | 20 | 0 | 4 | 0.12 | -0.20 |
| thinkingcap-dualfast vs strata-iq4xs-xhigh | 20 | 0 | 5 | 0.06 | -0.28 |
| thinkingcap-dualfast vs strata-iq4xs-omp | 20 | 1 | 3 | 0.62 | -0.12 |
| thinkingcap-dualfast vs strata-iq4xs-omp-xhigh | 20 | 1 | 2 | 1.00 | -0.07 |
| thinkingcap-dualfast vs glm-avar6 | 20 | 1 | 2 | 1.00 | -0.07 |
| thinkingcap-dualfast vs glm-avar6-xhigh | 20 | 3 | 4 | 1.00 | -0.07 |
| thinkingcap-dualfast vs glm-avar6-omp | 20 | 3 | 2 | 1.00 | +0.03 |
| thinkingcap-dualfast vs glm-avar6-omp-xhigh | 20 | 3 | 2 | 1.00 | +0.03 |
| thinkingcap-dualfast-xhigh vs thinkingcap-dualfast-omp | 20 | 1 | 3 | 0.62 | -0.05 |
| thinkingcap-dualfast-xhigh vs thinkingcap-dualfast-omp-xhigh | 20 | 2 | 2 | 1.00 | +0.00 |
| thinkingcap-dualfast-xhigh vs strata-iq4xs | 20 | 0 | 4 | 0.12 | -0.17 |
| thinkingcap-dualfast-xhigh vs strata-iq4xs-xhigh | 20 | 0 | 5 | 0.06 | -0.25 |
| thinkingcap-dualfast-xhigh vs strata-iq4xs-omp | 20 | 1 | 3 | 0.62 | -0.10 |
| thinkingcap-dualfast-xhigh vs strata-iq4xs-omp-xhigh | 20 | 1 | 2 | 1.00 | -0.05 |
| thinkingcap-dualfast-xhigh vs glm-avar6 | 20 | 1 | 2 | 1.00 | -0.05 |
| thinkingcap-dualfast-xhigh vs glm-avar6-xhigh | 20 | 3 | 4 | 1.00 | -0.05 |
| thinkingcap-dualfast-xhigh vs glm-avar6-omp | 20 | 3 | 2 | 1.00 | +0.05 |
| thinkingcap-dualfast-xhigh vs glm-avar6-omp-xhigh | 20 | 3 | 2 | 1.00 | +0.05 |
| thinkingcap-dualfast-omp vs thinkingcap-dualfast-omp-xhigh | 20 | 3 | 1 | 0.62 | +0.05 |
| thinkingcap-dualfast-omp vs strata-iq4xs | 20 | 1 | 3 | 0.62 | -0.12 |
| thinkingcap-dualfast-omp vs strata-iq4xs-xhigh | 20 | 0 | 3 | 0.25 | -0.20 |
| thinkingcap-dualfast-omp vs strata-iq4xs-omp | 20 | 1 | 1 | 1.00 | -0.05 |
| thinkingcap-dualfast-omp vs strata-iq4xs-omp-xhigh | 20 | 2 | 1 | 1.00 | +0.00 |
| thinkingcap-dualfast-omp vs glm-avar6 | 20 | 3 | 2 | 1.00 | +0.00 |
| thinkingcap-dualfast-omp vs glm-avar6-xhigh | 20 | 4 | 3 | 1.00 | +0.00 |
| thinkingcap-dualfast-omp vs glm-avar6-omp | 20 | 3 | 0 | 0.25 | +0.10 |
| thinkingcap-dualfast-omp vs glm-avar6-omp-xhigh | 20 | 4 | 1 | 0.38 | +0.10 |
| thinkingcap-dualfast-omp-xhigh vs strata-iq4xs | 20 | 0 | 4 | 0.12 | -0.17 |
| thinkingcap-dualfast-omp-xhigh vs strata-iq4xs-xhigh | 20 | 0 | 5 | 0.06 | -0.25 |
| thinkingcap-dualfast-omp-xhigh vs strata-iq4xs-omp | 20 | 2 | 4 | 0.69 | -0.10 |
| thinkingcap-dualfast-omp-xhigh vs strata-iq4xs-omp-xhigh | 20 | 2 | 3 | 1.00 | -0.05 |
| thinkingcap-dualfast-omp-xhigh vs glm-avar6 | 20 | 3 | 4 | 1.00 | -0.05 |
| thinkingcap-dualfast-omp-xhigh vs glm-avar6-xhigh | 20 | 3 | 4 | 1.00 | -0.05 |
| thinkingcap-dualfast-omp-xhigh vs glm-avar6-omp | 20 | 3 | 2 | 1.00 | +0.05 |
| thinkingcap-dualfast-omp-xhigh vs glm-avar6-omp-xhigh | 20 | 3 | 2 | 1.00 | +0.05 |
| strata-iq4xs vs strata-iq4xs-xhigh | 20 | 1 | 2 | 1.00 | -0.07 |
| strata-iq4xs vs strata-iq4xs-omp | 20 | 3 | 1 | 0.62 | +0.07 |
| strata-iq4xs vs strata-iq4xs-omp-xhigh | 20 | 4 | 1 | 0.38 | +0.12 |
| strata-iq4xs vs glm-avar6 | 20 | 4 | 1 | 0.38 | +0.12 |
| strata-iq4xs vs glm-avar6-xhigh | 20 | 5 | 2 | 0.45 | +0.12 |
| strata-iq4xs vs glm-avar6-omp | 20 | 6 | 1 | 0.12 | +0.23 |
| strata-iq4xs vs glm-avar6-omp-xhigh | 20 | 7 | 2 | 0.18 | +0.23 |
| strata-iq4xs-xhigh vs strata-iq4xs-omp | 20 | 3 | 0 | 0.25 | +0.15 |
| strata-iq4xs-xhigh vs strata-iq4xs-omp-xhigh | 20 | 4 | 0 | 0.12 | +0.20 |
| strata-iq4xs-xhigh vs glm-avar6 | 20 | 4 | 0 | 0.12 | +0.20 |
| strata-iq4xs-xhigh vs glm-avar6-xhigh | 20 | 4 | 0 | 0.12 | +0.20 |
| strata-iq4xs-xhigh vs glm-avar6-omp | 20 | 6 | 0 | 0.03 | +0.30 |
| strata-iq4xs-xhigh vs glm-avar6-omp-xhigh | 20 | 6 | 0 | 0.03 | +0.30 |
| strata-iq4xs-omp vs strata-iq4xs-omp-xhigh | 20 | 3 | 2 | 1.00 | +0.05 |
| strata-iq4xs-omp vs glm-avar6 | 20 | 2 | 1 | 1.00 | +0.05 |
| strata-iq4xs-omp vs glm-avar6-xhigh | 20 | 3 | 2 | 1.00 | +0.05 |
| strata-iq4xs-omp vs glm-avar6-omp | 20 | 3 | 0 | 0.25 | +0.15 |
| strata-iq4xs-omp vs glm-avar6-omp-xhigh | 20 | 4 | 1 | 0.38 | +0.15 |
| strata-iq4xs-omp-xhigh vs glm-avar6 | 20 | 1 | 1 | 1.00 | +0.00 |
| strata-iq4xs-omp-xhigh vs glm-avar6-xhigh | 20 | 3 | 3 | 1.00 | +0.00 |
| strata-iq4xs-omp-xhigh vs glm-avar6-omp | 20 | 3 | 1 | 0.62 | +0.10 |
| strata-iq4xs-omp-xhigh vs glm-avar6-omp-xhigh | 20 | 4 | 2 | 0.69 | +0.10 |
| glm-avar6 vs glm-avar6-xhigh | 20 | 2 | 2 | 1.00 | +0.00 |
| glm-avar6 vs glm-avar6-omp | 20 | 3 | 1 | 0.62 | +0.10 |
| glm-avar6 vs glm-avar6-omp-xhigh | 20 | 4 | 2 | 0.69 | +0.10 |
| glm-avar6-xhigh vs glm-avar6-omp | 20 | 4 | 2 | 0.69 | +0.10 |
| glm-avar6-xhigh vs glm-avar6-omp-xhigh | 20 | 4 | 2 | 0.69 | +0.10 |
| glm-avar6-omp vs glm-avar6-omp-xhigh | 20 | 2 | 2 | 1.00 | +0.00 |

## Per task (solve rate across draws; partial credit in brackets)

| Task | thinkingcap-dualfast | thinkingcap-dualfast-xhigh | thinkingcap-dualfast-omp | thinkingcap-dualfast-omp-xhigh | strata-iq4xs | strata-iq4xs-xhigh | strata-iq4xs-omp | strata-iq4xs-omp-xhigh | glm-avar6 | glm-avar6-xhigh | glm-avar6-omp | glm-avar6-omp-xhigh |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| #1172 | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] |
| #1174 | 0.0 [0.70] | 0.0 [0.80] | 0.0 [0.70] | 0.0 [0.80] | 0.0 [0.80] | 0.0 [0.60] | 0.0 [0.60] | 0.0 [0.80] | 0.0 [0.60] | 0.0 [0.80] | 0.0 [0.80] | 0.0 [0.60] |
| #1203 | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] |
| #1204 | 0.0 [0.33] | 0.0 [0.33] | 0.5 [0.67] | 0.0 [0.00] | 0.5 [0.67] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] |
| #1209 | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] |
| #1307 | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 0.0 [0.00] | 1.0 [1.00] | 1.0 [1.00] |
| #1464 | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] |
| #1470 | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] |
| #1510 | 0.0 [0.25] | 0.0 [0.50] | 0.0 [0.50] | 0.0 [0.50] | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.50] | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.50] | 0.0 [0.50] | 0.0 [0.00] |
| #1518 | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 0.5 [0.70] | 1.0 [1.00] | 1.0 [1.00] | 0.0 [0.40] | 0.0 [0.40] | 0.0 [0.40] | 0.0 [0.40] | 1.0 [1.00] |
| #1555 | 0.0 [0.50] | 0.0 [0.50] | 0.0 [0.50] | 0.0 [0.50] | 0.5 [0.75] | 1.0 [1.00] | 0.0 [0.50] | 0.0 [0.50] | 0.0 [0.50] | 1.0 [1.00] | 0.0 [0.50] | 1.0 [1.00] |
| #1556 | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.00] | 0.5 [0.50] | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.00] |
| #1564 | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] |
| #1571 | 0.5 [0.75] | 1.0 [1.00] | 0.5 [0.94] | 0.0 [0.62] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 0.0 [0.88] | 1.0 [1.00] | 0.0 [0.88] |
| #1573 | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 0.0 [0.00] | 1.0 [1.00] | 1.0 [1.00] | 0.0 [0.00] | 0.0 [0.00] |
| #1588 | 0.0 [0.00] | 0.0 [0.00] | 1.0 [1.00] | 1.0 [1.00] | 0.5 [0.50] | 1.0 [1.00] | 0.0 [0.50] | 1.0 [1.00] | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.00] | 0.0 [0.00] |
| #1608 | 1.0 [1.00] | 1.0 [1.00] | 0.5 [0.50] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 0.0 [0.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 0.0 [0.00] | 0.0 [0.00] |
| #1610 | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 0.0 [0.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 0.0 [0.00] | 0.0 [0.00] |
| #1612 | 0.0 [0.00] | 0.0 [0.00] | 0.5 [0.50] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 0.0 [0.00] | 0.0 [0.00] | 1.0 [1.00] | 1.0 [1.00] | 0.0 [0.00] |
| #1621 | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] | 1.0 [1.00] |
