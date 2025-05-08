#!/bin/bash
#程式名稱:d01易經心理媽傳記.bash
#編輯:易經及媽傳記,修改時間:1041107 1091122 1101127 1121223
#製作為臨床心理諮商輔導合併媽傳記投影片 
#written by:幸安榮譽出品!
echo "現在時刻是:`date +%T`!臣妾shellscript率奴卑bash與sed,程式開始!"

#cd ..
#mkdir 備份d011夾2023`date +%T`
#cp -rf d011 備份d011夾2023`date +%T`
#cd ./d011

echo "奴才正在為皇上測試本電腦能否執行某些軟體!"
echo "測試完畢,謝皇上!"

echo "奴才正在為皇上建立執行本程式所需要用到的文檔與資料夾!"

cp -a 工具程式資料夾 工具程式資料夾現在要用
cp -a 基本資料資料夾 基本資料資料夾現在要用
cp -a HTML參考樣板資料夾 HTML參考樣板資料夾現在要用
cp -a 投影片參考樣板資料夾 投影片參考樣板資料夾現在要用
cp -a 易經輸入端資料夾 易經輸入端資料夾現在要用

for file in 基本資料資料夾現在要用/*.txt; do
    sed "s/\(..*\)\(  \)\(..*\)/\1 \&nbsp \3/" "$file" > "${file%.txt}格式化.txt"
done

declare -i i=0
for folder in 總戰果 總戰果1 總戰果2 戰果 中間成品 標記; do
    [ -d "易經$folder資料夾" ] && rm -rf "易經$folder資料夾"
    mkdir "易經$folder資料夾"
done

for folder in 1 2 3 4 5 6 7 8 9 10 11 12 戰果; do
    [ -d "易經維基網資料暫存$folder資料夾" ] && rm -rf "易經維基網資料暫存$folder資料夾"
    mkdir "易經維基網資料暫存$folder資料夾"
done

for folder in 1 2 3 4 5 戰果; do
    [ -d "易經古原文暫存$folder資料夾" ] && rm -rf "易經古原文暫存$folder資料夾"
    mkdir "易經古原文暫存$folder資料夾"
done

for folder in 1 2 3 4 5 戰果; do
    [ -d "易經HTML暫存$folder資料夾" ] && rm -rf "易經HTML暫存$folder資料夾"
    mkdir "易經HTML暫存$folder資料夾"
done

for folder in 1 2 3 4 5 6 7 8 9 10 11 12 戰果; do
    [ -d "易經投影片暫存$folder資料夾" ] && rm -rf "易經投影片暫存$folder資料夾"
    mkdir "易經投影片暫存$folder資料夾"
done

echo "建立完畢,謝皇上!"

echo "" > 垃圾sed.sed
declare -i i=0
for course in `cat 工具程式資料夾現在要用/掃垃圾文字.txt`; do
    i=i+1
    echo "/$course/c\\" >> 垃圾sed.sed
    echo "$course是垃圾" >> 垃圾sed.sed
done

echo " " > 垃圾再一次sed.sed
declare -i i=0
for course in `cat 工具程式資料夾現在要用/掃垃圾文字再一次.txt`; do
    i=i+1
    echo "/$course/c\\" >> 垃圾再一次sed.sed
    echo " " >> 垃圾再一次sed.sed
done

echo "" > 感染專有名詞sed.sed
declare -i g=0
for course in `cat 易經輸入端資料夾現在要用/易經自選專有名詞.txt`; do
    g=g+1
    echo "/$course/c\\" >> 感染專有名詞sed.sed
    echo "<A HREF=\"http://zh.wikipedia.org/zh-tw/$course\" target=\"_new\">$course</A>" >> 感染專有名詞sed.sed
done

echo "" > 專有名詞我要獨立列sed.sed
declare -i g=0
for course in `cat 易經輸入端資料夾現在要用/易經自選專有名詞.txt`; do
    g=g+1
    echo "s/$course/\\n--&--\\n/g" >> 專有名詞我要獨立列sed.sed
done

echo "奴才將為皇上下載自選標題維基資料! 奴才斗膽敢問皇上想從自選標題第幾列開始?"
echo -e '\a'
begin_line_self_topic=1
echo "$begin_line_self_topic" > begin_line_self_topic.txt
echo "奴才再斗膽敢問皇上想至自選標題第幾列結束?"
end_line_self_topic=1
echo "$end_line_self_topic" > end_line_self_topic.txt
echo "奴才將為皇上挑選第$begin_line_self_topic列到第$end_line_self_topic列的自選標題維基資料下載!"
echo "這是本王自選標題維基資料下載" > 易經維基網資料暫存戰果資料夾/自選專有名詞維基文獻.txt
echo "" >> 易經維基網資料暫存戰果資料夾/自選專有名詞維基文獻.txt

declare -i i=`expr $begin_line_self_topic - 1`
sed -n "`cat begin_line_self_topic.txt`,`cat end_line_self_topic.txt`p" 易經輸入端資料夾現在要用/易經自選專有名詞.txt > 風水自選專有名詞測試第$begin_line_self_topic到第$end_line_self_topic列.txt

for course in `cat 風水自選專有名詞測試第$begin_line_self_topic到第$end_line_self_topic列.txt`; do
    i=i+1
    echo "" >> 易經維基網資料暫存戰果資料夾/自選專有名詞維基文獻.txt
    echo "這是本王的資料---$course---" >> 易經維基網資料暫存戰果資料夾/自選專有名詞維基文獻.txt
    w3m "http://zh.wikipedia.org/zh-tw/$course" > 易經維基網資料暫存1資料夾/自選專有名詞維基文獻粗1第$i條.txt

    grep -v "^$" 易經維基網資料暫存1資料夾/自選專有名詞維基文獻粗1第$i條.txt > 易經維基網資料暫存2資料夾/自選專有名詞維基文獻粗2去空白行第$i條.txt
    sed -f 垃圾sed.sed 易經維基網資料暫存2資料夾/自選專有名詞維基文獻粗2去空白行第$i條.txt > 易經維基網資料暫存2資料夾/自選專有名詞維基文獻粗2垃圾標記第$i條.txt
    sed "s/\(..*\)\(是垃圾\)/垃圾點a\n\n\1\2/" 易經維基網資料暫存2資料夾/自選專有名詞維基文獻粗2垃圾標記第$i條.txt > 易經維基網資料暫存2資料夾/自選專有名詞維基文獻粗2垃圾點a第$i條.txt

    declare -i g=0
    for incourse in `cat 工具程式資料夾現在要用/掃垃圾文字.txt`; do
        g=g+1
        sed -n "/$incourse是垃圾/,/垃圾點a$/p" 易經維基網資料暫存2資料夾/自選專有名詞維基文獻粗2垃圾點a第$i條.txt > 易經維基網資料暫存3資料夾/自選專有名詞維基文獻粗3第$i條的$incourse.txt
    done

    grep -l "$course" 易經維基網資料暫存3資料夾/自選專有名詞維基文獻粗3第*.txt > 含有$course的片段的檔名.txt
    echo "my luck to you" > 易經維基網資料暫存4資料夾/含有$course.txt
    echo "" >> 易經維基網資料暫存4資料夾/含有$course.txt
    declare -i k=0
    for paper in `cat 含有$course的片段的檔名.txt`; do
        k=k+1
        cat "$paper" >> 易經維基網資料暫存4資料夾/含有$course.txt
        echo "" >> 易經維基網資料暫存4資料夾/含有$course.txt
    done

    sed -n "/^$course..*/,/參考[資文][料獻]/p" 易經維基網資料暫存4資料夾/含有$course.txt > 易經維基網資料暫存5資料夾/含有$course粗掃.txt
    echo "以下是$course維基網資料" > 易經維基網資料暫存戰果資料夾/自選專有名詞維基文獻第$i條$course.txt
    sed -f 垃圾再一次sed.sed 易經維基網資料暫存5資料夾/含有$course粗掃.txt >> 易經維基網資料暫存戰果資料夾/自選專有名詞維基文獻第$i條$course.txt
    echo "" >> 易經維基網資料暫存戰果資料夾/自選專有名詞維基文獻第$i條$course.txt
    cat 易經維基網資料暫存戰果資料夾/自選專有名詞維基文獻第$i條$course.txt >> 易經維基網資料暫存戰果資料夾/自選專有名詞維基文獻.txt
