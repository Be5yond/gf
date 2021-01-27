# gf
a git-flow branch management

# Installation
```
pip install gitflo
```

# Usage
## 1. Unified standard commit format
## *gf commit*
> Standardize the format of commit.   
> 使用-b/-f 选择是否添加body/footer信息
```
<type>(emoji): <header>
<BLANK LINE> //空行
<body>
<BLANK LINE> //空行
<footer>
```
- type 用于说明 commit 的类别, header 是 commit 目的的简短描述   
- *body 部分是对本次 commit 的详细描述，可以分成多行
- *footer Footer 部分只用于两种情况。BREAKING CHANGE (不兼容的改变) 和 Closes Issue 填写bug编号/或者需求编号

![commit_screenshot](https://github.com/Be5yond/gf/blob/main/doc/commit.png?raw=true)
## 2. branch management
gf feature start &lt;branchname&gt;   
gf feature submit &lt;branchname&gt;   
gf feature finish &lt;branchname&gt;   
gf feature delete &lt;branchname&gt;   
todo：详细说明


# interface 
## *gf switch*
![switch](https://github.com/Be5yond/gf/blob/main/doc/switch.png?raw=true)

## *gf status*
> 合并 git status & git add & git restore部分功能   
> 选择文件 然后执行命令添加或者移除暂存区
![status](https://github.com/Be5yond/gf/blob/main/doc/status.png?raw=true)

## *gf tag*
> create a tag in 'v{major}.{minor}.{patch}_{date}' format   
> Use -p/-m/-M to increase patch/minor/major version number

<img src="https://github.com/Be5yond/gf/blob/main/doc/tag.png?raw=true" width="200px" />

## *gf undo*
> 撤销last commit提交, == *git reset "HEAD^"*

## *gf log*
> todo