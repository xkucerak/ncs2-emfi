# 000

### Results

| No. of attempts | TOP-1 ACC | note                                                                                                                                                            |
| :-------------: | :-------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|       14        |    NaN    | NCS2 got stuck after the attack and needed a restart                                                                                                            |
|       17        |  78.125%  | baseline accuracy                                                                                                                                               |
|       69        | < 78.125% | misclassified image/s only during the attack, and in 12 cases (out of these 69), accuracy dropped below 10\%, meaning misclassification stayed after the attack |

## Settings

### Software

| param           | value     |
| :-------------- | :-------- |
| **Model**       | ResNet-50 |
| **Image count** | 256       |

### Location

| param | value    |
| :---: | -------- |
| **X** | 123.6 mm |
| **Y** | 154.4 mm |
| **Z** | 1.0 mm   |

### ChipSHOUTER

| param        | value  |
| :----------- | :----- |
| **Voltage**  | 410 V  |
| **Repeat**   | 18     |
| **width**    | 160 ns |
| **Deadtime** | 17 ms  |

### Probe

| param           | value |
| --------------- | ----- |
| **Core Width**  | 1 mm  |
| **Windig**      | CCW   |
| **Aprox. Rot**. | RIGHT |