done

echo "下載完畢,謝皇上!"

	echo '以下是風水專有名詞維基文獻' >> 易經總戰果資料夾/我的著作文獻部份.txt
	echo "" >> 易經總戰果資料夾/我的著作文獻部份.txt
	cat 易經維基網資料暫存戰果資料夾/自選專有名詞維基文獻.txt >> 易經總戰果資料夾/我的著作文獻部份.txt

##<02>以下進入易經古原文編輯
	echo "奴才正在為皇上編輯易經古原文資料!"
	grep -v '^$' 易經輸入端資料夾現在要用/yijing.txt > 易經古原文暫存1資料夾/yijing暫存檔1.txt	#全文去除雙空白行
	sed 's/%/&\n/p' 易經古原文暫存1資料夾/yijing暫存檔1.txt > 易經古原文暫存1資料夾/yijing暫存檔2.txt	#利用%使不同病名之間增加空行
	grep -v '%' 易經古原文暫存1資料夾/yijing暫存檔2.txt > 易經古原文暫存1資料夾/yijing暫存檔3.txt	#殺了%不同病名之間就有空行了
	sed 's/\(《易經》\)\(.*\)/\1\n\1\2/1' 易經古原文暫存1資料夾/yijing暫存檔3.txt > 易經古原文暫存1資料夾/yijing暫存檔4.txt	#使《易經》第一卦 乾 乾為天 乾上乾下  之後的資料換列原句,多出《易經》領導行,必再加一列,因為本來就獨立列
	sed 's/\(彖曰：\)\(.*\)/\\xxxx\n\1\2/1' 易經古原文暫存1資料夾/yijing暫存檔4.txt > 易經古原文暫存1資料夾/yijing暫存檔5.txt 
	sed 's/\(象曰：\)\(.*\)/\\xxx\n\1\2/1' 易經古原文暫存1資料夾/yijing暫存檔5.txt > 易經古原文暫存1資料夾/yijing暫存檔6.txt 
	sed 's/\(文言曰：\)\(.*\)/\\xx\n\1\2/1' 易經古原文暫存1資料夾/yijing暫存檔6.txt > 易經古原文暫存1資料夾/yijing暫存檔7.txt 
	sed 's/\(初.*：\)\(.*\)/\\xxxxx\n\1\2/1' 易經古原文暫存1資料夾/yijing暫存檔7.txt > 易經古原文暫存戰果資料夾/yijing每卦到空列分隔全文文本有分斷點.txt	#《易經》到空列分隔每卦之全文粗文本

#以下產生卦名專有名詞的固定格式報表檔,以前用Awk作比較好寫,為了程式方法精簡,只用bash與sed,所以費力改成sed
	sed -n "s/\(《易經》\)\(第..*卦\)\(  *\)\([^ ][^ ]*\)\(  *\)\([^ ][^ ]*\)\(  *\)\([^ ][^ ]*\)/\2 \4 \6 \8/p" 易經古原文暫存戰果資料夾/yijing每卦到空列分隔全文文本有分斷點.txt > 易經古原文暫存戰果資料夾/yijing含有卦名首列.txt	#根據易經古文原本產生的含有卦名首列,第一卦的例子是:《易經》	第一卦              乾          乾為天          乾上乾下,過濾的資料
	sed -n "s/\(《易經》\)\(第..*卦\)\(  *\)\([^ ][^ ]*\)\(  *\)\([^ ][^ ]*\)\(  *\)\([^ ][^ ]*\)/\4/p" 易經古原文暫存戰果資料夾/yijing每卦到空列分隔全文文本有分斷點.txt > 易經古原文暫存戰果資料夾/yijing標題.txt	#卦名名稱,第一列是:乾  
	sed -n "s/\(《易經》\)\(第..*卦\)\(  *\)\([^ ][^ ]*\)\(  *\)\([^ ][^ ]*\)\(  *\)\([^ ][^ ]*\)/\2/p" 易經古原文暫存戰果資料夾/yijing每卦到空列分隔全文文本有分斷點.txt > 易經古原文暫存戰果資料夾/yijing順序.txt	#卦的國字數目編號順序,第一列是:第一卦
	sed -n "s/\(《易經》\)\(第..*卦\)\(  *\)\([^ ][^ ]*\)\(  *\)\([^ ][^ ]*\)\(  *\)\([^ ][^ ]*\)/\2 \4/p" 易經古原文暫存戰果資料夾/yijing每卦到空列分隔全文文本有分斷點.txt > 易經古原文暫存戰果資料夾/yijing順序標題.txt	#卦的國字數目編號順序 卦名, 分成2攔,第一列是:第一卦 乾
	sed -n "s/\(《易經》\)\(第..*卦\)\(  *\)\([^ ][^ ]*\)\(  *\)\([^ ][^ ]*\)\(  *\)\([^ ][^ ]*\)/啟稟皇上,易經\2是\4卦!,本卦看起來是\6, 由\8組成!/p" 易經古原文暫存戰果資料夾/yijing每卦到空列分隔全文文本有分斷點.txt > 易經古原文暫存戰果資料夾/yijing標題列智慧解說.txt	#卦名首列翻譯白話				
				
	
#將易經標題(乾,坤)製成sed感染,目標是維基百科,本段不放上面跟垃圾及專有名詞一起,是因為來源後出,易經古原文暫存戰果資料夾/yijing標題.txt是本程式製造出來的, 而垃圾及專有名詞仍舊是從輸入端拷貝來的
	echo "" > 感染易經標題sed.sed
	declare -i g=0
	for course in `cat 易經古原文暫存戰果資料夾/yijing標題.txt`
	do 
	g=g+1
	echo "/$course/c\\" >> 感染易經標題sed.sed
	echo "<A HREF=\"http://zh.wikipedia.org/zh-tw/$course\" target=\"_new\">$course</A>" >> 感染易經標題sed.sed
	done

#將易經標題(乾,坤)製成我要獨立列,小心會幹掉一整列其它文字
	echo "" > 易經標題我要獨立列sed.sed
	declare -i g=0
	for course in `cat 易經古原文暫存戰果資料夾/yijing標題.txt`
	do 
	g=g+1
	echo "s/$course/\\n--&--\\n/g" >> 易經標題我要獨立列sed.sed
	done


#以下程式作出易經各個卦的yijing編號.txt(全文切開成個別64卦)文件存檔
	declare -i i=0
	for course in `cat 易經古原文暫存戰果資料夾/yijing順序.txt`	#卦的國字數目編號順序,第一列是:第一卦
	do
	i=i+1
	echo "$i" >> 易經古原文暫存2資料夾/yijing暫存檔8_$i.txt	#先起首各卦阿拉伯數字
	sed -n "/$course/,/《易經》$/p" 易經古原文暫存戰果資料夾/yijing每卦到空列分隔全文文本有分斷點.txt >> 易經古原文暫存2資料夾/yijing暫存檔8_$i.txt 		#個別卦名切開粗檔案開始
	sed -n '/[1-9]$/!p' 易經古原文暫存2資料夾/yijing暫存檔8_$i.txt > 易經古原文暫存3資料夾/yijing暫存檔9_$i.txt	#暫時殺了起首各卦阿拉伯數字  
	sed -n '/《易經》$/!p' 易經古原文暫存3資料夾/yijing暫存檔9_$i.txt > 易經古原文暫存4資料夾/yijing暫存檔10_$i.txt	#殺了沒用的《易經》領導行,因為已經切開了
	sed -n '/x$/!p' 易經古原文暫存4資料夾/yijing暫存檔10_$i.txt > 易經古原文暫存5資料夾/yijing暫存檔11_$i.txt	#暫時殺了分斷點x  
	grep -v '^$' 易經古原文暫存5資料夾/yijing暫存檔11_$i.txt > 易經古原文暫存戰果資料夾/yijing切開第$i卦古原文無分斷點.txt	#殺了空白列,產生個別卦名分段檔案,原來古原文全文保留
	sed -n "s/\($course\) *\(..*\)/\2/p" 易經古原文暫存戰果資料夾/yijing順序標題.txt > 易經古原文暫存戰果資料夾/yijing第$i卦古原文分段切開卦名.txt	#第二行卦名入分開檔前面的卦名都是合在一起
	done	
	echo "編輯完畢,謝皇上!"	


