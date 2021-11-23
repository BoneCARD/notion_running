#!/bin/sh

if [ ! $1 ];then
  echo "需要传入一个变量来设置监控git的哪个分支，example：git_auto_run.sh master"
  exit 1
else
  BRANCH=$1
  echo "监控git分支：$1"
fi

# 新建分支，并与远端的BRANCH关联
git checkout $BRANCH
git branch --set-upstream-to=origin/$BRANCH $BRANCH

LOCAL=$(git log $BRANCH -n 1 --pretty=format:"%H")
REMOTE=$(git log remotes/origin/$BRANCH -n 1 --pretty=format:"%H")

nohup python3 server.py >/dev/null 2>&1 &

while true
do
  changed=0
  git remote update && git status -uno | grep -q 'Your branch is behind' && changed=1
  if [ $changed = 0 ]; then
    # echo "wait for git branch $BRANCH to update"
    echo -ne "\r $(date "+bas-%Y-%m-%d %H:%M:%S") wait for git branch $BRANCH to update"
    sleep 1m
  else
    echo "update git branch of $BRANCH"
    # 拉取最新的git数据
    git pull
    nohup python3 server.py >/dev/null 2>&1 &
    sleep 1m
  fi
done
