# Results

{{ '{{ results }}' }}

## Settings

### Software

| param           | value               |
| :-------------- | :------------------ |
| **Model**       | {{ cfg_model }}     |
| **Image count** | {{ cfg_img_count }} |
| **Delay**       | {{ cfg_delay }} s   |
| **Top-1**       | {{ cfg_top_1 }}     |
| **Top-5**       | {{ cfg_top_5 }}     |

### Location

| param | value          |
| :---: | -------------- |
| **X** | {{ pos_x }} mm |
| **Y** | {{ pos_y }} mm |
| **Z** | {{ pos_z }} mm |

### ChipSHOUTER

| param        | value                |
| :----------- | :------------------- |
| **Voltage**  | {{ cs_voltage }} V   |
| **Repeat**   | {{ cs_repeat }}      |
| **Width**    | {{ cs_width }} ns    |
| **Deadtime** | {{ cs_deadtime }} ms |

### Probe

| param            | value                |
| ---------------- | -------------------- |
| **Core Width**   | {{ probe_core }} mm  |
| **Winding**      | {{ probe_winding }}  |
| **Approx. Rot.** | {{ probe_rotation }} |