##<02-1>非互動式投影片易經古文部份1:各卦全文
	echo "" > 易經卦名古文投影片sed.sed

	echo "/投影片1字/c\\" >> 易經卦名古文投影片sed.sed 
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第1張投影片作執行長學經歷
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/001執行長學經歷格式化.txt > 001執行長學經歷加換列符.txt
	cat 001執行長學經歷加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片2字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第2張投影片作總顧問學經歷
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/002總顧問學經歷格式化.txt > 002總顧問學經歷格式化加換列符.txt
	cat 002總顧問學經歷格式化加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片3字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第3張投影片作中藥局營業項目
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/003中藥局營業項目.txt > 003中藥局營業項目加換列符.txt
	cat 003中藥局營業項目加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片4字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第4張投影片作中藥局經營理念
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/004中藥局經營理念.txt > 004中藥局經營理念加換列符.txt
	cat  004中藥局經營理念加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片5字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第5張投影片作中藥局歷史源流
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/005中藥局歷史源流.txt > 005中藥局歷史源流加換列符.txt
	cat  005中藥局歷史源流加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片6字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第6張投影片作中藥局診療日記
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/006中藥局診療日記1090101.txt > 006中藥局診療日記1090101加換列符.txt
	cat  006中藥局診療日記1090101加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "" >> 易經卦名古文投影片sed.sed
	declare -i k=0
	for problem in `cat 易經古原文暫存戰果資料夾/yijing標題.txt`	##第七張投影片起作期刊論文逐一播放 
	do 
	k=k+1
	echo "易經古文共有64卦,本段為第$k卦$problem卦的條文<\/br>\\" > 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符.txt
	sed -n 's/$/<br>\\/p' 易經古原文暫存戰果資料夾/yijing切開第$k卦古原文無分斷點.txt >> 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符.txt	#上面切開的用到了
	b=`expr $k + 6`	##第七張投影片起放考古第一題
	echo "/投影片$b字/c\\" >> 易經卦名古文投影片sed.sed
	
	cat 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符.txt | wc -l > 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符行數.txt	#統計行數

	a=`cat 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符行數.txt`
	if [ $a -gt 10 ]
	then sed -n '1,10p' 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符.txt > 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符只有前十列.txt

	echo "......<br>\\" >> 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符只有前十列.txt
	echo "<a href=\"../易經投影片暫存1資料夾/易經古原文第$k卦文加換列符.txt\" target=\"_new\">..我要看整段原文</a>" >> 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符只有前十列.txt	#看不夠要看全段也可以

	else sed -n '1,$p' 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符.txt > 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符只有前十列.txt
	fi

	cat 易經投影片暫存1資料夾/易經古原文第$k卦文加換列符只有前十列.txt >> 易經卦名古文投影片sed.sed

	done


	echo "" > 易經投影片暫存2資料夾/index期刊中段粗.html	##製作樣板個數
	l=0
	while [ $l -lt 67 ]
	do
	l=`expr $l + 1`
	a=`expr -8000 + 1000 \* $l`
	echo '<q><strong><center>' >> 易經投影片暫存2資料夾/index期刊中段粗.html 
	echo "易經古文解析講座" >> 易經投影片暫存2資料夾/index期刊中段粗.html
	echo '</br></center></strong><b>' >> 易經投影片暫存2資料夾/index期刊中段粗.html
	echo "投影片$l字段" >> 易經投影片暫存2資料夾/index期刊中段粗.html
	echo '</b></q>' >> 易經投影片暫存2資料夾/index期刊中段粗.html
	echo '</div>' >> 易經投影片暫存2資料夾/index期刊中段粗.html
	echo "<div class=\"step slide\" data-x=\"$a\" data-y=\"-1500\">" >> 易經投影片暫存2資料夾/index期刊中段粗.html
	done
	sed '$d' 易經投影片暫存2資料夾/index期刊中段粗.html > 易經投影片暫存2資料夾/index期刊中段.html

	cat 投影片參考樣板資料夾現在要用/index起段.html > 易經投影片暫存2資料夾/投影片秀易經卦名古文粗.html	##連接樣板
	cat 易經投影片暫存2資料夾/index期刊中段.html >> 易經投影片暫存2資料夾/投影片秀易經卦名古文粗.html
	cat 投影片參考樣板資料夾現在要用/index止段.html >> 易經投影片暫存2資料夾/投影片秀易經卦名古文粗.html
	sed -f 易經卦名古文投影片sed.sed 易經投影片暫存2資料夾/投影片秀易經卦名古文粗.html > 投影片參考樣板資料夾現在要用/投影片秀易經古文解析講座$course.html
#####開檔1號
echo "Generated HTML file: 投影片參考樣板資料夾現在要用/投影片秀易經古文解析講座$course.html"	##先放易經古文分卦全文投影片
	cp -a 投影片參考樣板資料夾現在要用 易經總戰果1資料夾	#怕放完就不見了,所以另存暫存戰果資料夾
	rm -rf 投影片參考樣板資料夾現在要用
	cp -a 投影片參考樣板資料夾 投影片參考樣板資料夾現在要用	#復歸原始  


##<02-2>非互動式投影片易經古文部份2:卦駁段塈媽傳記投影片
	echo "" > 易經卦名古文投影片sed.sed
	
	echo "/投影片1字/c\\" >> 易經卦名古文投影片sed.sed 
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第1張投影片作執行長學經歷
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/000出版社營業項目格式化.txt > 000出版社營業項目格式化加換列符.txt
	cat 000出版社營業項目格式化加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed	

	echo "/投影片2字/c\\" >> 易經卦名古文投影片sed.sed 
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第1張投影片作執行長學經歷
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/001執行長學經歷格式化.txt > 001執行長學經歷加換列符.txt
	cat 001執行長學經歷加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片3字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第2張投影片作總顧問學經歷
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/002總顧問學經歷格式化.txt > 002總顧問學經歷格式化加換列符.txt
	cat 002總顧問學經歷格式化加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片4字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第3張投影片作中藥局營業項目
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/003中藥局營業項目.txt > 003中藥局營業項目加換列符.txt
	cat 003中藥局營業項目加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片5字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第4張投影片作中藥局經營理念
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/004中藥局經營理念.txt > 004中藥局經營理念加換列符.txt
	cat  004中藥局經營理念加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片6字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第5張投影片作中藥局歷史源流
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/005中藥局歷史源流.txt > 005中藥局歷史源流加換列符.txt
	cat  005中藥局歷史源流加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片7字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第6張投影片作中藥局診療日記
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/006中藥局診療日記1090101.txt > 006中藥局診療日記1090101加換列符.txt
	cat  006中藥局診療日記1090101加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "" >> 易經卦名古文投影片sed.sed
	declare -i k=0
	for problem in `cat 易經古原文暫存戰果資料夾/yijing標題.txt`	##第七張投影片起作期刊論文逐一播放 
	do 
	k=k+1
	b=`expr $k + 7`	##第四張投影片起放考古第一題
	echo "/投影片$b字/c\\" >> 易經卦名古文投影片sed.sed

#開始組合媽手記相片,記事本,媽文章,生活照,演講,變色盤,易經卦駁段
	sed -n 's/$/<br>\\/p' 投影片參考樣板資料夾現在要用/媽手記相片程式.txt > 媽手記相片程式有換列符.txt
cat 媽手記相片程式有換列符.txt >> 易經卦名古文投影片sed.sed
	sed -n 's/$/<br>\\/p' 投影片參考樣板資料夾現在要用/記事本程式.txt > 記事本程式有換列符.txt
