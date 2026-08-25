# SBB03基板技術資料

## 設計情報

### 通信I/F一覧
| ポート   | アドレス | デバイス/<br/>コネクター | 用途                              |
|-------|------|-----------------|---------------------------------|
| uart1 | -    | J6              | シリアルコンソール                |
| uart3 | -    | J4              | 無線機リモートコントロール(予備)   |
| uart5 | -    | J5              | 外部GNSSレシーバー               |
| i2c1  | 0x68 | J3              | ICM-20948(9軸センサー)          |
| i2c4  | (任意) | J2              | 外部I2Cセンサー(予備)          |
| i2c5  | 0x76 | U4              | BME280(気圧・温度・湿度センサー) |
| i2c5  | 0x18 | U5              | TLV320AIC3104(オーディオコーデック:無線機データ通信) |
| i2s   | -    | U5              | TLV320AIC3104                  |

### I/O機能割り当て
| SBB<br/>J1 | RasPi<br/>J8 | 機能選択     | 用途                  |
|------------|--------------|----------|---------------------|
| (28)       | (27)         | (SDA0)   | (未接続、RasPiのシステムで使用) |
| (27)       | (28)         | (SCL0)   | (未接続、RasPiのシステムで使用) |
| 4          | 3            | SDA1     | I2C: ICM-20948      |
| 6          | 5            | SCL1     | I2C: ICM-20948      |
| 8          | 7            | TXD3     | 無線機リモートコントロール(予備)   |
| 30         | 29           | RXD3     | 無線機リモートコントロール(予備)   |
| 32         | 31           | GPCLK2   | TLV320AIC3104動作クロック(予備)  |
| 25         | 26           | GPIO7	   | (未接続)             |
| 23         | 24           | SDA4     | 外部I2Cセンサー(予備)       |
| 22         | 21           | SCL4     | 外部I2Cセンサー(予備)       |
| 20         | 19           | SDA5     | I2C: BME280/TLV320AIC3104 |
| 24         | 23           | SCL5     | I2C: BME280/TLV320AIC3104 |
| 31         | 32           | TXD5     | UART: GNSSレシーバー     |
| 34         | 33           | RXD5     | UART: GNSSレシーバー     |
| 7          | 8            | TXD1     | シリアルコンソール           |
| 9          | 10           | RXD1     | シリアルコンソール           |
| 35         | 36           | GPIO16   | GNSS 1秒パルス(予備)      |
| 12         | 11           | GPIO17   | 無線機送信制御             |
| 11         | 12           | PCM_CLK  | I2S: TLV320AIC3104      |
| 36         | 35           | PCM_FS   | I2S: TLV320AIC3104      |
| 37         | 38           | PCM_DIN  | I2S: TLV320AIC3104      |
| 39         | 40           | PCM_DOUT | I2S: TLV320AIC3104      |
| 16         | 15           | GPIO22   | 無線機リモートコントロール       |
| 15         | 16           | GPIO23   | 無線機リモートコントロール       |
| 17         | 18           | GPIO24   | 無線機リモートコントロール       |
| 21         | 22           | GPIO25   | (未接続) |         
| 38         | 37           | GPIO26   | TLV320AIC3104リセット(予備) |
| 14         | 13           | GPIO27   | 無線機リモートコントロール       |

## 使用方法

### シリアルコンソール有効化
- cmdline.txt から "quiet" を削除
- config.txt に下記を追加
```config.txt
dtparam=uart0_console
enable_uart=1
```

### シリアルポートとi2Cを追加
- config.txt に下記を追加またはアンコメント
```config.txt
dtoverlay=uart3
dtoverlay=uart5
dtparam=i2c_arm=on
dtoverlay=i2c4,pins_8_9
dtoverlay=i2c5,pins_10_11
```

### GNSSレシーバーの有効化
- J5にGNSSレシーバーを接続
- uartにデータが流れていることを確認
```
cat /dev/ttyAMA5
```
#### gpsdインストール
```
sudo apt update
sudo apt install gpsd gpsd-clients -y
```
- /etc/default/gpsd 編集
```
# START_DAEMON を true にする（記述があれば）
START_DAEMON="true"

# USBの自動検出を無効化（UART固定にするため）
USBAUTO="false"

# 使用するデバイスに /dev/ttyAMA5 を指定
DEVICES="/dev/ttyAMA5"

# オプション（-n はクライアントの接続を待たずに即座にGPSデータを読み始める設定）
GPSD_OPTIONS="-n"
```
- 設定を反映させるために、gpsd サービスを再起動する。あわせて、ラズパイ起動時に自動でサービスが始まるように有効化しておく。
```
sudo systemctl daemon-reload
sudo systemctl restart gpsd
sudo systemctl enable gpsd
```
- 動作確認
```
cgps
```


### サウンドカードの設定
SBB03基板に搭載した TLV320AIC3104 をサウンドカードして認識させるため、デバイスツリーソースファイルを用意した。

- デバイスツリーソースファイルをコンパイル
```
dtc -@ -I dts -O dtb -o SBB03_tlv320aic3104.dtbo SBB03_tlv320aic3104.dts
```

