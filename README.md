# Programming Historian Issue Analyzer README

This repository holds code and data for analyzing the entirety of issues from Programming Historian's Jekyll repository.

We may expand to also analyze the ph-submissions repository, though that repository has had fewer consistent processes so the data might be all over the place.

The repository includes:

scripts
- generate dataset

Issue Data 
https://docs.github.com/en/rest/reference/issues#list-repository-issues

| Name | Type | In  | Description |
|-------------|-------------|-----|--------------------------|
| milestone	| string | query | If an integer is passed, it should refer to a milestone by its number field. If the string * is passed, issues with any milestone are accepted. If the string none is passed, issues without milestones are returned. |
| state	| string | query | Indicates the state of the issues to return. Can be either open, closed, or all. |
| assignee	| string | query | Can be the name of a user. Pass in none for issues with no assigned user, and * for issues assigned to any user.|
| creator | string | query | The user that created the issue.|
|mentioned | string | query | A user that's mentioned in the issue.|
| labels | string | query | A list of comma separated label names. Example: bug,ui,@high |


Comments Data


datasets
- github datasets

issues
comments
reactions

notebooks
- explore datasets