cat 記事本程式有換列符.txt >> 易經卦名古文投影片sed.sed

	echo "易經古文共有64卦,本段為第$k卦$problem卦的卦駁段" > 易經投影片暫存3資料夾/易經古原文第$k卦文標題列包皮1.txt
	sed "s/\(..*\)\($problem\)\(..*\)/\1<a href=\"https:\/\/www\.ncbi\.nlm\.nih\.gov\/pubmed\/\2\"\>Look!$k國衛院<\/a\>,\2\3\n下一待用網址/" 易經投影片暫存3資料夾/易經古原文第$k卦文標題列包皮1.txt > 易經投影片暫存3資料夾/易經古原文第$k卦文標題列包皮2.txt
	sed "s/下一待用網址/<a href=\"http:\/\/zh\.wikipedia\.org\/zh-tw\/$problem\" target=\"_new\"\>我看維基<\/a\> Look!$k維基,下一待用網址/" 易經投影片暫存3資料夾/易經古原文第$k卦文標題列包皮2.txt > 易經投影片暫存3資料夾/易經古原文第$k卦文標題列包皮3.txt
	sed "s/\(..*\)\(下一待用網址\)/\1<a href=\"http:\/\/www\.google\.com\/search?q=%$problem\" target=\"_new\"\>我看谷歌<\/a\>Look!$k谷歌,下一待用網址/" 易經投影片暫存3資料夾/易經古原文第$k卦文標題列包皮3.txt > 易經投影片暫存3資料夾/易經古原文第$k卦文標題列有包皮.txt
	sed -n 's/$/<br>\\/p' 易經投影片暫存3資料夾/易經古原文第$k卦文標題列有包皮.txt > 易經投影片暫存3資料夾/易經古原文第$k卦文標題列有包皮加換列符.txt
#cat 易經投影片暫存3資料夾/易經古原文第$k卦文標題列有包皮加換列符.txt >> 易經卦名古文投影片sed.sed

sed "s/\(..*\)\(b\)\(\.jpg..*\)/\1b$k\3/" 投影片參考樣板資料夾現在要用/我相片程式.txt > 我相片程式$k.txt
	sed -n 's/$/<br>\\/p' 我相片程式$k.txt > 我相片程式有換列符.txt
cat 我相片程式有換列符.txt >> 易經卦名古文投影片sed.sed
	
	l=`expr $k + 1`	#媽寫的內容
	sed -n "/m$k[^0-9]/,/m$l/p" m.txt > 媽寫的內容第$k卦駁段.txt
	sed -n '1,2p' 媽寫的內容第$k卦駁段.txt > 媽寫的內容第$k卦駁段前二列a.txt
sed "s/\(m$k\)\([^0-9]..*\)\(\(.*\)\)/\2/g" 媽寫的內容第$k卦駁段前二列a.txt > 媽寫的內容第$k卦駁段前二列.txt 
	sed -n 's/$/<br>\\/p' 媽寫的內容第$k卦駁段前二列.txt > 媽寫的內容第$k卦駁段前二列有換列符.txt 	
	cat 媽寫的內容第$k卦駁段前二列有換列符.txt >> 易經卦名古文投影片sed.sed 

	sed -n '3,4p' 媽寫的內容第$k卦駁段.txt > 媽寫的內容第$k卦駁段中二列.txt
	sed -n 's/$/<br>\\/p' 媽寫的內容第$k卦駁段中二列.txt > 媽寫的內容第$k卦駁段中二列有換列符.txt
	cat 媽寫的內容第$k卦駁段中二列有換列符.txt >> 易經卦名古文投影片sed.sed

	sed -n 's/$/<br>\\/p' 投影片參考樣板資料夾現在要用/我多媒體程式.txt > 我多媒體程式有換列符.txt
cat 我多媒體程式有換列符.txt >> 易經卦名古文投影片sed.sed

	sed '1,4d' 媽寫的內容第$k卦駁段.txt > 媽寫的內容第$k卦駁段後列a.txt
sed '$d' 媽寫的內容第$k卦駁段後列a.txt > 媽寫的內容第$k卦駁段後列.txt		
	sed -n 's/$/<br>\\/p' 媽寫的內容第$k卦駁段後列.txt > 媽寫的內容第$k卦駁段後列有換列符.txt	
	cat 媽寫的內容第$k卦駁段後列有換列符.txt >> 易經卦名古文投影片sed.sed

	sed -n 's/$/<br>\\/p' 投影片參考樣板資料夾現在要用/變色盤程式.txt > 變色盤程式有換列符.txt
cat 變色盤程式有換列符.txt >> 易經卦名古文投影片sed.sed
	

	sed -n "/^[初上六九][六九二三四五]/p" 易經古原文暫存戰果資料夾/yijing切開第$k卦古原文無分斷點.txt > 易經投影片暫存5資料夾/易經古原文第$k卦駁段.txt

	echo "" > 易經投影片暫存5資料夾/易經古原文第$k卦駁段有圖.txt
	declare -i i=0
	for problem in `cat 易經投影片暫存5資料夾/易經古原文第$k卦駁段.txt`	
	do 
	i=i+1
	echo "$problem" > 易經投影片暫存6資料夾/日a$i.txt
	sed "/^九/s/$/\&nbsp\&nbsp\&nbsp日日日日日日/p" 易經投影片暫存6資料夾/日a$i.txt > 易經投影片暫存6資料夾/日b$i.txt
	sed "/^.九/s/$/\&nbsp\&nbsp\&nbsp日日日日日日/p" 易經投影片暫存6資料夾/日b$i.txt > 易經投影片暫存6資料夾/日bb$i.txt
	sed "/^六/s/$/\&nbsp\&nbsp\&nbsp日日囗囗日日/p" 易經投影片暫存6資料夾/日bb$i.txt > 易經投影片暫存6資料夾/日c$i.txt
	sed "/^.六/s/$/\&nbsp\&nbsp\&nbsp日日囗囗日日/p" 易經投影片暫存6資料夾/日c$i.txt > 易經投影片暫存6資料夾/日cc$i.txt
	sed -n '1p' 易經投影片暫存6資料夾/日cc$i.txt > 易經投影片暫存6資料夾/日d$i.txt
	cat 易經投影片暫存6資料夾/日d$i.txt >> 易經投影片暫存5資料夾/易經古原文第$k卦駁段有圖.txt
	done


	sed -n 's/$/<br>\\/p' 易經投影片暫存5資料夾/易經古原文第$k卦駁段有圖.txt > 易經投影片暫存5資料夾/易經古原文第$k卦駁段有圖有換列符.txt
	cat 易經投影片暫存5資料夾/易經古原文第$k卦駁段有圖有換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed
	done

	echo "" > 易經投影片暫存9資料夾/index期刊中段粗.html	##製作樣板個數
	l=0
	while [ $l -lt 67 ]
	do
	l=`expr $l + 1`
	a=`expr -8000 + 1000 \* $l`
#echo '<q><strong><center>' >> 易經投影片暫存9資料夾/index期刊中段粗.html 
#echo "易經古文解析講座" >> 易經投影片暫存9資料夾/index期刊中段粗.html
#echo '</br></center></strong><b>' >> 易經投影片暫存9資料夾/index期刊中段粗.html
	echo "投影片$l字段" >> 易經投影片暫存9資料夾/index期刊中段粗.html
	echo '</b></q>' >> 易經投影片暫存9資料夾/index期刊中段粗.html
	echo '</div>' >> 易經投影片暫存9資料夾/index期刊中段粗.html
	echo "<div class=\"step slide\" data-x=\"$a\" data-y=\"-1500\">" >> 易經投影片暫存9資料夾/index期刊中段粗.html
	done
	sed '$d' 易經投影片暫存9資料夾/index期刊中段粗.html > 易經投影片暫存9資料夾/index期刊中段.html

	cat 投影片參考樣板資料夾現在要用/index起段.html > 易經投影片暫存9資料夾/投影片秀易經卦名古文粗.html	##連接樣板
	cat 易經投影片暫存9資料夾/index期刊中段.html >> 易經投影片暫存9資料夾/投影片秀易經卦名古文粗.html
	cat 投影片參考樣板資料夾現在要用/index止段.html >> 易經投影片暫存9資料夾/投影片秀易經卦名古文粗.html
	sed -f 易經卦名古文投影片sed.sed 易經投影片暫存9資料夾/投影片秀易經卦名古文粗.html > 投影片參考樣板資料夾現在要用/投影片秀易經古文解析講座卦駁段$course.html


#####開檔2號
echo "Generated HTML file: 投影片參考樣板資料夾現在要用/投影片秀易經古文解析講座卦駁段$course.html"	##再放分段卦駁文投影片
	cp -a 投影片參考樣板資料夾現在要用 易經總戰果1資料夾	#怕放完就不見了,所以另存暫存戰果資料夾	
	rm -rf 投影片參考樣板資料夾現在要用
	cp -a 投影片參考樣板資料夾 投影片參考樣板資料夾現在要用	#復歸原始 


