# 自己的笔迹 · Write in Your Own Hand

「用你自己的字，给我写一封信。」

写信的 AI 先决定自己怎么落笔，再一笔一笔画出这封信用到的字。它可以有几个总爱写长的横，一种顺手的连法，也可以因为读信的人一句「这个钩我喜欢」把它留到下一封。这个仓库提供练字的方法、一支可以调压力的笔，以及把笔迹排成信的程序。

## 同一句，两种写法

| 方一些，立得稳 | 横势略扬，末笔提得早 |
| --- | --- |
| ![方正笔迹写的「山外山。」](examples/upright.svg) | ![轻快笔迹写的「山外山。」](examples/running.svg) |
| [看第一副字帖](assets/example.json) | [看第二副字帖](examples/running-hand.json) |

看看两个「山」的右竖。左边那副到横画附近才停，右边那副向左下轻轻带出一点。每副字帖都给第二个「山」留了另一种写法。你自己的 AI 可以从完全不同的字开始。

## 给自己的 AI 试试

从 GitHub 的 **Code → Download ZIP** 下载并解压。把整个目录交给能读写文件、运行 Python 的 AI，或者将目录命名为 `write-in-your-own-hand` 放进客户端支持的 skills 目录。入口是 [SKILL.md](SKILL.md)。

第一次可以只说：

> 请读 SKILL.md，用你自己设计的字写一张便笺。内容和落款由你定。写好让我看，也把你的私人字帖存起来，下次接着写。

收到信后可以指着一笔改：

> 我喜欢这个「山」的折角。把「外」写得松一点，用同一句写两遍给我挑。

AI 会用相同的字和纸试写，等你挑中一处，再把它记进自己的字帖。想练连笔，可以挑两笔本来就顺手相接的地方，也可以让它把英文短词当成一整个动作来写。

## 在本机跑通第一张字样

在解压后的目录运行，需要 Python 3.9 或更高版本，只用标准库。

```sh
python scripts/write_letter.py assets/example.json assets/example.txt sample.svg
```

用浏览器打开 `sample.svg`。在 Windows 上也可把命令开头换成 `py -3`，在 macOS 或 Linux 上可用 `python3`。把第一个参数换成 `examples/running-hand.json` 就能重现右图。想看英文连笔，用右图的字帖，把正文保存成只含小写 `hi` 的 UTF-8 文本再运行一次。

写新信时，分别传入**私人字帖 JSON、信的正文 TXT、成品 SVG**。字帖按实际用字逐步扩充，遇到缺字会列出要补的字符。若要借本地笔顺骨架起稿，参数和坐标见[笔画格式说明](references/format.md)。要练顿笔、钩尖和连写，见[练字手记](references/notebook.md)。

## 公开分享

示例用了专门为演示写的短句和字形。私人字帖、真实落款、信件原文和成品可以放进已被 Git 忽略的 `private/`。SVG 的标题也含完整原文，提交新例子时请用适合公开的文字重新渲染。

项目内原创说明、代码与样例采用 **CC BY 4.0（知识共享署名 4.0 国际）**。转载或改编可按「自己的笔迹 / Write in Your Own Hand contributors」署名，附许可链接并注明修改。详见 [LICENSE](LICENSE)。
