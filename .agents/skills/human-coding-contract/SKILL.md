---
name: human-coding-contract
description: Use plain syntax and layered architecture for coding tasks with commit-based progress reports; new features require investigating existing code, a confirmed short spec, a dedicated branch, and a pull request merge after acceptance; 中文触发词包括人话编码契约、土法编码和分层交付；仅在用户明确启用本 skill 时使用。
---

# Human Coding Contract

This is an opt-in, project-specific coding workflow. Apply it only when the user explicitly invokes `$human-coding-contract` or asks for 人话编码契约、土法编码、分层交付, or the plain coding contract. Do not apply it as a global rule.

Communicate with the user in Chinese unless the user asks for another language. Keep the commit handoff in Chinese.

## Missing background

This is a hard stop. Do not start coding, invent sample data, or assume a "typical" structure when required background is missing.

If the task depends on inputs the user has not provided — such as HTML/XML to parse, API payloads, file formats, screenshots, table schemas, or business rules — explicitly ask the user for that material and wait. Do not guess and begin development.

Forbidden: the user asks to parse academic-affairs training-plan HTML, but no HTML was given. Inventing a plausible HTML, writing a parser against that guess, and "filling in later" is strictly not allowed.

Ask in Chinese. Name what is missing and why it is needed. Do not list implementation files or write code until the missing background is in hand.

A requirements sentence such as “read the third column” is not an HTML sample. Do not invent `<table>` / `<tr>` / `<td>` markup, HAR-shaped pages, or “typical vendor HTML” to write a parser. Ask for a real page dump or HAR excerpt and wait.

Parser and importer work has the same hard stop. A fixture must already be in the repo, or it must be a redacted excerpt the user provided. Do not invent input that "looks like" the real HTML, payload, or table so the parser can be finished. Do not set the expected value from the new parser's current output. If the real input is missing, ask and wait.

## File edits

This is a hard rule, not a preference.

Change source files, tests, and docs only with the dedicated editor tools provided to the agent: `Edit`, `Write`, or `apply_patch`.

Forbidden ways to change those files:

- `python` / `perl` / `ruby` scripts or one-liners that rewrite files
- `sed` / `awk` / `ed` in-place patches
- shell heredoc or `printf` redirected onto a source path
- editing a copy under `/tmp` and overwriting the project file

Shell is for running tests, git, formatters, and compilers — not for patching code.

If `Edit` cannot find `old_string`:

1. Read the file again and retry `Edit` with a smaller unique snippet.
2. If it still fails, `Write` the full corrected file content.
3. Do not “give up and use Python”.

Running `gofmt` / `eslint --fix` from the shell after an editor change is allowed. Using the shell as a substitute for the editor is not.

## New feature gate

Apply this only to a new feature, or to a behavior change whose "done" cannot be judged from the chat alone. Do not apply it to a bugfix, a one-line or single-function change, a question, a review, or when the user explicitly says to stay on the current branch or skip the pull request.

Do not edit code and do not create the branch until the spec is confirmed.

1. Investigate the existing code first. Read the neighboring feature in role order: entity → data → business → entry. Record the real types, errors, routes, tests, and style already in the repo. Use the directory and type names that neighbor already uses. Do not create `entity/`, `data/`, `business/`, or `entry/` to fill four roles, and do not invent a parallel stack, sample payload, or "typical" API.

2. Write a short spec in the conversation. Do not add a spec file unless the user asks, or the repo already keeps specs. Small tasks may merge sections. Never drop these four: 目标, 非目标, 验收标准, 失败与回滚. 非目标 must name what this change will not do, including layers or files that stay untouched. Do not implement a named 非目标 to finish the feature or to fill a missing role. Add 接口/数据, 依赖与影响, and 测试 only when the investigation shows they matter. Do not paste a long template. Put every undecided choice in 开放问题; do not hide it in the plan.

   ```
   【Spec，等确认】

   标题：[模块] 动作/结果
   基线分支：[main / master / 当前默认分支]

   现状：
   - [读过的现有路径]：[已经怎么做，准备复用什么]

   背景：
   - [为什么做；不做会怎样]

   目标：
   - [可判定的结果]

   非目标：
   - [这次明确不做的事]

   验收：
   - [Given / When / Then，或可执行清单]

   失败与回滚：
   - [失败时怎么停、怎么撤；无数据变更就写明无需回滚]

   开放问题：
   - [没有就写“无”]
   ```

