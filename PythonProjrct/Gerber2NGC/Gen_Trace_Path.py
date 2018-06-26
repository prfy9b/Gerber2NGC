from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")


from sympy import *


def gen_trace_path(filename, gerberList, offset, h, stop_lift):
    fs_int_num, fs_dec_num, unit_scale = 0, 0, 1
    for i, line in enumerate(gerberList):
        if gerberList[i].find('%FSLA') != -1:
            fs_int_num = int(gerberList[i][gerberList[i].find('X') + 1])
            fs_dec_num = int(gerberList[i][gerberList[i].find('X') + 2])

        if gerberList[i].find('%MOIN') != -1:
            unit_scale = 25.4

    # get all pre-defined apetures
    apeture_dict = {}
    for i, line in enumerate(gerberList):
        apeture_tuple = ()
        if gerberList[i].find('ADD') != -1:
            apeture_num = gerberList[i][gerberList[i].find('ADD') + 2:gerberList[i].find(',') - 1]
            apeture_type = gerberList[i][gerberList[i].find(',') - 1]

            if apeture_type == 'C':  # to be continue
                Cir_Dia = gerberList[i][gerberList[i].find(',') + 1:gerberList[i].find('*')]
                apeture_tuple = ('Circle', Cir_Dia, 0, 0)
                print(apeture_num, apeture_tuple)

            elif apeture_type == 'R':  # to be continue
                Rect_A = gerberList[i][gerberList[i].find(',') + 1:gerberList[i].find('X')]
                Rect_B = gerberList[i][gerberList[i].find('X') + 1:gerberList[i].find('*')]
                apeture_tuple = ('Rectangle', Rect_A, Rect_B, 0)
                print(apeture_num, apeture_tuple)

            elif apeture_type == 'O':  # to be continue
                print('obround')

            elif apeture_type == 'P':  # to be continue
                print('polygon')

            apeture_dict[apeture_num] = apeture_tuple

    draw_trace = []
    aptset_idx, regnset_idx = [], []
    aptset_cnt, regnset_cnt = 0, 0
    for i, line in enumerate(gerberList):
        if gerberList[i][0] == 'D': aptset_idx.append(i); aptset_cnt += 1;
        if gerberList[i].find('M02') != -1: aptset_idx.append(i); aptset_cnt += 1;
    print(aptset_idx, aptset_cnt)

    draw_trace.append('G0 Z' + h + '\n')

    for m in range(0, len(aptset_idx) - 1):  # 0,1,2,3,4,5,M02，for every peroid an apeture set~changed
        current_apt_set = gerberList[aptset_idx[m]][:-2]
        print(current_apt_set)

        if float(apeture_dict[current_apt_set][1]) > 0.002:

            for n in range(aptset_idx[m] + 1, aptset_idx[m + 1]):  # for every line inside one certain peroid an apeture set~changed
                current_Dcode = gerberList[n][-5:-2]  # get the Dcode (D01, 02, 03) for each line inside this period
                if gerberList[n].find('G01') != -1:  # examine from line n+1, loop till a line without "G01 "
                    if gerberList[n].find('D03') != -1:
                        print(current_Dcode, 'flash apeture')
                    elif gerberList[n].find('D01') != -1:  # if D01 found
                        draw_to_x = unit_scale * int(gerberList[n][gerberList[n].find('X') + 1:gerberList[n].find('Y')]) / 10**fs_dec_num + offset[0]
                        draw_to_x = round(draw_to_x, 3)
                        draw_to_y = unit_scale * int(gerberList[n][gerberList[n].find('Y') + 1:gerberList[n].find('D01*')]) / 10**fs_dec_num + offset[1]
                        draw_to_x = round(draw_to_x, 3)
                        draw_to_y = round(draw_to_y, 3)
                        draw_trace.append('G1 X' + str(draw_to_x) + ' Y' + str(draw_to_y) + ' F1200 ;Apeture ' + current_apt_set + ' drawing\n')
                    elif gerberList[n].find('D01') == -1 and gerberList[n].find('D02') == -1:  # if D01 not found, and D02 not found
                        draw_to_x = unit_scale * int(gerberList[n][gerberList[n].find('X') + 1:gerberList[n].find('Y')]) / 10**fs_dec_num + offset[0]
                        draw_to_x = round(draw_to_x, 3)
                        draw_to_x = round(draw_to_x, 3)
                        draw_to_y = unit_scale * int(gerberList[n][gerberList[n].find('Y') + 1:gerberList[n].find('*')]) / 10**fs_dec_num + offset[1]
                        draw_to_x = round(draw_to_x, 3)
                        draw_to_y = round(draw_to_y, 3)
                        draw_trace.append('G1 X' + str(draw_to_x) + ' Y' + str(draw_to_y) + ' F1200 ;Apeture ' + current_apt_set + ' drawing\n')
                    elif gerberList[n].find('D02') != -1 and gerberList[n].find('D01') == -1:  # if D01 not found, instead, D02 found
                        start_pnt_x = unit_scale * int(gerberList[n][gerberList[n].find('X') + 1:gerberList[n].find('Y')]) / 10**fs_dec_num + offset[0]
                        start_pnt_x = round(start_pnt_x, 3)
                        start_pnt_y = unit_scale * int(gerberList[n][gerberList[n].find('Y') + 1:gerberList[n].find('D02*')]) / 10**fs_dec_num + offset[1]
                        start_pnt_y = round(start_pnt_y, 3)
                        draw_trace.append('G91\n')
                        draw_trace.append('G0 Z' + stop_lift + '\n')
                        draw_trace.append('G90\n')
                        draw_trace.append('G1 X' + str(start_pnt_x) + ' Y' + str(start_pnt_y) + ' F2400 ;Apeture ' + current_apt_set + ' moveing\n')
                        draw_trace.append('G91\n')
                        draw_trace.append('G0 Z-' + stop_lift + '\n')
                        draw_trace.append('G90\n')
    return draw_trace