##<02-3>非互動式投影片易經古文部份3:彖象段
	echo "" > 易經卦名古文投影片sed.sed

	echo "/投影片1字/c\\" >> 易經卦名古文投影片sed.sed 
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第1張投影片作執行長學經歷
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/001執行長學經歷格式化.txt > 001執行長學經歷加換列符.txt
	cat 001執行長學經歷加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片2字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第2張投影片作總顧問學經歷
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/002總顧問學經歷格式化.txt > 002總顧問學經歷格式化加換列符.txt
	cat 002總顧問學經歷格式化加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片3字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第3張投影片作中藥局營業項目
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/003中藥局營業項目.txt > 003中藥局營業項目加換列符.txt
	cat 003中藥局營業項目加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片4字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第7張投影片作中藥局經營理念
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/004中藥局經營理念.txt > 004中藥局經營理念加換列符.txt
	cat  004中藥局經營理念加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片5字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第5張投影片作中藥局歷史源流
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/005中藥局歷史源流.txt > 005中藥局歷史源流加換列符.txt
	cat  005中藥局歷史源流加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "/投影片6字/c\\" >> 易經卦名古文投影片sed.sed
	echo "<center>竹文診所</center>\\" >> 易經卦名古文投影片sed.sed	##第6張投影片作中藥局診療日記
	sed -n 's/$/<br>\\/p' 基本資料資料夾現在要用/006中藥局診療日記1090101.txt > 006中藥局診療日記1090101加換列符.txt
	cat  006中藥局診療日記1090101加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed

	echo "" >> 易經卦名古文投影片sed.sed
	declare -i k=0
	for problem in `cat 易經古原文暫存戰果資料夾/yijing標題.txt`	##第四張投影片起作期刊論文逐一播放 
	do 
	k=k+1
	echo "易經古文共有64卦,本段為第$k卦$problem卦的彖象段<\/br>\\" > 易經投影片暫存10資料夾/易經古原文第$k卦文加換列符.txt
	sed -n 's/$/<br>\\/p' 易經古原文暫存戰果資料夾/yijing切開第$k卦古原文無分斷點.txt >> 易經投影片暫存10資料夾/易經古原文第$k卦文加換列符.txt	#上面切開的用到了
	b=`expr $k + 6`	##第七張投影片起放考古第一題
	echo "/投影片$b字/c\\" >> 易經卦名古文投影片sed.sed
	echo "易經古文共有64卦,本段為第$k卦$problem卦的彖象段" > 易經投影片暫存11資料夾/易經古原文第$k卦彖象段粗1.txt
	sed "s/\(..*\)\($problem\)\(..*\)/\1<a href=\"https:\/\/www\.ncbi\.nlm\.nih\.gov\/pubmed\/\2\"\>Look!$k國衛院<\/a\>,\2\3\n下一待用網址/" 易經投影片暫存11資料夾/易經古原文第$k卦彖象段粗1.txt > 易經投影片暫存11資料夾/易經古原文第$k卦彖象段粗2.txt
	sed "s/下一待用網址/<a href=\"http:\/\/zh\.wikipedia\.org\/zh-tw\/$problem\" target=\"_new\"\>我看維基<\/a\> Look!$k維基,下一待用網址/" 易經投影片暫存11資料夾/易經古原文第$k卦彖象段粗2.txt > 易經投影片暫存11資料夾/易經古原文第$k卦彖象段粗3.txt
	sed "s/\(..*\)\(下一待用網址\)/\1<a href=\"http:\/\/www\.google\.com\/search?q=%$problem\" target=\"_new\"\>我看谷歌<\/a\>Look!$k谷歌,下一待用網址/" 易經投影片暫存11資料夾/易經古原文第$k卦彖象段粗3.txt > 易經投影片暫存11資料夾/易經古原文第$k卦彖象段粗4.txt
	sed -n 's/$/<br>\\/p' 易經投影片暫存11資料夾/易經古原文第$k卦彖象段粗4.txt > 易經投影片暫存11資料夾/易經古原文第$k卦彖象段加換列符.txt
	sed -n "/彖曰/,/象曰/p" 易經投影片暫存10資料夾/易經古原文第$k卦文加換列符.txt >> 易經投影片暫存11資料夾/易經古原文第$k卦彖象段加換列符.txt
	cat 易經投影片暫存11資料夾/易經古原文第$k卦彖象段加換列符.txt >> 易經卦名古文投影片sed.sed
	echo "-----------------------" >> 易經卦名古文投影片sed.sed
	done

	echo "" > 易經投影片暫存12資料夾/index期刊中段粗.html	##製作樣板個數
	l=0
	while [ $l -lt 67 ]
	do
	l=`expr $l + 1`
	a=`expr -8000 + 1000 \* $l`
	echo '<q><strong><center>' >> 易經投影片暫存12資料夾/index期刊中段粗.html 
	echo "竹文診所" >> 易經投影片暫存12資料夾/index期刊中段粗.html
	echo '</br></center></strong><b>' >> 易經投影片暫存12資料夾/index期刊中段粗.html
	echo "投影片$l字段" >> 易經投影片暫存12資料夾/index期刊中段粗.html
	echo '</b></q>' >> 易經投影片暫存12資料夾/index期刊中段粗.html
	echo '</div>' >> 易經投影片暫存12資料夾/index期刊中段粗.html
	echo "<div class=\"step slide\" data-x=\"$a\" data-y=\"-1500\">" >> 易經投影片暫存12資料夾/index期刊中段粗.html
	done
	sed '$d' 易經投影片暫存12資料夾/index期刊中段粗.html > 易經投影片暫存12資料夾/index期刊中段.html

	cat 投影片參考樣板資料夾現在要用/index起段.html > 易經投影片暫存12資料夾/投影片秀易經卦名古文粗.html	##連接樣板
	cat 易經投影片暫存12資料夾/index期刊中段.html >> 易經投影片暫存12資料夾/投影片秀易經卦名古文粗.html
	cat 投影片參考樣板資料夾現在要用/index止段.html >> 易經投影片暫存12資料夾/投影片秀易經卦名古文粗.html
	sed -f 易經卦名古文投影片sed.sed 易經投影片暫存12資料夾/投影片秀易經卦名古文粗.html > 投影片參考樣板資料夾現在要用/投影片秀易經古文解析講座彖象段$course.html
#####開檔3號
#echo "Generated HTML file: 投影片參考樣板資料夾現在要用/投影片秀易經古文解析講座彖象段$course.html"	#放分段彖象投影片
	cp -a 投影片參考樣板資料夾現在要用 易經總戰果1資料夾	#怕放完就不見了,所以另存暫存戰果資料夾	
	rm -rf 投影片參考樣板資料夾現在要用
	cp -a 投影片參考樣板資料夾 投影片參考樣板資料夾現在要用	#復歸原始  

	
##<03>以下下載易經64卦卦義維基資料
	echo "奴才將為皇上下載易經64卦卦義維基資料! 奴才斗膽敢問皇上想從易經第幾卦開始?"
	echo -e '\a'
#gedit  易經古原文暫存戰果資料夾/yijing標題.txt
#read begin_line_yijing_topic
begin_line_yijing_topic=1
	echo "$begin_line_yijing_topic" > begin_line_yijing_topic.txt
	echo "奴才再斗膽敢問皇上想至自選標題第幾列結束?"
#read end_line_yijing_topic
end_line_yijing_topic=2
	echo "$end_line_yijing_topic" > end_line_yijing_topic.txt
	echo "奴才將為皇上挑選第$begin_line_yijing_topic列到第$end_line_yijing_topic列的易經64卦卦義維基資料下載!"
	echo "這是本王自選易經64卦卦義維基資料下載" > 易經維基網資料暫存戰果資料夾/yijing卦名維基文獻.txt
	echo "" >> 易經維基網資料暫存戰果資料夾/yijing卦名維基文獻.txt	#增加空列好看一點
	declare -i i=`expr $begin_line_yijing_topic - 1`
	sed -n "`cat begin_line_yijing_topic.txt`,`cat end_line_yijing_topic.txt`p" 易經古原文暫存戰果資料夾/yijing標題.txt > yijing順序測試第$begin_line_yijing_topic列到第$end_line_yijing_topic列.txt	
	for course in `cat yijing順序測試第$begin_line_yijing_topic列到第$end_line_yijing_topic列.txt`
	do
	i=i+1
	w3m "http://zh.wikipedia.org/zh-tw/$course" > 易經維基網資料暫存6資料夾/yijing第$i卦$course維基網資料網頁粗.txt	