- 生成した SBB03_tlv320aic3104.dtbo を /boot/overlays/ にコピー
```
sudo cp SBB03_tlv320aic3104.dtbo /boot/overlays/
```

- /boot/config.txt に下記を追記して再起動
```
dtoverlay=SBB03_tlv320aic3104
```

- サウンドカード名、カード番号の確認
```
cat /proc/asound/cards
```

- alsamixerの設定内容一覧  
(-cオプションの値はサウンドカード名かカード番号)
```
amixer -c tlv320aic3104so scontrols
```

- 音量設定
dierwolf使用前に、音量設定を適切にするため、下記のようにシェルスクリプト等で設定するようにする。
```
#!/bin/sh
#出力設定
amixer -c tlv320aic3104so sset 'PCM' 100%
amixer -c tlv320aic3104so sset 'HP DAC' 75%
amixer -c tlv320aic3104so sset 'HP' 0
#入力設定
amixer -c tlv320aic3104so sset 'Left Line1L Mux' 'single-ended'
amixer -c tlv320aic3104so sset 'Left PGA Mixer Line1L' on
amixer -c tlv320aic3104so sset 'PGA' 60%
```


### DireWolf インストール
https://www.github.com/wb2osz/direwolf
direwolf/doc/Raspberry-Pi-APRS.pdf に基づいてインストール

```
sudo apt-get install cmake
sudo apt-get install libasound2-dev
sudo apt-get install libudev-dev
sudo apt-get install pkg-config
sudo apt-get install libavahi-client-dev
sudo apt-get install gpiod libgpiod-dev
```

```
cd ~
git clone https://www.github.com/wb2osz/direwolf
cd direwolf
```

```
mkdir build && cd build
cmake -DUNITTEST=1 ..
make -j
make test
sudo make install
```

```
make install-conf
```

下記のコマンドで tlv320aic3104-soundcard のカード番号を確認する。
```
aplay –l 
arecord -l
```

#### direwolf.conf 編集
```
ADEVICE  plughw:3,0　#カード番号が3の場合
ARATE 48000         #SBB03はサンプリングレート48kHzに最適化しているので

#CHANNEL 0設定(無線機は1台なので0番のみ)
CHANNEL 0
MYCALL JXXXXX-11    #<コールサイン>-<ssid> 11:気球、航空局、宇宙船など
MODEM 1200          #1200bpsで運用する(無線機のマイクスピーカー端子では9600bpsは不可能)
PTT GPIOD  gpiochip0  17    #PTT制御はGPIO17使用
```

direwolf.conf の設定で一定間隔でAPRSビーコンを送信することもできるが、
今回は、pythonプログラムでAPRSパケットを生成し、KISSプロトコルでdirewolfを操作して送信する方法をとるため、direwolf.confでのビーコン設定はしない。


### APRSビーコンの送出

#### APRSビーコン送出プログラム
space_balloon_and_kite/python/aprs ディレクトリーに、aprs_beacon.py を用意した。
このプログラムは、無線機(IC-T10)のリモコン機能を使用して、144.660MHzと431.040MHzの2つの周波数で交互にAPRSビーコンを送出する。

このプログラムを使用して正常に送信するためには、下記の要件を満たす必要がある。
- IC-T10の設定は、下記「IC-T10設定」に従うこと
- SBB03基板のJ4コネクターとIC-T10のマイクジャック/スピーカージャックを専用ケーブルで接続しておくこと
- あらかじめdirewolfを起動しておくこと
- サウンドカード設定スクリプト SBB03_sset.sh を実行してくおくこと(RasPi起動後毎回必要)

#### IC-T10設定
- ケーブルの抜き差しをする際は電源を切っておくこと
- 使用時は電源をオンし、スピーカーボリュームを12時の向き(中間)に回しておくこと
- 「mic S」設定を「SimPLE」にしておくこと
- メモリーチャンネル M-CH0に144.660MHzを、M-CH1に431.040MHzを、それぞれ設定しておくこと
- メモリーチャンネルには周波数の他、モードと送信出力も記憶されるので、モードはFM、送信出力は最大(5W)にしておく
- MICゲイン を1(最低)に設定しておくこと
- タイムアウトタイマーは最も短い 1分 に設定しておくことが望ましい
- ロック機能を設定しておくことが望ましい(ロック中もリモコン機能は有効)
- PTTロックは **設定しない** こと

#### 自動起動
下記のような crontab で、起動時に自動起動することができる。
```
@reboot screen -dmS direwolf /usr/local/bin/direwolf -c /home/pi/direwolf.conf
@reboot /home/pi/SBB03/python/SBB03_sset.sh > /home/pi/SBB03/python/SBB03_sset.log 2>&1
@reboot screen -dmS SBB03_py /home/pi/SBB03/python/sb-env/bin/python /home/pi/SBB03/python/aprs_beacon.py
```

ここで、ユーザー名 「pi」は、必要に応じて使用しているユーザー名に変更する。
また、python仮想環境、スクリプト配置ディレクトリーも適宜変更する。

