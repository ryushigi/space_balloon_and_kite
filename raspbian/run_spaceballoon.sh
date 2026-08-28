#!/bin/bash -f
# python space_balloon.py            \
#        --mode 0                    \
#        --icm20948                  \
#        --icm20948_addr 0x68        \
#        --icm20948_i2cbus 1         \
#        --gt502ggn                  \
#        --gt502ggn_interval 5       \
#        --powermonitor              \
#        --framerate 30              \
#        --framebuffer 50            \
#        --width 1980                \
#        --height 1080               \
#        --csvbuffer 614400          \
#        --csv_output_dir   ./output \
#        --movie_output_dir ./output

python space_balloon.py            \
       --mode 5                    \
       --icm20948                  \
       --icm20948_addr 0x68        \
       --icm20948_i2cbus 1         \
       --bme280                    \
       --bme280_i2cbus 5           \
       --bme280_interval 5         \
       --bme280_addr 0x76          \
       --gt502ggn                  \
       --gt502ggn_interval 5       \
       --direwolf_interval 10      \
       --powermonitor              \
       --framerate 30              \
       --framebuffer 50            \
       --width 1980                \
       --height 1080               \
       --csvbuffer 614400          \
       --csv_output_dir   ./output \
       --movie_output_dir ./output


# python space_balloon.py            \
#        --mode 0                    \
#        --icm20948                  \
#        --icm20948_addr 0x68        \
#        --icm20948_i2cbus 1         \
#        --powermonitor              \
#        --framerate 30              \
#        --framebuffer 50            \
#        --width 1980                \
#        --height 1080               \
#        --csvbuffer 614400          \
#        --csv_output_dir   ./output \
#        --movie_output_dir ./output