#掃垃圾文字程式段開始
	grep -v "^$" 易經維基網資料暫存6資料夾/yijing第$i卦$course維基網資料網頁粗.txt > 易經維基網資料暫存7資料夾/yijing第$i卦$course維基網資料網頁去空白行.txt	
	sed -f 垃圾sed.sed 易經維基網資料暫存7資料夾/yijing第$i卦$course維基網資料網頁去空白行.txt > 易經維基網資料暫存8資料夾/yijing第$i卦$course維基網資料網頁垃圾標記.txt 
	sed "s/\(..*\)\(是垃圾\)/垃圾點a\n\n\1\2/" 易經維基網資料暫存8資料夾/yijing第$i卦$course維基網資料網頁垃圾標記.txt > 易經維基網資料暫存9資料夾/yijing第$i卦$course維基網資料網頁垃圾點a.txt

	declare -i g=0
	for incourse in `cat 工具程式資料夾現在要用/掃垃圾文字.txt` 
	do
	g=g+1	
	sed -n "/$incourse是垃圾/,/垃圾點a$/p" 易經維基網資料暫存9資料夾/yijing第$i卦$course維基網資料網頁垃圾點a.txt > 易經維基網資料暫存10資料夾/yijing第$i卦$course維基網資料網頁的$incourse.txt
	done	

	grep -l "$course" 易經維基網資料暫存10資料夾/yijing*.* > 含有第$i卦的片段的檔名.txt 
	echo "my luck to you!!!" > 易經維基網資料暫存11資料夾/含有第$i卦.txt
	echo "" >> 易經維基網資料暫存11資料夾/含有第$i卦.txt
	declare -i k=0
	for paper in `cat 含有第$i卦的片段的檔名.txt`
	do 
	k=k+1
	cat "$paper" >> 易經維基網資料暫存11資料夾/含有第$i卦.txt
	echo "" >> 易經維基網資料暫存11資料夾/含有第$i卦.txt
	done

	sed -n "/^$course..*/,/參考[資文][料獻]/p" 易經維基網資料暫存11資料夾/含有第$i卦.txt > 易經維基網資料暫存12資料夾/含有第$i卦粗掃.txt	#$name不能在檔名中因為以後要用卦序變數來叫檔案
	sed -f 垃圾再一次sed.sed 易經維基網資料暫存12資料夾/含有第$i卦粗掃.txt > 易經維基網資料暫存戰果資料夾/yijing第$i卦維基網資料網頁.inc	#以上先存分開的,以後可製Powerpoint(.ppt)網頁
#gedit 易經維基網資料暫存戰果資料夾/yijing第$i卦維基網資料網頁.inc	#先分開的用編輯器打開檢視手動修改一下再存檔,排網頁用
	echo "" >> 易經維基網資料暫存戰果資料夾/yijing卦名維基文獻.txt	#增加空列好看一點
	cat 易經維基網資料暫存戰果資料夾/yijing第$i卦維基網資料網頁.inc >> 易經維基網資料暫存戰果資料夾/yijing卦名維基文獻.txt	#再存組合的,以後可製Word(.doc)文件
	done
#以上易經自選卦名維基文獻存檔備用(分開的組合的都有),下面將設計HTML展開
#gedit 易經維基網資料暫存戰果資料夾/yijing卦名維基文獻.txt	#再組合的用編輯器打開檢視手動修改一下再存檔,編書用
	echo "下載完畢,謝皇上!"

	cat 易經維基網資料暫存戰果資料夾/yijing卦名維基文獻.txt >> 易經總戰果資料夾/我的著作文獻部份.txt
	echo "" >> 易經總戰果資料夾/我的著作文獻部份.txt
	echo "" >> 易經總戰果資料夾/我的著作文獻部份.txt

	
##<04>開始製作HTML網頁,上文段1為古原文<02>,下文段2為下載易經64卦卦義維基資料,<03>
	declare -i i=`expr $begin_line_yijing_topic - 1`
	for course in `cat yijing順序測試第$begin_line_yijing_topic列到第$end_line_yijing_topic列.txt`	#第二卦\n第三卦\n第四卦	
	do
	i=i+1
	echo "$course" >> 易經總戰果資料夾/我的著作文獻部份.txt
	cat 易經古原文暫存戰果資料夾/yijing切開第$i卦古原文無分斷點.txt >> 易經總戰果資料夾/我的著作文獻部份.txt	#古原文編書用
	echo "" >> 易經總戰果資料夾/我的著作文獻部份.txt
	sed -n 's/$/<\/br>/p' 易經古原文暫存戰果資料夾/yijing切開第$i卦古原文無分斷點.txt > 易經HTML暫存1資料夾/yijing第$i卦古原文網頁內容段.inc
	
	sed -n "2,20p" 易經HTML暫存1資料夾/yijing第$i卦古原文網頁內容段.inc > 易經HTML暫存2資料夾/yijing第$i卦古原文網頁內容段第2到第20列.inc	#怕古原文內容太多先抓幾列就好
	echo "<a href=\"../../易經古原文暫存戰果資料夾/yijing切開第$i卦古原文無分斷點.txt\" target=\"_new\">........我要看整段古文</a></br>" >> 易經HTML暫存2資料夾/yijing第$i卦古原文網頁內容段第2到第20列.inc	#看不夠要看全段也可以
	echo '/皇上的大標題/c\' > 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo "易經解掛中西醫病名對照大辭典" >>  易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo '/皇上的副標題/c\' >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo "易經卦義分析" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	name="`cat 易經古原文暫存戰果資料夾/yijing第$i卦古原文分段切開卦名.txt`"
	echo '/皇上的選單連結1/c\' >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo "<a href=\"http://zh.wikipedia.org/zh-tw/$name\" target=\"_new\">我看維基" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	echo '/皇上的選單連結2/c\' >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo "<a href=\"http://www.google.com/search?q=%$name卦\" target=\"_new\">我看谷歌" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	echo '/皇上的選單連結3/c\' >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	w3m "http://www.google.com/search?q=%$name卦百度" > 百度派來的a.txt	#用谷歌吊出百度的技巧
	sed -n "s/\(.*\)\( \)\(.*\.baidu..*\)/\3/1p" 百度派來的a.txt > 百度派來的b.txt
	sed -n "1p" 百度派來的b.txt > 百度派來的c.txt
	sed -n "s/\(.*com\)\( . \)\(item\)\( . \)\(..*\)/\1\/\3\/\5/p" 百度派來的c.txt > 百度派來的d.txt	
	echo  "<a href=\"`cat 百度派來的d.txt`\" target=\"_new\">我看百度" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	echo '/皇上的選單連結4/c\' >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo "<a href=\"http://www.nricm.edu.tw\" target=\"_new\">國家中醫藥研究所" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	echo '/皇上的選單連結5/c\' >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo "<a href=\"http://www.ncbi.nlm.nih.gov/pubmed/?term=$course\" target=\"_new\">PubMed" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	echo '/皇上的選單連結6/c\' >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo "<a href=\"http://www.sciencemag.org\" target=\"_new\">Science期刊" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	echo '/皇上的選單連結7/c\' >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo "<a href=\"http://www.google.com/search?q=%中西醫病名對照大辭典\" target=\"_new\">中西醫病名對照大辭典" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	echo '/皇上的選單連結8/c\' >> 	易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo "<a href=\"http://www.google.com/search?q=%易經\" target=\"_new\">易經消息" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	echo '/皇上的內容標題1/c\' >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo "`cat 易經古原文暫存戰果資料夾/yijing第$i卦古原文分段切開卦名.txt`" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	echo '/文段1/c\' >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	sed -f 專有名詞我要獨立列sed.sed 易經HTML暫存2資料夾/yijing第$i卦古原文網頁內容段第2到第20列.inc > 易經HTML暫存3資料夾/yijing第$i卦古原文網頁內容段第2到第20列專有名詞獨立列.inc	#以下將為易經古原文製作專有名詞及易經標題的感染
	sed -f 易經標題我要獨立列sed.sed 易經HTML暫存3資料夾/yijing第$i卦古原文網頁內容段第2到第20列專有名詞獨立列.inc > 易經HTML暫存3資料夾/yijing第$i卦古原文網頁內容段第2到第20列專有名詞易經標題獨立列.inc
	sed -f 感染專有名詞sed.sed 易經HTML暫存3資料夾/yijing第$i卦古原文網頁內容段第2到第20列專有名詞易經標題獨立列.inc > 易經HTML暫存3資料夾/yijing第$i卦古原文網頁內容段第2到第20列專有名詞感染.inc
	sed -f 感染易經標題sed.sed 易經HTML暫存3資料夾/yijing第$i卦古原文網頁內容段第2到第20列專有名詞感染.inc > 易經HTML暫存3資料夾/yijing第$i卦古原文網頁內容段第2到第20列感染專有名詞易經標題.inc
	sed -n 's/$/\\/p' 易經HTML暫存3資料夾/yijing第$i卦古原文網頁內容段第2到第20列感染專有名詞易經標題.inc >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed
	echo "以上是古文易經第$i卦$name恭祝講總統萬歲萬萬歲" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	echo '/文段2/c\' >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed	#暫不設計段列分句及感染	
	sed -n 's/$/\\/p' 易經維基網資料暫存戰果資料夾/yijing第$i卦維基網資料網頁.inc >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed 
	echo "</br>易經第$i卦$name恭祝講總統lucky you中頭彩" >> 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed

	done	


