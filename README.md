# Electrical Learning Assistant — Community Edition

A Codex-first Agent Skill for studying electrical engineering with a local, source-linked learning workspace. It guides the AI through study, problem solving, durable knowledge review, and workspace validation.

> 中文简介：这是一套面向电气工程学习的 AI Skill，帮助 AI 按照本地学习工作区中的课程资料和已审核知识，继续学习、制作关联原文的笔记、解题、复盘和整理知识。

**This is an instructions package, not a hosted tutor or a course-material archive.** Full workflows require a compatible local Electrical Engineering Learning System workspace and an AI environment that can read and work with that folder.

## Get the Skill

- **Repository:** <https://github.com/hanzhichengnb-cpu/electrical-learning-assistant-community>
- **Main instructions:** <https://raw.githubusercontent.com/hanzhichengnb-cpu/electrical-learning-assistant-community/main/SKILL.md>

The repository link is the best link to give an AI: it can read `SKILL.md` and follow its links to the relevant workflows, references, scripts, and assets. The raw `SKILL.md` link is useful for a quick inspection, but does not contain the complete bundle by itself.

## What it can do

| Learning task | What the Skill guides the AI to do |
|---|---|
| Resume a study session | Read the workspace's saved source, page, review status, and next action before continuing. |
| Study course materials | Work from source pages, explain concepts and prerequisites, and prepare source-linked reading notes using the workspace's supported format. |
| Solve problems | Identify the problem structure, retrieve relevant approved knowledge and course-page references, verify decisive source details, and explain the reasoning. |
| Reflect and retain knowledge | Keep normal solving conversational; prepare a review item only after the learner chooses to save it. |
| Review and publish knowledge | Present the exact version for the learner to approve before adding or materially revising durable knowledge. |
| Validate and move a workspace | Check saved state and references, diagnose integrity issues, and rebind a moved source only when its file hash matches. |

The workflow keeps course sources, reading notes, and approved long-term knowledge distinct. It also teaches source-grounded technical English as part of the engineering explanation.

## Give the link to an AI

For an AI that can access public GitHub repositories, share the repository link above with a request like this:

```text
Please use the Electrical Learning Assistant Community Edition from
https://github.com/hanzhichengnb-cpu/electrical-learning-assistant-community.
Read SKILL.md and the supporting files relevant to my request. First check
whether I have provided a compatible local electrical-engineering learning
workspace. If I have, use that workspace and follow its saved state and review
rules. If I have not, explain what is missing; do not imply that you can see my
course files or saved learning history.
```

The AI needs its own GitHub or web access to fetch the link. A link does not install the Skill into an AI account, grant access to your computer, or provide your personal learning workspace.

## Install in Codex

Clone this repository into Codex's skills directory, then start a new conversation or reload Skills:

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/hanzhichengnb-cpu/electrical-learning-assistant-community.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/electrical-learning-assistant-community"
```

Then invoke it explicitly:

```text
Use $electrical-learning-assistant-community to continue my electrical engineering study.
```

If your Codex installation uses a custom `CODEX_HOME`, the clone command follows that location.

## Workspace requirements

The Skill operates a workspace; it does not create the full learning system by itself. Full use requires a local workspace that follows the [workspace contract](references/workspace-contract.md), including:

- a workspace `AGENTS.md` and `VERSION`;
- `objects/`, `sources/`, `staging/`, and the workspace's own `tools/`;
- `00_System/runtime/CURRENT_STATE.yaml`;
- the local specifications and commands required by the requested workflow.

Course PDFs, personal annotations, study progress, knowledge objects, and the local search index belong in the learner's workspace. They are not included in this repository. If a workspace capability is missing, the Skill's instructions require the AI to detect that and use a supported fallback or explain the limitation rather than inventing commands.

## Compatibility

- **Designed for:** Codex with local filesystem access to a compatible electrical-engineering learning workspace.
- **Can be read by:** Other AI assistants with public GitHub or web access and the ability to follow Markdown links.
- **Needs adaptation outside Codex:** Workspace commands, local file access, and any environment-specific rendering or browser workflow must be supported by that AI environment. Reading the instructions alone does not supply those tools.
- **Workspace line:** Prepared as a separate public iteration based on the Electrical Engineering Learning System V1.3 line. Workspace release numbers and Skill revisions are tracked independently.

## Repository contents

This repository contains only the reusable Skill package:

- `SKILL.md` — activation metadata and top-level workflow routing;
- `workflows/` — study, solve, reflect, review, resume, validation, and publication procedures;
- `references/` — workspace, teaching, portability, source-language, and delivery guidance;
- `scripts/` — small helpers for state checkpoints and source rebinding;
- `assets/` — reusable reading-delivery layout files.

The community edition has its own Skill name and can be installed alongside another `electrical-learning-assistant` Skill.

## Privacy and review boundaries

No course materials, personal notes, saved state, knowledge-base objects, or source PDFs are included here. When you use the Skill, the AI works with files available in your own environment; privacy and data handling also depend on that AI product and its settings.

The workflows preserve learner approval before publishing durable knowledge. Review the Skill and any scripts before installing them, and give the AI access only to the workspace it needs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CHANGELOG.md](CHANGELOG.md). Please do not submit personal course files, private notes, runtime state, source PDFs, or copies of a learner's workspace.

## License

No license has been selected for this public edition yet. Public visibility permits people to read the repository; it does not by itself grant permission to redistribute or modify the contents.

---

## 中文使用说明

### 适用范围

这份 Skill 适合已经有本地电气工程学习工作区，并且能让 AI 读取该工作区的用户。它可以指导 AI 按保存状态继续学习、阅读课程 PDF、制作关联原文的学习笔记、结合已审核知识解题、复盘、审阅待保存内容，以及检查工作区完整性。

### 把链接发给 AI

把上面的 GitHub 仓库链接和一句说明一起发给支持读取 GitHub 的 AI，并要求它先读取 `SKILL.md`，再按任务读取相关工作流和参考文件。AI 还需要有权限访问你自己的本地学习工作区。公开仓库不会包含你的课件、知识库或学习进度；链接本身也不会替 AI 安装 Skill 或授予它本机文件权限。

### 当前边界

公开版以 Codex 和 V1.3 学习工作区为主要适配对象。其他 AI 可以读取这些 Markdown 指令，但需要具备相应的本地文件和命令执行能力；不同平台可能需要额外适配。没有兼容工作区时，它仍可以阅读说明，但不能声称能访问个人学习记录或执行保存、续学等工作区操作。
