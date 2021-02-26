# gf
a git-flow branch management

# Installation
```
pip install gitflo
```

# Usage
## 1. branch management
### 三个长期分支Dev/Test/Release，features分支为短期分支，分支之间只能feature>dev>test>release单项合并    
1. feature分支：例如："f-cash", 从develop分支创建，开发完成后，merge到develop分支，上线后feature分支删除
2. develop分支：开发人员日常工作分支，对应开发环境，进行联调和自测，自测通过后merge到test分支
3. test分支：测试人员日常工作分支，对应测试环境，测试通过后merge到Release分支
4. release分支：可对应git的Master(Main)分支，发布线上的版本，pre(预发布)环境验收通过后部署prod(生产)环境上线

### 各分支与环境关系

| 分支      | 生命周期     | 环境     |  部署  |   是否需审核 |
| ---------- | :-----------:  | :-----------: | :-----------: | :-----------: |
| Release     | 长期     | Prod     | 手动  |  是
| Release     | 长期     | Pre     |  手动  |  否
| Test     | 长期     | test     | 自动(代码提交时) | 否
| Develop     | 长期     | Dev     | 自动(代码提交时) | 否
| Feature     | 短期     | Local     |  手动 | 否
### 分支流传流程
![commit_screenshot](https://github.com/Be5yond/gf/blob/main/doc/flow.png?raw=true)

### gf 分支管理
1. gf feature start &lt;branchname&gt; 创建分支   对应上图中 1
2. gf feature submit &lt;branchname&gt; 分支合并到develop分支   对应上图中 2
3. gf feature delete &lt;branchname&gt; 删除分支  对应上图中 3
4. gf test 将当前Develop分支合并到Test分支，提交测试   对应上图中 4
5. gf release  将当前Dest分支合并到Release分支, 准备发布

 - - - 
## 2. Unified standard commit format
### *gf commit*
> 标准的commit msaage格式    
> 使用-b/-f 选择是否添加body/footer信息flow
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
- - -
## 3.Other Interface
### *gf branch*
更简单的branch切换，展示与remote的同步进度   
![switch](https://github.com/Be5yond/gf/blob/main/doc/branch.png?raw=true)

 - - - 
### *gf status*
> 合并 git status & git add & git restore部分功能   
> 选择文件 然后执行命令添加或者移除暂存区
![status](https://github.com/Be5yond/gf/blob/main/doc/status.png?raw=true)

- - -
### *gf tag*
> create a tag in 'v{major}.{minor}.{patch}_{date}' format   
> Use -p/-m/-M to increase patch/minor/major version number

<img src="https://github.com/Be5yond/gf/blob/main/doc/tag.png?raw=true" width="200px" />

### *gf undo*
> 撤销last commit提交, == *git reset "HEAD^"*

### *gf log*
更美观的log信息
![status](https://github.com/Be5yond/gf/blob/main/doc/log.png?raw=true)


### *gf inspect*
项目trending
![status](https://github.com/Be5yond/gf/blob/main/doc/inspect.png?raw=true)