##<05>開始展開HTML網頁,來自<04>,上文段1為古原文<02>,下文段2為下載易經64卦卦義維基資料,<03>
#目前有個一書籍樣板,編號01,八個外包網頁樣板,編號02-09
	echo "奴才將為皇上展開易經解析HTML樣板網頁! 奴才斗膽敢問皇上想從第幾個樣板開始?"
	echo -e "\007"
#gedit HTML參考樣板資料夾現在要用/HTML參考樣板.txt
	cp HTML參考樣板資料夾現在要用/HTML參考樣板.txt HTML參考樣板資料夾現在要用/HTML參考樣板1.txt
	sed -n "s/\(..*\)\(---\)\(.*\)/\1/p" HTML參考樣板資料夾現在要用/HTML參考樣板1.txt > HTML參考樣板資料夾現在要用/HTML參考樣板2.txt
	mv HTML參考樣板資料夾現在要用/HTML參考樣板2.txt HTML參考樣板資料夾現在要用/HTML參考樣板.txt	
#read begin_line_template_topic
begin_line_template_topic=3	
	echo "$begin_line_template_topic" > begin_line_template_topic.txt
	echo "奴才再斗膽敢問皇上想至第幾列結束?"
#read end_line_template_topic
end_line_template_topic=3
	echo "$end_line_template_topic" > end_line_template_topic.txt
	echo "奴才將為皇上挑選第$begin_line_template_topic列到第$end_line_template_topic列的展開易經解析HTML樣板網頁!"
	sed -n "`cat begin_line_template_topic.txt`,`cat end_line_template_topic.txt`p" HTML參考樣板資料夾現在要用/HTML參考樣板.txt > 易經參考樣板測試第$begin_line_template_topic列到第$end_line_template_topic列.txt
	mv HTML參考樣板資料夾現在要用/HTML參考樣板1.txt HTML參考樣板資料夾現在要用/HTML參考樣板.txt

	declare -g g=`expr $begin_line_yijing_topic - 1`	#外層迴圈開始,HTML網頁樣板迴圈,變數改用g
	for course in `cat 易經參考樣板測試第$begin_line_template_topic列到第$end_line_template_topic列.txt`
	do
	g=g+1
	declare -i i=`expr $begin_line_yijing_topic - 1`	#內層迴圈開始,帶入古原文及維基網頁sed.sed至HTML網頁樣板迴圈,變數才用i
	for incourse in `cat yijing順序測試第$begin_line_yijing_topic列到第$end_line_yijing_topic列.txt`
	do
	i=i+1
	sed -f 易經HTML暫存戰果資料夾/yijing第$i卦古原文及維基網頁sed.sed HTML參考樣板資料夾現在要用/$course資料夾/$course.html > HTML參考樣板資料夾現在要用/$course資料夾/fuck$g$i.html
	echo -e '\a'
#####開檔4號	
#firefox HTML參考樣板資料夾現在要用/$course資料夾/fuck$g$i.html
	cp -a HTML參考樣板資料夾現在要用/$course資料夾 易經總戰果2資料夾	#怕放完就不見了,所以另存一個資料夾
	rm -rf HTML參考樣板資料夾現在要用
	cp -a HTML參考樣板資料夾 HTML參考樣板資料夾現在要用	#復歸原始

	done	#內層迴圈結束
	done	#外層迴圈結束
	echo "展開完畢,謝皇上!"


##<06>再修書	
#####開檔5號	
#libreoffice --writer 易經總戰果資料夾/我的著作文獻部份.txt


##<07>以下為風水個案分析	
	echo "奴才將為皇上分析風水個案資料! 奴才斗膽敢問皇上想從風水個案標題第幾列開始?"
	echo -e '\a'
#gedit 易經輸入端資料夾現在要用/易經個案列表.txt 
#read begin_line_case_topic
begin_line_case_topic=1
	echo "$begin_line_case_topic" > begin_line_case_topic.txt
	echo "奴才再斗膽敢問皇上想至風水個案第幾列第幾列結束?"
#read end_line_case_topic
end_line_case_topic=1
	echo "$end_line_case_topic" > end_line_case_topic.txt
	echo "奴才將為皇上挑選第$begin_line_case_topic列到第$end_line_case_topic列的風水個案資料分析!"
	sed -n "`cat begin_line_case_topic.txt`,`cat end_line_case_topic.txt`p" 易經輸入端資料夾現在要用/易經個案列表.txt > 風水個案測試第$begin_line_case_topic列到第$end_line_case_topic列.txt

	declare -i i=0
	for course in `cat 風水個案測試第$begin_line_case_topic列到第$end_line_case_topic列.txt`	
	do
	i=i+1	
	
	echo '/皇上的大標題/c\' > 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	echo "皇上風水解析" >>  易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	echo '/皇上的副標題/c\' >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	echo "風水個案分析" >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed

	echo '/皇上的選單連結1/c\' >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	echo "<a href=\"http://www.google.com/search?q=%中西醫病名對照大辭典\" target=\"_new\">中西醫病名對照大辭典" >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed	

	echo '/皇上的選單連結2/c\' >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	echo "<a href=\"http://www.me.ncku.edu.tw/tw/\" target=\"_new\">成大機械系" >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	
	echo '/皇上的選單連結3/c\' >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	echo "<a href=\"http://w3.sname.ncku.edu.tw/main.php?site_id=0\" target=\"_new\">成大系統系" >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed

	echo '/皇上的選單連結4/c\' >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	echo "<a href=\"http://mt.web.ym.edu.tw/front/bin/home.phtml\" target=\"_new\">陽明醫技系" >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed	

	echo '/皇上的選單連結5/c\' >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	echo "<a href=\"http://www.cnu.edu.tw/\" target=\"_new\">嘉南藥理大學" >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed

	echo '/皇上的選單連結6/c\' >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	echo "<a href=\"http://dse.nhcue.edu.tw/\" target=\"_new\">竹教大特教系" >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed

	echo '/皇上的內容標題1/c\' >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	echo "$course風水個案分析" >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed

	echo '/文段1/c\' >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
#gedit 易經輸入端資料夾現在要用/$course.txt	#先用編輯器打開檢視手動修改一下再存檔,排網頁用
	sed -n 's/$/\<\/br\>/p' 易經輸入端資料夾/$course.txt > 易經HTML暫存4資料夾/$course加段列標籤.inc 
	sed -f 專有名詞我要獨立列sed.sed 易經HTML暫存4資料夾/$course加段列標籤.inc > 易經HTML暫存4資料夾/$course專有名詞我要獨立列.inc	#以下將為風水個案製作專有名詞及易經標題的感染
	sed -f 易經標題我要獨立列sed.sed 易經HTML暫存4資料夾/$course專有名詞我要獨立列.inc > 易經HTML暫存4資料夾/$course專有名詞易經標題獨立列.inc
	sed -f 感染專有名詞sed.sed 易經HTML暫存4資料夾/$course專有名詞易經標題獨立列.inc > 易經HTML暫存4資料夾/$course感染專有名詞.inc
	sed -f 感染易經標題sed.sed 易經HTML暫存4資料夾/$course感染專有名詞.inc > 易經HTML暫存5資料夾/$course感染專有名詞易經標題.inc
	sed -n 's/$/\\/p' 易經HTML暫存5資料夾/$course感染專有名詞易經標題.inc >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed
	echo "$course恭祝講總統萬歲萬萬歲" >> 易經HTML暫存戰果資料夾/風水個案$course資料分析sed.sed	
	done
