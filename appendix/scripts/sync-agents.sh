#!/usr/bin/env bash
# 把 wiki 的 AGENTS.md 同步到各仓库：每个目标开一个同步 PR。
# 用法：bash scripts/sync-agents.sh <关联 issue，如 northpeak/wiki#12>
# wiki 的 AGENTS.md 合并进 main 之后再跑。
set -euo pipefail
ORG=northpeak
REF="${1:?要给关联 issue，如 northpeak/wiki#12}"
TARGETS="numerics-kit:main maxtext:main maxtext:modelx project-management:main project-management-infra:main gke-component-a:master gke-component-b:main gke-component-c:master gke-component-d:master tpu-device-plugin:main"   # 新仓库建好后加进来
DIRECT="project-management project-management-infra"   # 同步 AGENTS.md 算记录类改动，这两个仓库直接推 main（AGENTS.md 第 4 节）

SRC=$(gh api repos/$ORG/wiki/contents/AGENTS.md --jq .content | tr -d '\n')
WIKI_SHA=$(gh api repos/$ORG/wiki/commits/main --jq .sha | cut -c1-7)
BODY=$(mktemp)
for t in $TARGETS; do
  repo=${t%%:*}; base=${t#*:}
  cur=$(gh api "repos/$ORG/$repo/contents/AGENTS.md?ref=$base" --jq .content 2>/dev/null | tr -d '\n' || true)
  if [ "$cur" = "$SRC" ]; then echo "$repo:$base 已一致"; continue; fi
  if [[ " $DIRECT " == *" $repo "* ]]; then
    fsha=$(gh api "repos/$ORG/$repo/contents/AGENTS.md?ref=$base" --jq .sha 2>/dev/null || true)
    gh api -X PUT repos/$ORG/$repo/contents/AGENTS.md -f message="chore: AGENTS.md 同步到 wiki@$WIKI_SHA

Refs $REF" -f content="$SRC" -f branch="$base" ${fsha:+-f sha="$fsha"} >/dev/null
    echo "$repo:$base 已直接推送"; continue
  fi
  br="chore/sync-agents-$WIKI_SHA-$base"
  sha=$(gh api repos/$ORG/$repo/git/ref/heads/$base --jq .object.sha)
  gh api -X POST repos/$ORG/$repo/git/refs -f ref="refs/heads/$br" -f sha="$sha" >/dev/null
  fsha=$(gh api "repos/$ORG/$repo/contents/AGENTS.md?ref=$br" --jq .sha 2>/dev/null || true)
  gh api -X PUT repos/$ORG/$repo/contents/AGENTS.md -f message="chore: AGENTS.md 同步到 wiki@$WIKI_SHA" \
    -f content="$SRC" ${fsha:+-f sha="$fsha"} -f branch="$br" >/dev/null
  cat > "$BODY" <<MD
## 做了什么

\`AGENTS.md\` 同步成 northpeak/wiki@$WIKI_SHA 的版本（由 \`wiki/scripts/sync-agents.sh\` 生成）。

## 关联

Refs $REF

## 怎么验证的

内容与 wiki 的 \`AGENTS.md\` 逐字节相同。

## 和原计划的偏差

无
MD
  url=$(gh api -X POST repos/$ORG/$repo/pulls -f title="chore: AGENTS.md 同步到 wiki@$WIKI_SHA" \
    -f head="$br" -f base="$base" -F body=@"$BODY" --jq .html_url)
  echo "$repo:$base → $url"
done
