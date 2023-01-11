import random
import math
###### define constants ######

### DDR4_4Gb_8B_x16_JD.ini
#NUM_BANK=8
# SALP increase bank #
N_SA = 1
NUM_BANK = 8*N_SA
#NUM_ROW=32768
# SALP row #
NUM_ROW = 32768/N_SA
NUM_COL=1024
DEVICE_WIDTH=16
### END DDR4_4Gb_8b_x16_JD

### other standard params ###
TOTAL_MEGS_OF_MEM = 32768 # MB
NUM_CHAN = 4 # default 1 channl
TRANS_SIZE = 64 # bytes
BUS_WIDTH = 64 # bits
STORAGE_PER_DEVICE = (NUM_ROW * (NUM_COL * DEVICE_WIDTH) * NUM_BANK) / 8 * (2**(-20)) # MB
MEGS_OF_STORAGE_PER_RANK = (STORAGE_PER_DEVICE * (BUS_WIDTH/DEVICE_WIDTH))  
TOTAL_NUM_RANK = (int)(TOTAL_MEGS_OF_MEM / MEGS_OF_STORAGE_PER_RANK) 
RANK_PER_CHAN = TOTAL_NUM_RANK/NUM_CHAN

# get # of ranks/chan
# maximum 2 ranks/chan
#if(TOTAL_NUM_RANK/2>1.0):
#    NUM_CHAN = TOTAL_NUM_RANK/2
#else:
#    NUM_CHAN = 1
#RANK_PER_CHAN = TOTAL_NUM_RANK/NUM_CHAN   


print("storage per device/chip (MB): "+str(STORAGE_PER_DEVICE))
print("Megs per Rank: "+str(MEGS_OF_STORAGE_PER_RANK))
print("# of ranks: "+str(TOTAL_NUM_RANK))
print("ranks per channel: "+str(RANK_PER_CHAN))
NUM_SA = 8
### END OTHER STANDARD PARAMS ###

### file io stuff ###

fo = open("mase_apr.trc", "w")