3. Stop and wait. `继续`, `1`, or an explicit approval confirms this spec. A requirements sentence is not confirmation. If an open question blocks the acceptance criteria, ask and wait.

4. After confirmation, create one branch from the named base branch before the first edit. Name it `feat/<short-slug>` unless the user names another branch. Do not develop the feature on the default branch, and do not pile it onto an unrelated dirty branch. If this is not a git repository, or the base branch cannot be determined, stop and say so. Do not pretend a branch or pull request exists.

5. Implement only on that branch. The collaboration cadence still applies: one logical commit at a time, stop for review, and commit only after `继续` or `1`. Do not push those commits early. The last `继续` approves that commit only. It is not acceptance of the whole feature and it is not permission to merge.

6. When every agreed logical goal is committed, stop for acceptance. Do not push or open a pull request yet. After the user explicitly accepts — `验收通过` or `合并` — push the feature branch, open a pull request into the base branch, and merge it. The pull request body is the confirmed spec plus the check results, not a new design. If checks fail, the remote is missing, or the pull request cannot merge, stop and report the blocker. Do not merge into the default branch with a local merge that skips the pull request.

If the user explicitly opts out of the branch or the pull request, say that exception once and follow the rest of this contract on the branch they named.

## Collaboration cadence

1. If required background is missing, ask for it and wait; do not guess. A new feature must pass the New feature gate first. After that spec is confirmed and the feature branch exists, list the files, each responsibility, and the planned commit scope for visibility, then implement the agreed goal without waiting for a second confirmation of that inventory. Do not repeat the same inventory for later commits in that goal. Bugfixes and changes the user explicitly kept off the gate still list the files and then implement without a spec confirmation.
2. Design in role order: entity → data → business → entry. See Layer roles. One logical goal may edit the related roles in one continuous segment, then stop once. Do not stop after each full layer. Each proposed commit must represent one clear logical goal and must not bundle many independent features.
3. Complete the code for the current logical goal and run the required checks, but do not commit or push. Pause once. In that same stop, show the review path and the progress report. Do not paste the full git diff into the conversation. Do not wait for review and then wait again after the commit. The exact 【停，等指令】 block below is mandatory; a casual prose summary does not count. Do not skip the template because the change looks small.

   The review path is required every time the user is asked to review. Follow the role order entity → data → business → entry; skip roles that did not change, and do not invent them. A change that touches one role lists only that role. Granularity must be the concrete function (or type/struct when there is no function). Do not stop at file level. List only changed functions, in that reading order, one short line each, saying what to look at. This is a route for sequential review, not a changelog.

   Use this exact structure. Use a short bullet list: more than one sentence, not a changelog.

   ```
   【停，等指令】

   拟议提交：[commit 信息]（共 X 个文件）

   审阅路径：
   1. [层] [文件] [函数]：[先看什么]
   2. [层] [文件] [函数]：[接着看什么]

   本次完成：
   - [文件或模块]：[改了什么、解决了什么]
   - [文件或模块]：[改了什么、解决了什么]

   检查：
   - [检查项]：[通过 / 失败及必要说明]

   全部进度：
   - [逻辑目标]：已完成
   - [逻辑目标]：已完成（本轮）
   - [逻辑目标]：当前下一步，尚未开始编码
   - [逻辑目标]：未开始

   当前下一步：
   - [下一个逻辑目标]：[现在到哪一步 / 待确认事项]（尚未开始编码）

   请确认审阅路径与进度，无误后回复“继续”或“1”。
   ```

   “本次完成” must list the changed files or modules, one short line each, covering what changed and why. Do not collapse the work into a single sentence. Do not write a long change document. “检查” must name the commands or quality gates and whether they passed. “全部进度” is required: list every logical goal in the agreed overall scope, each with status (已完成 / 本轮完成 / 当前下一步 / 未开始). Do not omit earlier completed goals. “当前下一步” is required and must name the single next logical goal and how far it is (for example 尚未开始编码, or 待确认某项). If the overall goal is done, say so in “全部进度”, set “当前下一步” to remaining confirmation or wrap-up items, and do not invent extra work.