#感染的字在HTML表現左右都會空一格how to solve?


##<08>開始展開HTML網頁,文段1為風水個案分析
	echo "奴才將為皇上展開風水個案分析HTML樣板網頁! 奴才斗膽敢問皇上想從第幾個樣板開始?"
	echo -e "\007"
#gedit HTML參考樣板資料夾現在要用/HTML參考樣板.txt	#外包的樣板可挑選
	cp HTML參考樣板資料夾現在要用/HTML參考樣板.txt HTML參考樣板資料夾現在要用/HTML參考樣板1.txt
	sed -n "s/\(..*\)\(---\)\(.*\)/\1/p" HTML參考樣板資料夾現在要用/HTML參考樣板1.txt > HTML參考樣板資料夾現在要用/HTML參考樣板2.txt
	mv HTML參考樣板資料夾現在要用/HTML參考樣板2.txt HTML參考樣板資料夾現在要用/HTML參考樣板.txt		
#read begin_line_template_topic
begin_line_template_topic=2	
	echo "$begin_line_template_topic" > begin_line_template_topic.txt
	echo "奴才再斗膽敢問皇上想至第幾列結束?"
#read end_line_template_topic
end_line_template_topic=2
	echo "$end_line_template_topic" > end_line_template_topic.txt
	echo "奴才將為皇上挑選第$begin_line_template_topic列到第$end_line_template_topic列的展開風水個案分析HTML樣板網頁!"
	sed -n "`cat begin_line_template_topic.txt`,`cat end_line_template_topic.txt`p" HTML參考樣板資料夾現在要用/HTML參考樣板.txt > 風水參考樣板測試第$begin_line_template_topic列到第$end_line_template_topic列.txt
	mv HTML參考樣板資料夾現在要用/HTML參考樣板1.txt HTML參考樣板資料夾現在要用/HTML參考樣板.txt

	declare -g g=0	#外層迴圈開始,HTML網頁樣板迴圈,變數改用g
	for course in `cat 風水參考樣板測試第$begin_line_template_topic列到第$end_line_template_topic列.txt`
	do
	g=g+1
	declare -i i=0	#內層迴圈開始,帶入風水個案$course資料分析sed.sed至HTML網頁樣板迴圈,變數才用i
	for incourse in `cat 風水個案測試第$begin_line_case_topic列到第$end_line_case_topic列.txt`
	do
	i=i+1
	sed -f 易經HTML暫存戰果資料夾/風水個案$incourse資料分析sed.sed HTML參考樣板資料夾現在要用/$course資料夾/$course.html > HTML參考樣板資料夾現在要用/$course資料夾/fuck$g$i.html
	echo -e '\a'
#####開檔6號	
#firefox HTML參考樣板資料夾現在要用/$course資料夾/fuck$g$i.html
	cp -a HTML參考樣板資料夾現在要用/$course資料夾 易經總戰果2資料夾	#怕放完就不見了,所以另存一個資料夾
	rm -rf HTML參考樣板資料夾現在要用
	cp -a HTML參考樣板資料夾 HTML參考樣板資料夾現在要用	#復歸原始

	done	#內層迴圈結束
	done	#外層迴圈結束
	echo "展開完畢,謝皇上!"
################################################################################################################################################
###以下為程式結尾段,整理本程式所產生的資料夾######################################################################################################
################################################################################################################################################
	declare i i=0	#將易經維基網資料暫存戰果資料夾存入易經戰果資料夾
	for folder in 戰果  
	do 
	if [ -d "易經維基網資料暫存$folder資料夾" ]
		then 
		mv 易經維基網資料暫存$folder資料夾 易經戰果資料夾
	fi
	done

	declare i i=0	#將易經維基網資料暫存非戰果資料夾存入易經中間成品資料夾
	for folder in 1 2 3 4 5 6 7 8 9 10 11 12 
	do 
	if [ -d "易經維基網資料暫存$folder資料夾" ]
		then 
		mv 易經維基網資料暫存$folder資料夾 易經中間成品資料夾
	fi
	done

	declare i i=0	#將易經古原文暫存戰果資料夾存入易經戰果資料夾
	for folder in 戰果  
	do 
	if [ -d "易經古原文暫存$folder資料夾" ]
		then 
		mv 易經古原文暫存$folder資料夾 易經戰果資料夾
	fi
	done

	declare i i=0	#將易經古原文暫存非戰果資料夾存入易經中間成品資料夾
	for folder in 1 2 3 4 5   
	do 
	if [ -d "易經古原文暫存$folder資料夾" ]
		then 
		mv 易經古原文暫存$folder資料夾 易經中間成品資料夾
	fi
	done

	declare i i=0	#將易經HTML暫存戰果資料夾存入易經戰果資料夾
	for folder in 戰果  
	do 
	if [ -d "易經HTML暫存$folder資料夾" ]
		then 
		mv 易經HTML暫存$folder資料夾 易經戰果資料夾
	fi
	done

	declare i i=0	#將易經HTML暫存非戰果資料夾存入易經中間成品資料夾
	for folder in 1 2 3 4 5    
	do 
	if [ -d "易經HTML暫存$folder資料夾" ]
		then 
		mv 易經HTML暫存$folder資料夾 易經中間成品資料夾
	fi
	done

	declare i i=0	#將易經投影片暫存戰果資料夾存入易經戰果資料夾
	for folder in 戰果  
	do 
	if [ -d "易經投影片暫存$folder資料夾" ]
		then 
		mv 易經投影片暫存$folder資料夾 易經戰果資料夾
	fi
	done	

	declare i i=0	#將易經投影片暫存非戰果資料夾存入易經中間成品資料夾
	for folder in 1 2 3 4 5 6 7 8 9 10 11 12    
	do 
	if [ -d "易經投影片暫存$folder資料夾" ]
		then 
		mv 易經投影片暫存$folder資料夾 易經中間成品資料夾
	fi
	done

	
#原在a裡操作的檔案統一移入標記資料夾收藏,因為若一開始就在資料夾中程式會叫不到
	mv -f 工具程式資料夾現在要用 易經標記資料夾
	mv -f 基本資料資料夾現在要用 易經標記資料夾
	mv -f 投影片參考樣板資料夾現在要用 易經標記資料夾	#從1_輸入端_雲端原始文件資料夾複製來的HTML參考樣板資料夾程式執行後移入標記資料夾收藏
	mv -f HTML參考樣板資料夾現在要用 易經標記資料夾
	mv -f 易經輸入端資料夾現在要用 易經標記資料夾
	mv -f 易經總戰果[1-2]資料夾 易經總戰果資料夾

	mv *_line_*.txt *測試*.txt 易經標記資料夾	#顧客從終端機輸入的資料移入標記資料夾收藏
	mv 垃圾sed.sed 易經標記資料夾
	mv 垃圾再一次sed.sed 易經標記資料夾
	mv 感染專有名詞sed.sed  易經標記資料夾
	mv 感染易經標題sed.sed  易經標記資料夾
	mv 含有*的片段的檔名.txt 易經標記資料夾
	mv 專有名詞我要獨立列sed.sed 易經標記資料夾
	mv 易經標題我要獨立列sed.sed 易經標記資料夾
	mv 百度派來的*.txt 易經標記資料夾
	mv 00*.txt 易經標記資料夾
	mv 易經卦名*sed.sed  易經標記資料夾	 
	mv *有換列符.txt 易經標記資料夾
	mv 媽寫的內容*.txt 易經標記資料夾
	mv 我相片* 易經標記資料夾
	
	rm -rf 易經中間成品資料夾
	rm -rf 易經標記資料夾
	
	echo -e '\a'  
	echo -e '\a'
#以下是程式研發人員溝通討論區