def gen_addr(num_chan, num_bank, num_rank, num_col, num_row, num_addr, num_sa):
    
    ### build chan list
    chan_lst = []
    chan_bits_len = (int)(math.log2(num_chan))
    if chan_bits_len > 0:
        for c in range((int)(num_chan)):
            chan_fmt_str = '0' + str(chan_bits_len) + 'b'
            b = format(c, chan_fmt_str)
            chan_lst.append(b)
    print("chan_list: "+str(chan_lst))  
    print("chan_bits: "+str(chan_bits_len))
    
    ### build bank lst
    bank_lst = []
    bank_bits_len = (int)(math.log2(num_bank))
    for c in range(num_bank):
        bank_fmt_str = '0' + str(bank_bits_len) + 'b'
        b = format(c, bank_fmt_str)
        bank_lst.append(b)
    print("bank_list: "+str(bank_lst))
    print("bank_bits: "+str(bank_bits_len))
    
    ### build rank lst
    rank_lst = []
    rank_bits_len = (int)(math.log2((int)(num_rank)))
    if rank_bits_len>0: 
        for c in range((int)(num_rank)):
            rank_fmt_str = '0' + str(rank_bits_len) + 'b'
            b = format(c, rank_fmt_str)
            rank_lst.append(b)
    print("rank_list: "+str(rank_lst))
    print("rank_bits: "+str(rank_bits_len))
    
    ### build col lst
    col_lst = []
    col_offset = (int)(math.log2(TRANS_SIZE)-math.log2(BUS_WIDTH/8))
    col_bits_len = (int)(math.log2(num_col)) - col_offset
    for c in range(2**col_bits_len):
        col_fmt_str = '0' + str(col_bits_len) + 'b'
        b = format(c, col_fmt_str)
        col_lst.append(b)    
    #print(col_lst)
    print("clo_bits: "+str(col_bits_len))
    
    ### build row lst
    rows_per_sa = num_row / num_sa # num of rows per subarray
    row_lst = []
    row_addr = 0
    row_bits_len = (int)(math.log2(num_row))
    for i in range(num_sa):
        row_fmt_str = '0' + str(row_bits_len) + 'b'
        b = format((int)(row_addr), row_fmt_str)
        row_lst.append(b)
        row_addr += rows_per_sa
    #print(row_lst)    
    print("row_bits: "+str(row_bits_len))
    
    ##### generate num_addr memory request

    # # DRAM-CAM baseline
    # for i in range(num_addr):
    #     for k in range(0,8): # each query visit a bank 8 times
    #         row = str(random.choice(row_lst))
    #         col = str(random.choice(col_lst))
    #         chan = "00"
    #         rank = "00"
    #         for j in range(0,4):
    #             bank = bank_lst[j]
    #             addr_tmp = row+col+rank+bank+chan
    #             # append zeros
    #             for m in range((int)(math.log2(TRANS_SIZE))):
    #                 addr_tmp += "0"
    #             fo.write(hex(int(addr_tmp,2))+" READ "+"0"+"\n")

    # # DRAM-CAM PD
    for i in range(num_addr):
    # # we use scheme 7 for maximum parallelism -> row:col:rank:bank:chan
        total = 121 # utilize total 121 banks
        counter = 0
        for c in range(0, len(chan_lst)):
            for r in range(0, len(rank_lst)):
                for b in range(0, len(bank_lst)):
                    if counter < total:
                        row = str(random.choice(row_lst))
                        col = str(random.choice(col_lst))
                        bank = bank_lst[b]
                        rank = rank_lst[r]
                        chan = chan_lst[c]
                        addr_tmp = row+col+rank+bank+chan
                        # append zeros
                        for m in range((int)(math.log2(TRANS_SIZE))):
                            addr_tmp += "0"
                        fo.write(hex(int(addr_tmp,2))+" READ "+"0"+"\n")
                        counter += 1
                    else:
                        continue

        # row = str(random.choice(row_lst))
        # col = str(random.choice(col_lst))

    #     for j in range(0, len(bank_lst)):
    #         bank = str(bank_lst[j])
    #         for k in range(0, len(rank_lst)):
    #             rank = str(rank_lst[k])
    #             for l in range(0, len(chan_lst)):
    #                 chan = str(chan_lst[l])
    #                 addr_tmp = row+col+rank+bank+chan

    #                 # append zeros
    #                 for m in range((int)(math.log2(TRANS_SIZE))):
    #                     addr_tmp += "0"
    #                 fo.write(hex(int(addr_tmp,2))+" READ "+"0"+"\n")

    # DRAM-CAM PR

    # bank_lst = ["000", "001", "010", "011"]
    # for i in range(num_addr*8):
    # ## we use scheme 7 for maximum parallelism -> row:col:rank:bank:chan
    #     row = str(random.choice(row_lst))
    #     col = str(random.choice(col_lst))
    #     rank = "00"
    #     chan = "00"
    #     for j in range(0, len(bank_lst)):
    #         bank = str(random.choice(bank_lst))
    #         addr_tmp = row+col+rank+bank+chan

    #         for m in range((int)(math.log2(TRANS_SIZE))):
    #             addr_tmp += "0"

    #         fo.write(hex(int(addr_tmp,2))+" READ "+"0"+"\n")

    #     for j in range(0, len(bank_lst)):
    #         bank = str(bank_lst[j])
    #         for k in range(0, len(rank_lst)):
    #             rank = str(rank_lst[k])
    #             for l in range(0, len(chan_lst)):
    #                 chan = str(chan_lst[l])
    #                 addr_tmp = row+col+rank+bank+chan

    #                 # append zeros
    #                 for m in range((int)(math.log2(TRANS_SIZE))):
    #                     addr_tmp += "0"
    #                 fo.write(hex(int(addr_tmp,2))+" READ "+"0"+"\n")

num_queries = 1000 
gen_addr(NUM_CHAN, NUM_BANK, RANK_PER_CHAN, NUM_COL, NUM_ROW, num_queries, 1)
