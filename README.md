# 尺素 · Chisu

> 客从远方来，遗我双鲤鱼。呼儿烹鲤鱼，中有尺素书。

古人把信写在一尺长的白绢上，所以信也叫「尺素」。

这是一个让 AI 用自己的字写信的 skill。

它不套现成的字体。写信的 AI 先决定自己的字长什么样：横往哪边扬，撇写多长，字是宽是窄。然后把这封信要用的字一笔一笔画出来，排成一封信。字帖会存下来，下一封接着用；你说「这个钩我喜欢」，它就把这个钩留到下一封。

所以它写出来的第一封信，大概会很笨、很工整，像刚学写字的小学生。这是对的，它就是刚学写字。

## 怎么用

从 GitHub 点 **Code → Download ZIP**，下载后解压。把整个文件夹交给一个能读写文件、能运行 Python 的 AI；如果你的客户端支持 skills，就把文件夹改名为 `chisu` 放进 skills 目录。入口是 [SKILL.md](SKILL.md)。

第一次可以只说：

> 请读 SKILL.md，用你自己设计的字给我写一张便笺。写什么、怎么落款，你自己定。写好给我看，也把你的字帖存起来，下次接着用。

收到信以后，可以指着某一笔说：

> 我喜欢这个折角。「外」写松一点，同一句写两遍给我挑。

> 这个字写错了。

后一句很常见。凭记忆画字，多一横少一点是常事。

## 里面有什么

| 文件 | 是什么 |
| --- | --- |
| [SKILL.md](SKILL.md) | 给 AI 看的说明：怎么写第一封、怎么接着写、常踩的坑 |
| `scripts/write_letter.py` | 把字帖和正文排成一封信（SVG） |
| `scripts/check_glyphs.py` | 对着笔顺骨架查字：笔画数对不对、每笔起止偏没偏 |
| [references/format.md](references/format.md) | 字帖文件的格式 |
| [references/notebook.md](references/notebook.md) | 练字手记 |
| `assets/example.json` | 一个最小的字帖，只有三个字，用来确认程序能跑 |

## 在自己电脑上跑一下

需要 Python 3.9 或更高版本，不用装别的东西。在解压后的文件夹里运行：

```sh
python scripts/write_letter.py assets/example.json assets/example.txt sample.svg
```

用浏览器打开 `sample.svg`。Windows 上可以把开头换成 `py -3`，macOS 和 Linux 上可以用 `python3`。

写新信时依次给三样东西：**字帖（JSON）、信的正文（TXT）、输出的图（SVG）**。字帖不用一开始写满，用到哪个字补哪个；缺字时程序会把缺的字列出来。

## 公开分享之前

你自己的字帖、真名落款、信的原文和成品图，放进 `private/` 文件夹，它已经被 Git 忽略，不会被上传。

生成的 SVG 里会带着信的全文。要公开的话，换一句可以公开的话重新生成。

## 许可

说明、代码和示例采用 **CC BY 4.0（知识共享署名 4.0 国际）**。转载或改编时请署名「尺素 / Chisu contributors」，附上许可链接，并注明改了什么。详见 [LICENSE](LICENSE)。

笔顺骨架数据（比如 Make Me a Hanzi）不包含在本仓库里。单独下载时，请遵守它们各自的许可。
