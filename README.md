# Bilibili全自动举报
# BilibiliAutoReport
# 20240907更新  
## 写在前面————前言🤓☝️ 
一切都开始于某个中午，似乎是去年的我在家刷B站时被推广黄油的视频烦破防了，在Google上搜索了“Bilibili批量举报”，在一个中文论坛上找到了这个[bilibili批量举报【高危脚本】-油猴中文网](https://bbs.tampermonkey.net.cn/thread-5222-2-1.html)，下完后发现用不了。  
我当时上大四，学的软件工程，代码一点不会，完成课设全靠网上找项目，油猴脚本是用JavaScript写的，我一窍不通。只能把代码发给AI，描述需求，提供报错。当天下午脚本就完成了。  
最初B站还没有对举报频率进行限制，我甚至可以开多个窗口，同时举报多个UP，有的人甚至一天之内稿件被下架清空。大概过了一个月后，B站加了举报频率限制，举报频率过快会封禁IP，开个代理或者等一段时间就能解决问题。  
人机验证是一直都有的，每个账号每天可以免验证举报几十次，后续每60秒一次人机验证。  
当时还没有制作全自动脚本的打算。直到后来我买了个玩客云的小盒子，我发现青龙可以定时运行各种脚本。  
整个程序花了大概三天，全是用ChatGPT写的，先是用关键词获取违规视频，再获取发布违规视频的账号。后来发现用Selenium重写举报过程太麻烦，就直接把油猴脚本改了一下，安装到测试浏览器上。  
真正运行起来时才发现有人机验证，只能去找过人机验证的项目，再把项目融合进程序里，写好人机验证的循环。每天就是运行、发现问题、解决问题、运行然后发现新问题。好在当时毕设已经完事了，我有足够的时间。毕设也是用ChatGPT写的。  
今天是2024年9月7号，放假，可以写点东西。前两天刚发现B站采用了新机制，运行在测试浏览器上的小号过不了人机验证，开代理后恢复正常，运行在常用浏览器上的大号一切正常，切换到小号也一切正常。初步的解决方案是在代码里加个请求代理的脚本，吧找到的代理存起来，每次运行浏览器时随机用一个代理，运行完成后把代理删除。具体怎么办等我先测试一下详细的机制。  
B站也是离谱，发现举报变多了，不去治理被举报目标，反而开始阻止用户举报......  
## 配置使用方法（仅限Windows，需要下载PyCharm）🐍 
1，下载安装[PyCharm](https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC)  
2，按照[教程](https://www.bing.com/search?q=PyCharm%E5%AE%89%E8%A3%85%E6%B1%89%E5%8C%96%E6%95%99%E7%A8%8B)安装和汉化PyCharm  
3，下载Relaease，解压至D盘  
4，在Pycharm中打开“D:\BilibiliAutoReport”文件夹，在软件的最上方会有一个绿色三角形，点击可以运行指定文件，用左边向下的三角来切换脚本  
5，脚本解释：AAA可以打开浏览器进行配置，并测试Bilibili是否登录成功，Getuid用于运行搜索+举报功能，单独运行Report仅会举报uid.txt文件内的目标，Start是全自动运行所有功能，且出错后不会停止，会一直运行    
6，先运行AAA，在打开的浏览器中[登录Bilibili](https://www.bing.com/search?q=%E5%A6%82%E4%BD%95%E7%99%BB%E5%BD%95%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9)，并[安装油猴脚本](https://www.bing.com/search?q=%E5%A6%82%E4%BD%95%E5%AE%89%E8%A3%85%E6%B2%B9%E7%8C%B4%E8%84%9A%E6%9C%AC)  
7，关闭浏览器，点击左边向下三角，切换并运行Getuid，并查看是否成功启动浏览器
8，双击红色停止按钮，彻底停止脚本，切换至Start，点击绿色三角
9，脚本已运行  


## 低能耗使用方法（仅限Windows）👍   
1，使用常规方法配置完成    
2，关闭PyCharm  
3，进入“BilibiliVideoAutoReport-main”文件夹，双击11111111.bat运行      

## 程序逻辑🧠   
1，Start.是守护进程，负责启动其他两个脚本，运行后会启动Getuid  
2，Getuid从云端加载关键词列表、黑名单和白名单，用关键词搜索得到原始列表。原始列表+白名单-黑名单后，去重，重新写入文件uid.txt  
3，处理完uid会自动启动Report进行举报，如果中途出错将重新启动Report，如果Report正常退出则重新运行Getuid获得新列表  
4，Report脚本读取uid，逐个调用油猴脚本进行举报  
5，先进行人机验证，成功后导航至目标投稿页，完成后跳转目标专栏，专栏完成跳转动态。用户完成后会按照代码内容决定是否跳过人机验证    

  
## 目前问题😒  
1，采用关键词搜索寻找目标的方法容易误杀，未来可能会采取更好的方法来获取目标  
2，B站似乎会包庇粉丝量高的账号，比如[收藏夹里没东西_
](https://space.bilibili.com/452078996/video)，和[山海之花](https://space.bilibili.com/297993336/video)  


## 引用信息🤝  
1，项目中过人机验证的代码来自于[MgArcher/Text_select_captcha: 实现文字点选、选字、选择、点触验证码识别，基于pytorch训练](https://github.com/MgArcher/Text_select_captcha/)，感谢大佬  
2，油猴脚本的手动版在[这里](https://greasyfork.org/zh-CN/scripts/497079-bilibili%E7%A8%BF%E4%BB%B6%E6%89%B9%E9%87%8F%E4%B8%BE%E6%8A%A5)  
3，ChromeDriver的[官方下载地址](https://developer.chrome.com/docs/chromedriver?hl=zh-cn)  
 

