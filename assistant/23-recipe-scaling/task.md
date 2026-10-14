# Scale a recipe from 4 to 10 servings, in metric

Write `/workspace/recipe-10.md` from `/workspace/recipe.md`: scale every amount by 10/4, then convert units: 1 cup = 240 ml, 1 tbsp = 15 ml, 1 tsp = 5 ml, 1 oz = 28 g.
Counts (eggs) are rounded to the nearest whole number (halves up); `pinch` amounts stay `1 pinch` (a pinch does not scale). Do not round the metric values.
Keep the format: first line `# Oat pancakes (serves 10)`, the same two-column table, amounts written `<number> <unit>` (counts as a bare number, no trailing `.0`), same ingredient order.