4. A user reply of `1` is equivalent to `继续`. Either means the changes are approved. Only then create the commit containing exactly the reviewed changes. Do not pause again after that commit. If the user requests revisions, update the code, rerun checks, and show the same combined stop (updated review path, updated progress) without committing. Do not paste the full git diff.

5. Do not implement the next independent feature while waiting. The next scope belongs only in “当前下一步”; do not write its code early. After `继续` or `1` and the commit, start that next goal unless the overall work is done.

## Readability over sophistication

Plain, even unsophisticated syntax is allowed. Do not require heavy engineering: no extra architecture, abstraction layers, pattern stacks, DI, plugin systems, or package splits unless the existing project already uses them.

The code must be human-readable at a glance. Opening a file should show what this layer does, where data comes from and goes, and what each branch decides. Prefer obvious repetition over cleverness that has to be guessed.

A reader should be able to:

- understand names without decoding them through comments
- follow control flow top to bottom, with conditions stating business judgments
- read the main path without first learning framework magic, metaprogramming, or type gymnastics
- point to where data is queried and where rules are written

## Style consistency

Style must stay consistent across modules and later work. New files follow the same naming, error handling, directory layout, comments, and import habits as existing code in the same layer. Reuse existing shared types, errors, logging, and validation; do not invent a parallel set per module.

Formatting, lint, and typecheck follow the repository's existing config. Do not add a second style for this feature, do not disable or bypass existing checks, and do not introduce naming or layout that conflicts with neighboring modules.

## Layer roles

`entity`, `data`, `business`, and `entry` are reading and calling roles, not directories to create.

- `entity`: the business nouns and their fields. It does not query storage, apply rules, or handle a request.
- `data`: how those nouns are stored and loaded. It does not decide whether the action is allowed.
- `business`: the rules, the allowed state changes, and the computed result. It does not parse HTTP or shape the response.
- `entry`: the door. It accepts input, calls business, and hands the result back. It does not contain the rules or the queries.

Calls stay one-way: entry → business → data. Review in the opposite order: entity → data → business → entry. Skip a role that this change did not touch. A small change that touches one role is reviewed only at that role; do not add the other three so the path looks complete.

Use the names the repo already uses, such as `handler` / `service` / `repo`, or whatever the neighboring feature uses. Do not create `entity/`, `data/`, `business/`, or `entry/` just to fill four layers.

One logical goal may edit the related roles in one continuous segment, then stop once for review. Do not stop after each full layer. The older prompt rule 「每完成一整层再停」 in `prompt/simple-syntax-architecture.md` is retired; do not follow it.

A script, plugin, or other single-file tool may keep these roles in one file. The functions must still be identifiable: which function is the door, which function is the rule, and which function touches storage.

## Coding principles

- Prefer ordinary classes, explicit branches, direct dependencies, and traceable control flow.
- Do not use decorator factories, reflection, metaclasses, dynamic code generation, pattern matching, nested comprehensions, the walrus operator, or type gymnastics.
- Classic patterns are allowed when implemented with ordinary classes, interfaces, or map/dictionary dispatch. Do not use dynamic proxies or auto-discovery.
- Keep dependencies one-way: entry → business → data. Do not cross layers or create circular dependencies. These are roles, not directories to create; see Layer roles.
- Inject dependencies through constructor arguments or direct imports. Do not use DI containers, service auto-discovery, or annotation wiring.
- Keep each function at or below 50 lines, excluding blank lines and comments. Split longer functions.
- Do not hide business logic in vague `utils`, `common`, or `base` packages.

## Comments and generics

Comments are for the human reviewer. Every file, every function, every declaration (`struct` / `class` / `type` / `interface` / `enum`), every field inside such a declaration, every constant, and every `if` / `elif` / `else` / `switch` / `case` must have a short comment. One or two lines is enough; do not write a changelog in comments.

