#!/usr/bin/env bash
# board.sh —— 把 issue / PR 放进 NorthPeak 看板并设字段。只依赖 gh 和 jq。
#
#   board.sh add    <issue或PR的URL> [S|L]      加进看板（可顺带设大小）
#   board.sh size   <URL> S|L
#   board.sh status <URL> "Design Pending"|"Ready to Develop"|"Blocked"|...
#
# 在任何仓库里不 clone wiki 也能用：
#   gh api repos/northpeak/wiki/contents/scripts/board.sh --jq .content | base64 -d | bash -s -- add <URL> S
set -euo pipefail
PROJECT=PVT_xxxxxxxxxxxxxxxx          # 看板 node id，查法见第 5 章 5.6
F_STATUS=PVTSSF_xxxxxxxxxxxxxxxxxxxxxxxx   # Status 字段 id
F_SIZE=PVTSSF_yyyyyyyyyyyyyyyyyyyyyyyy     # Size 字段 id
declare -A STATUS=([Triage]=aaaaaaaa ["Design Pending"]=bbbbbbbb ["Ready to Develop"]=cccccccc ["In Progress"]=dddddddd [Blocked]=eeeeeeee [Done]=ffffffff)   # 选项 id
declare -A SIZE=([S]=11111111 [L]=22222222)

node_of() {  # URL -> issue / PR 的 node id
  local u=$1 kind; [[ $u == */pull/* ]] && kind=pulls || kind=issues
  local path; path=$(sed -E 's#https://github.com/([^/]+)/([^/]+)/(issues|pull)/([0-9]+).*#repos/\1/\2/'"$kind"'/\4#' <<<"$u")
  gh api "$path" --jq .node_id
}
item_of() {  # URL -> 看板条目 id（不存在就加进去）
  gh api graphql -f query='mutation($p:ID!,$c:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$c}){item{id}}}' \
    -f p="$PROJECT" -f c="$(node_of "$1")" --jq .data.addProjectV2ItemById.item.id
}
set_opt() {  # item field option
  gh api graphql -f query='mutation($p:ID!,$i:ID!,$f:ID!,$o:String!){updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,fieldId:$f,value:{singleSelectOptionId:$o}}){projectV2Item{id}}}' \
    -f p="$PROJECT" -f i="$1" -f f="$2" -f o="$3" >/dev/null
}
cmd=${1:-}; url=${2:-}; val=${3:-}
[[ -n $cmd && -n $url ]] || { sed -n '2,9p' "$0" 2>/dev/null; exit 2; }
case $cmd in
  add)    it=$(item_of "$url"); [[ -n $val ]] && set_opt "$it" "$F_SIZE" "${SIZE[$val]:?大小只能是 S 或 L}"; echo "已加入看板 $it" ;;
  size)   set_opt "$(item_of "$url")" "$F_SIZE" "${SIZE[$val]:?大小只能是 S 或 L}"; echo "Size=$val" ;;
  status) set_opt "$(item_of "$url")" "$F_STATUS" "${STATUS[$val]:?未知状态：$val}"; echo "Status=$val" ;;
  *) echo "未知命令 $cmd" >&2; exit 2 ;;
esac
