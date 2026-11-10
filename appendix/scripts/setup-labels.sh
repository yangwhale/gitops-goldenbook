#!/usr/bin/env bash
# setup-labels.sh —— 给一个仓库建好标签：先删 GitHub 默认标签，再按角色建。
#   setup-labels.sh <org>/<repo> training|infra|wiki
# 幂等：已有的标签会被更新颜色和描述（--force）；表外的标签会被删除，已在用的仓库慎用。
set -euo pipefail
REPO=${1:?用法：setup-labels.sh <org>/<repo> training|infra|wiki}
ROLE=${2:?第二个参数：training | infra | wiki}

KEEP=()
mk() { gh label create "$1" -R "$REPO" --color "$2" --description "$3" --force >/dev/null; KEEP+=("$1"); echo "  $1"; }

common_type() {
  mk type/bug      d93025 "缺陷"
  mk type/feat     1a73e8 "新功能"
  mk type/docs     5f6368 "文档"
  mk type/chore    9aa0a6 "杂务"
  mk size/S        1e8e3e "小任务，不需要 RFC"
  mk size/L        9334e6 "大任务，先写 RFC"
  mk P0            b60205 "阻塞"
  mk tracker       f9ab00 "总表：同一问题的不同方面，或大任务拆给不同的人"
}
issue_repo() {
  mk type/design   bfdadc "设计、调研、RFC"
  mk type/question cfd3d7 "问询：怎么用、是否符合预期"
  mk P1            d93f0b "优先级：本阶段必须解决，影响上线主路径"
  mk P2            fbca04 "优先级：重要但不阻塞主路径"
  mk area/other    d4c5f9 "领域：以上都不是"
}

echo "$REPO（$ROLE）："
common_type
case $ROLE in
  wiki)
    mk access 80868b "权限变更" ;;
  training)
    issue_repo
    mk type/accuracy  e99695 "精度、数值和参考对不上（loss、梯度、输出）"
    mk type/perf      f9d0c4 "性能不达预期（吞吐、步时、MFU、显存）"
    mk area/maxtext   1d76db "领域：MaxText 代码与配置"
    mk area/jax-xla   5319e7 "领域：JAX、XLA 编译器、libtpu"
    mk area/kernel    b60205 "领域：kernel（Pallas、Tokamax 等）"
    mk area/inference 0e8a16 "领域：TPU 推理"
    mk area/torch-tpu fbca04 "领域：PyTorch on TPU"
    mk area/env       c5def5 "领域：环境、版本、镜像、依赖" ;;
  infra)
    issue_repo
    mk type/perf      f9d0c4 "性能不达预期（调度与节点启动时延、网络带宽 / 时延、存储吞吐）"
    mk area/gke       326ce5 "领域：GKE on TPU（切片、device plugin、Kueue / JobSet、节点池、维修与健康、存储挂载）"
    mk area/network   006b75 "领域：网络（ICI / DCN / OCS、VPC、NAT、DNS、多网卡）"
    mk area/env       c5def5 "领域：配额与容量" ;;
  *) echo "未知角色 $ROLE" >&2; exit 2 ;;
esac

# 删掉表外的标签（GitHub 新仓库自带的 bug、enhancement、accessibility 等）。
# 默认标签在建仓库后异步生成，所以放在最后、按实际列表删，而不是开头按固定名单删。
gh label list -R "$REPO" -L 200 --json name --jq '.[].name' | while IFS= read -r l; do
  [[ " ${KEEP[*]} " == *" $l "* ]] && continue
  gh label delete "$l" -R "$REPO" --yes >/dev/null && echo "  删除 $l"
done
