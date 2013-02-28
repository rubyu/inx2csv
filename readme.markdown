## E-DIC英和和英第2版のinxファイルをcsvに変換するサンプル


### すべてのデータを出力する場合

    usage: inx2csv.exe path_to_inx path_to_csv

この場合、出力は


    "02900000010","000","ABANDON TO , abandon somebody/something to somebody/something | ","「～を（あきらめて，(略)"
    "02900000010","001"," The crew was forced to abandon their ship to the waves.  | 乗組員たちはついに船を捨て，船が(略)",""


のようになります。
カラムはそれぞれmain_id, sub_id, heading, bodyになり、sub_idが000以外の場合、bodyが空になります。
データは何も加工されず、そのまま出力されます。


### Ankiに適した出力

    usage: inx2csv.exe --mode anki path_to_inx path_to_csv

この場合、出力は


    "ABANDON TO , abandon somebody/something to somebody/something","「～を（あきらめて(略)"
    "ABANDON TO , abandon oneself to something","「（強い感情など）に身をゆだねる，(略)"


のようになります。
データをそのまま出力はせず、作者のニーズに合わせて以下のような処理を行なっています。
ソースを同梱していますので適時改変してください。

- headingの最後の " | "を取り除いている。
- 例文は出力しない。（sub_idが000のものだけ出力）
- ▲▲～△△で囲まれている部分からIDを取り除いている。
- CRタグをBRタグに置換している。
- 検索の利便性のための、リンクだけからなるアイテムについては取り除いている。


### 注意事項

- すべての辞書で動作確認はしていません。


https://github.com/rubyu/inx2csv/blob/master/inx2csv.zip?raw=true