- File: put a header comment at the top stating what this file is responsible for and which role it belongs to. If a script, plugin, or other single-file tool keeps several roles in one file, name which function is the door, which is the rule, and which touches storage, instead of assigning the whole file to one directory layer.
- Function: state what it does, and when needed the parameters, return value, exceptions, or side effects. Do not skip a function because it looks trivial.
- Declaration (`struct` / `class` / `type` / `interface` / `enum`): state what it represents in the business, which layer owns it, and where it is produced and consumed.
- Field of a declaration: comment every field, stating what it means. Add the unit, range, source, or why it exists when that is not obvious from the name. Do not rely on the field name alone, even when the name looks clear.
- Constant: comment every constant, stating what the value means, where it comes from, and why this value. For units, ranges, or enum-like values, list the allowed values and their meaning. Do not leave a bare number or magic string without naming it as a constant and explaining it.
- Condition: comment what the judgment is for — the business purpose — not a restatement of the expression. Write the reason and the consequence. Forbidden: `// if user is null`. Required: `// 没有登录用户则无法查培养方案，直接返回`.
- Explain complex decisions, security boundaries, and important side effects in plain language. Do not narrate obvious non-branching code such as increments or simple assignments.
- Only basic generics are allowed, such as `List[T]`, `Ref[T]`, or `[T any]`. Before writing a generic function, ask the user:

  `这处泛型是为了复用 [逻辑]，写法是 [片段]，你能看懂吗？`

  If the user does not understand it, immediately use a concrete non-generic function.

  Do not use generics, type gymnastics, or "advanced" syntax in a way that splits style across modules.

## Quality gates

Static checks are required. Before asking for review or committing, the change must pass this repository's existing static checks and typechecks. If the project has no command yet, say so and stop; do not skip, and do not "fix lint later". If docs, a Taskfile, or a script claim a static-check config exists but the file is absent — for example `.golangci.yml` — stop and say that. Do not report the check as passed, and do not treat style as already enforced by the missing config. Treat every lint error as a bug and fix it before committing.

- Go: run `golangci-lint run` and handle `if err != nil` explicitly.
- Python: run `ruff check .`, never use a bare `except: pass`, and split long functions.
- Vue/TypeScript: run `eslint` and `tsc --noEmit`; do not use `any` and keep types explicit.
- Other languages: run the repo's existing static check and typecheck commands.

## Pre-commit checklist

1. The business logic still works when generics are replaced with concrete types.
2. A junior developer can find where data is queried and where rules are written.
3. Project-root quality checks are green before asking for review. Existing format/lint config is not bypassed. If a claimed config file is missing, the stop says so; the check is not reported as passed.
4. Every file, function, declaration, field inside a declaration, constant, and condition has a short comment: file purpose, function purpose, what the declaration and each field mean, what each constant is for, and what each judgment is for.
5. The proposed commit contains only the previously reported files and logical goal.
6. Secrets, tokens, and passwords do not appear in code, comments, logs, diff output, or commit messages.
7. No commit or push occurs before explicit approval. Do not paste the full git diff into the conversation.
8. A role-ordered review path has been given at function granularity so the user can read entity → data → business → entry, function by function. Unchanged roles are skipped and not invented. A one-role change lists only that role.
9. The code is based on user-provided inputs and observed structures, not invented samples or guessed formats. Parser and importer fixtures come from a repo sample or a user-provided excerpt, and expected values are not taken from the new code's own output.
10. New code matches the style of existing modules in the same layer; no second style was introduced for this feature.
11. The main path is readable at a glance and does not depend on advanced syntax or extra engineering to make sense.
12. Source, tests, and docs were changed only with Edit / Write / apply_patch; no shell or Python rewriting.
13. A new feature was investigated and its spec was confirmed before the first edit.
14. New-feature commits are on the dedicated branch, not the default branch. The pull request is opened and merged only after explicit acceptance of the whole feature, not after `继续`.
15. Every `struct` / `class` / `type` / `interface` / `enum` and each of its fields has a comment saying what it represents; no field is left to the name alone.
16. Every constant has a comment naming its meaning, source, and, where relevant, its unit or allowed values; no unexplained magic value was introduced.
17. 非目标 was written, including work and layers left untouched, and that work was not implemented.
