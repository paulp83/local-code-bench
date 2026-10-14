# Fill in the application form

`/workspace/cv.md` is a CV and `/workspace/schema.json` is the JSON Schema of an application form. Write `/workspace/application.json` that validates against the schema and answers truthfully from the CV.

Notes: `country` uses the schema's enum codes; `years_experience` counts whole years of work from the earliest start year to 2026 (the CV's last job runs to 2026);
`skills` lists the CV's skills in order; `available` is `true`.
