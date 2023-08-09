# [Python小白逆袭大神](https://aistudio.baidu.com/aistudio/education/group/info/1224)

该课程为 Paddle AI Studio 出品。2020年就已经结课，有些东西不能直接运行，这里记录一下。

下面简单的说一下几个作业情况。

## [青春有你2](https://baike.baidu.com/item/%E9%9D%92%E6%98%A5%E6%9C%89%E4%BD%A0%E7%AC%AC%E4%BA%8C%E5%AD%A3) 选手信息爬取

使用传统的 requests 模块不能过百度百科认证，具体情况可以看这篇[文章](https://segmentfault.com/q/1010000043342060)，所以我是用了 aiohttp 能够正确获取到网页内容。

其中的一些细节，比如网页元素的获取等等就不说了。

## [青春有你2](https://baike.baidu.com/item/%E9%9D%92%E6%98%A5%E6%9C%89%E4%BD%A0%E7%AC%AC%E4%BA%8C%E5%AD%A3) 选手数据分析

这里为了保持一致，使用了 2020 年提供的选手信息数据，代码没啥问题。

## [青春有你2](https://baike.baidu.com/item/%E9%9D%92%E6%98%A5%E6%9C%89%E4%BD%A0%E7%AC%AC%E4%BA%8C%E5%AD%A3) 选手识别

在 AI Studio 中无法复现，最终两张图片全识别为 <虞书欣>。

本地复现时没有注意版本问题，一开始就安装最近的版本，PaddleHub==2.3.1，paddlepaddle-gpu==2.4.2，但是注意到 PaddleHub 更新到 2.x 版本时，[BaseCVDataset不存在了](https://github.com/PaddlePaddle/PaddleHub/issues/1435)，由于不想更换环境，就不打算复现了，直接跳过。

## [青春有你2](https://baike.baidu.com/item/%E9%9D%92%E6%98%A5%E6%9C%89%E4%BD%A0%E7%AC%AC%E4%BA%8C%E5%AD%A3) 评论数据爬取分析

代码没有问题，调用 PaddleHub 中的 porn_detection_lstm 模块来进行评论内容审核。

