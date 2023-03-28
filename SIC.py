# 系統程式SIC ver4
# + Mrecoder

from pickletools import TAKEN_FROM_ARGUMENT4
import string
file_prog = open('(test)SIC.txt')
txtContxt = file_prog.read()
file_opCode = open('opCode.txt')
k = file_opCode.read()
# 存record包含T、M
record =[]
symbolTab = {}
opCodeTable = {}
index_addressing = []
# 紀錄初始Address
address = "0x0"
# 報錯
error = 0
# 起始行數
startLine = -1

class progFront :
    # 存object code(三欄位資料，位置，object code)
    def __init__(self, data, addR, obJCode):
        self.data = data
        self.addR = addR
        self.obJCode = obJCode

class labelFront :
    # 存進symbol table(有無定義，位置，行數)
    def __init__(self,if_def, addR, line):
        self.if_def = if_def
        self.addR = addR
        self.line = line

class recordFront :
    # recorder(onepass要更正，位置，object code，是否為M)
    def __init__(self,one_pass_TRecord, addR, obJCode,MRecord):
        self.one_pass_TRecord = one_pass_TRecord
        self.addR = addR
        self.obJCode = obJCode
        self.MRecord = MRecord

# 建立opcode字典
def opCodeCon():
    op_line = k.split("\n")
    for i in range (len(op_line)) :
        op_line[i] = op_line[i].split(" ")
        opCodeTable[op_line[i][0]] = op_line[i][1]

# 查opCode
def search_op(op_data):
    # 找不到的時候報錯->Flase
    return opCodeTable.get(op_data,False) 

## 檢查是否為16進位
def if_hex(data):
    return all(x in string.hexdigits for x in data)

def show_data(data) :
    return data[0] + "\t" + data[1] + "\t" + data[2]

# 新增label
def insert_Label(key,val_tf,val_Address,val_line,mRecord) :
    result = symbolTab.get(key,False)
    # 第一次出現
    if result == False :
        # 定義到，直接加入
        if val_tf == True :
            arr2 = [val_line]
            symbolTab[key] = labelFront(val_tf,val_Address,val_line)
        # 沒有定義到但有用到
        else :
            arr = [val_Address]
            arr2 = [val_line]
            symbolTab[key] = labelFront(val_tf,arr,arr2)
    # 已經紀錄過的
    else :
        # 沒定義繼續被叫到
        if val_tf == False :
            symbolTab[key].addR.append(val_Address)
            symbolTab[key].line.append(val_line)
        # 之前有叫到現在被定義
        else :
            # record 
            for i in range(len(symbolTab[key].addR)) :
                try :
                    index_add = index_addressing.index(symbolTab[key].addR[i])
                except ValueError :
                    index_add = -1
                # print(index_addressing,symbolTab[key].addR[i])
                if index_add != -1 :
                    record.append(recordFront(True,symbolTab[key].addR[i],hex(int(val_Address,16)+ int("0x8000",16)),mRecord)) 
                else :  
                    record.append(recordFront(True,symbolTab[key].addR[i],val_Address,mRecord)) 
            arr2 = symbolTab[key].line
            arr2.append(val_line)
            symbolTab[key] = labelFront(val_tf,val_Address,arr2)

# 查詢label
def search_Label(label_data) :
    result = symbolTab.get(label_data,False)
    # 沒有加進去過
    if result == False :
        return False
    # 沒定義但有加進去
    elif result.if_def == False :
        return False
    else :
        return result.addR

# 切割整理好的一行資料
def slic_data(data,line):
    global startLine,address,error
    # 紀錄在第幾個位置讀到opcode
    recoder_j = -1
    data = data.split("'")
    # 表示含有' (BYTE)
    if (len(data)) != 1 :
        data[0] = data[0].strip(" ")
        tmpp = data[0].split(" ")
        tmpp[len(tmpp)-1] = tmpp[len(tmpp)-1] + "'" + data[1] + "'"
        data = tmpp
    else :
        data = data[0]
        data = data.split(" ")
    # 索引定址多的空格
    for i in range(len(data)):
        if '' in data :
            data.remove('')
    if len(data) <= 3 :
        # 開始判斷
        if_mnemonic = 0
        if_pseudocode = 0
        for j in range(len(data)) :
            if data[j] == "START" :
                if j == 1 :
                    if startLine != -1 :
                        print("Error! Line ",line+1," >>>>>>>>>>寫了兩個start")
                        error += 1
                        return False
                    # 紀錄行數
                    startLine = line
                    # 判斷起始位置是否為16進位
                    if len(data) == 3 :
                        if len(data[2]) <= 4 :
                            if if_hex(data[2]) == True :
                                address = "0x" + data[2]
                               
                                        # ===起始位址====
                                        # print("M record")
                            else :
                                print("Error! Line ",line+1," >>>>>>>>>>起始位置必須為16進位")
                                error += 1
                                return False
                        else :
                            print("Error! Line ",line+1," >>>>>>>>>>起始位置不能超過4bits")
                            error += 1
                            return False
                        insert_Label(data[0],True,address,i,False)
                        return data # 不再對位置做判斷了
                    else :
                        startLine = line
                        print("Error! Line ",line+1," >>>>>>>>>>START 格式有誤 :沒有輸入起始位置")
                        error += 1
                        return False
                else :
                    startLine = line
                    if j == 0 :
                        print("Error! Line ",line+1," >>>>>>>>>>START 格式有誤：少輸入程式名稱")
                    else :
                        print("Error! Line ",line+1," >>>>>>>>>>START 格式有誤：輸入兩個Label")
                    error += 1
                    return False 
            # 程式開始執行了
            elif startLine >= 0 :
                if search_op(data[j]) == False :
                    # BYTE WORD、 RESB RESW 
                    if data[j] == "BYTE" or data[j] == "WORD" or data[j] == "RESB" or data[j] == "RESW" :
                        if_pseudocode  += 1
                        recoder_j = j
                        if len(data) < 3 :
                            if j == 0 :
                                print("Error! Line ",line+1," >>>>>>>>>>定義變數有誤 : 沒有Label")
                                error += 1
                                return False
                            else:
                                print("Error! Line ",line+1," >>>>>>>>>>定義變數有誤 : 沒有給值")
                                error += 1
                                return False
                    elif data[j] == "END" :
                        # print("End of the program.")\
                        if len(data) == 2 :
                            # if data[0] != "END"  :
                            if data[0] == "END" :  
                                yy = search_Label(data[1]) 
                                if yy != False:
                                    return True
                                else :
                                    print("Error! Line ",line+1," >>>>>>>>>>Label沒有定義到 : ",data[1])
                                    error += 1
                                    return False
                            else :
                                print("Error! Line ",line+1," >>>>>>>>>>END指令格式錯誤")
                                error += 1
                                return False
                        else :
                            print("Error! Line ",line+1," >>>>>>>>>>END指令格式錯誤")
                            error += 1
                            return False             
                else :
                    # 排版
                    if_mnemonic += 1
                    if if_mnemonic == 1 :
                        recoder_j = j
        if startLine == -1 :
            print("Error! Line ",line+1," >>>>>>>>>>指令不是從 START 開始")
            error += 1
            return False
        elif if_mnemonic+if_pseudocode > 1 :
            print("Error! Line ",line+1," >>>>>>>>>>mnemonic 或 假指令 總共有",if_mnemonic+if_pseudocode,"個")
            error += 1
            return False
        elif if_mnemonic+if_pseudocode == 1 :
            if recoder_j == 0 and len(data) == 1:
                data.insert(0,"")
                data.insert(2,"")
            elif recoder_j == 1 and len(data) == 2 :
                data.insert(2,"")
            elif recoder_j == 0 and len(data) == 2 :
                data.insert(0,"")
            elif recoder_j != 1 and len(data) == 3 :
                error += 1
                print("Error! Line ",line+1," >>>>>>>>>>格式錯誤，mnemonic在錯誤位置")
                error += 1
                return False
        elif if_mnemonic+if_pseudocode == 0 :
            print("Error! Line ",line+1," >>>>>>>>>>沒有mnemonic 或 假指令")
            error += 1
            return False
     
        # Label定義到的就加入
        if data[0] != "" :
            # else 為RSUB 給標籤
            if data [2] != "" :
                if  data[0] == data[2] :
                    print("Error! Line ",line+1," >>>>>>>>>>Label與Operand相同",data[0])
                    error += 1
                    return False
                else :
                    if search_Label(data[0]) == False :
                        if data[1] == "BYTE" :
                            if data[2][1] == "'" and data[2][-1] == "'" and len(data[2])>3 :
                                insert_Label(data[0],True,address,line,False)
                            else :
                                print("Error! Line ",line+1," >>>>>>>>>>BYTE格式有誤")
                                error += 1
                                return False
                        else :
                            insert_Label(data[0],True,address,line,False)
                    else :
                        print("Error! Line ",line+1," >>>>>>>>>>Label重複定義",data[0])
                        error += 1
                        return False
    else :
        
        print("Error! Line ",line+1, ">>>>>>>>>>輸入有誤，超過三個輸入值")
        # START 超過三欄位
        if "START" in data :
            startLine = line
        error += 1
        return False
    return data

def count_address(data,line):
    global address,error
    # 先處理label
    address = int(str(address), 16)
    if data[1] == "BYTE" :
        if data[2][1] == "'" and data[2][-1] == "'":
            # C = len()
            tmp = data[2][2:-1]
            if tmp != "":
                if data[2][0] == "C" :
                    address = hex(address + len(tmp))
                    # object Code===========================
                    
                    aci = ""
                    for k in range(len(tmp)) :
                        aci = aci + str(hex(ord(tmp[k]))[2:])
                    return aci
                    # object Code===========================


                # X = len()/2 必須偶數個
                elif data[2][0] == "X" :
                    
                    if len(tmp) % 2 == 0 : 
                        address = hex(address + int(len(tmp)/2))
                        if if_hex(tmp) == False :
                            print("Error! Line ",line+1," >>>>>>>>>>BYTE X 型態後要為16進位")
                            error += 1
                            return False
                            
                        # object Code===========================
                        else :
                            return tmp
                        # object Code===========================
                    else :
                        print("Error! Line ",line+1," >>>>>>>>>>BYTE hex的operand有誤，有半byte的情況")
                        error += 1
                        return False
                else :
                    print("Error ! Line ",line+1," >>>>>>>>>> BYTE格式有誤  C' ' / X' ' ")
                    error += 1
                    return False
            else :
                address = hex(address)
                print("Error! Line ",line+1," >>>>>>>>>>BYTE 型態後面沒有給值")
                error += 1
                return False
        else :
            address = hex(address)
            print("Error! Line ",line+1," >>>>>>>>>>BYTE 的operand格式('')有誤")
            error += 1
            return False
    elif data[1] == "WORD" :
        if data[2].isdigit() == False :
            print("Error! Line ",line+1," >>>>>>>>>>WORD 後面接10進位的值")
            address = hex(address)
            error += 1
            return False
        # 轉16進位
        address = hex(address + 3)
        return hex(int(data[2]))[2:].zfill(6)
    elif data[1] == "RESW" :
        if data[2].isdigit() == False :
            print("Error! Line ",line+1," >>>>>>>>>>RESW 後面接10進位的值")
            address = hex(address)
            error += 1
            return False
        # n*3
        address = hex(address + int(data[2])*3)
    elif data[1] == "RESB" :
        if data[2].isdigit() == False :
            print("Error! Line ",line," >>>>>>>>>>RESB 後面接10進位的值")
            address = hex(address)
            error += 1
            return False
        # 轉hex
        address = hex(address + int(data[2]))
    
    elif data[1] != "START" and data[1] != "END":
        address = hex(address + 3)
        # object Code===========================
        # RSUB 後面不能 + 咚咚
        if data[1] == "RSUB" :
            if data[2] != "" :
                print("Error! Line ",line+1," >>>>>>>>>>RSUB 後面不能加 Operand")
                error += 1
                return False

        opCode = search_op(data[1])
        if opCode != False :
            if len(data[2]) != 0 :
                labe_address = ""
                # 先確認是否為索引定址
                if "," in data[2] :
                    if data[2][-2:] == ",X" :
                        tmp2 = data[2].split(",")
                        labe_address = search_Label(tmp2[0])

                        # 有定義
                        if labe_address != False :
                            opCode = hex(int(opCode+"0000",16) + int(labe_address,16))
                        # 沒有定義
                        else :
                            opCode = hex(int(opCode+"0000",16))
                            insert_Label(tmp2[0],False,hex(int(address,16) - 2 ),line,False) # 改後面兩個bytes
                            index_addressing.append(hex(int(address,16) - 2 ))
                        return opCode[2:].zfill(6)
                    else :
                        print("Error! Line ",line+1," >>>>>>>>>>索引定址格式有誤")
                        error += 1
                        return False
                else :
                    labe_address = search_Label(data[2])
                    # 有定義
                    if labe_address != False :
                        opCode = hex(int(opCode+"0000",16) + int(labe_address,16))
                        return opCode[2:].zfill(6)
                    # 沒有定義
                    else :
                        opCode = opCode + "0000"
                        insert_Label(data[2],False,hex(int(address,16) - 2),line,False)
                        # print(data[2],False,hex(int(address,16) - 2),line,False)
                        return opCode.zfill(6)
            else :
                opCode = opCode + "0000"
                return opCode 
                
                # print("Error >>>>>>>>>>定義變數沒給值")
        else :
            if "," in data[1] :
                print("Error! Line ",line+1," >>>>>>>>>>索引定址格式有誤")
                error += 1
                return False
                

        # object Code===========================
    else:
        address = hex(address)
        

    return ""

def recorder(proName,initAddress,endAddress) :
    outputFile = open('107213036陳思蓓_output.txt','w')

    # print("====================Object Code================================")
    # print("H",proName.ljust(6),initAddress[2:].zfill(6),hex(int(endAddress,16) - int(initAddress[2:],16))[2:].zfill(6).upper(),sep = " ")
    outputFile.write("H " + proName.ljust(6) + " " + initAddress[2:].zfill(6) + " " + (hex(int(endAddress,16) - int(initAddress[2:],16))[2:].zfill(6)).upper() + "\n")
    output = ""
    # 長度
    count = 0
    # T record起始位置
    pc = ""
    # relocation bits
    mrecord_output = ""
    for i in range(1,len(record)-1) :
        
        # if record[i].one_pass_TRecord != "End":
        # one pass 要改的 T record
        if record[i].one_pass_TRecord == True :
            # print(record[i].obJCode,"1")
            if output != "" :
                # print("T",pc[2:].zfill(6).upper(),hex(int(count/2))[2:].zfill(2).upper(),output,sep = " ")
                outputFile.write("T " + pc[2:].zfill(6).upper() + " " + hex(int(count/2))[2:].zfill(2).upper() + " " + output + "\n")
            ## T record 更正(one pass的位置)    
            # print("T",record[i].addR[2:].zfill(6).upper(),"02",record[i].obJCode[2:].upper().zfill(4),sep = " ")
            # print(record[i].one_pass_TRecord, record[i].addR, record[i].obJCode,record[i].MRecord)
            outputFile.write("T " + record[i].addR[2:].zfill(6).upper() + " 02 " + record[i].obJCode[2:].upper().zfill(4) + "\n")
            output = ""
            count = 0
            pc = ""
        # 非更改位置的T record
        else :
                
            if pc == "" :
                pc = record[i].addR
            # 長度沒爆前就一直塞
            if (count + len(record[i].obJCode)) <= 30*2 :
                # 普通指令
                if record[i].obJCode != "" :
                    if output == "" :
                        output =  record[i].obJCode.upper()
                    else :
                        output +=  " " + record[i].obJCode.upper()
                    count = count + len(record[i].obJCode)
                    if record[i].MRecord == True :
                        mrecord_output += "M " + hex(int(record[i].addR,16) - int(initAddress,16) + 1)[2:].upper().zfill(6) + " 04\n"
    
                # 遇到保留位置等等的指令
                else :
                    
                    # print(record[i].one_pass_TRecord, record[i].addR, record[i].obJCode, record[i].MRecord)
                    if output != "" :
                        # print("T",pc[2:].zfill(6).upper(),hex(int(count/2))[2:].upper().zfill(2),output,sep = " ")
                        outputFile.write("T " + pc[2:].zfill(6).upper() + " " + hex(int(count/2))[2:].upper().zfill(2) + " " + output + "\n")
                        output = ""
                        count = 0
                        pc = ""
            #  如果加現在這個爆掉了爆掉了!!! 就印出來前面的，然後紀錄這次進來的
            else :
                # print("T",pc[2:].zfill(6).upper(),hex(int(count/2))[2:].upper().zfill(2),output,sep = " ")
                if output != "" :
                    outputFile.write("T " + pc[2:].zfill(6).upper() +  " " + hex(int(count/2))[2:].upper().zfill(2) + " " + output + "\n")
                if len(record[i].obJCode) > 60 :
                    pc = record[i].addR
                    # print(len(record[i].obJCode))
                    for k in range (int(len(record[i].obJCode)/60)) :
                        outputFile.write("T " + pc[2:].upper().zfill(6) + " 1E " + record[i].obJCode[60*k:60*(k+1)].upper() + "\n")
                        pc = hex(int(pc,16) + 30)
                        count = len(record[i].obJCode[(k+1)*60:])
                        # print(count)
                        output = record[i].obJCode[(k+1)*60:].upper()
                else :
                    output = record[i].obJCode.upper()
                    count = len(record[i].obJCode)
                    pc = record[i].addR
                # print("3")
    # M recod
    # print(mrecord_output[0:-1])
    # if initAddress[2:] != "1000" :
    outputFile.write(mrecord_output)
    
    # print("E",record[len(record)-1].addR[2:].upper().zfill(6),sep = " ")
    outputFile.write("E " + record[len(record)-1].addR[2:].upper().zfill(6))
    outputFile.close()

# 讀檔案
def read_txt() :
    global error
    end_program = False
    keep = []
    s = txtContxt.split("\n")
    for i in range (len(s)) :   
        # 用len() = 0判斷是不是空白行
        if len(s[i]) != 0 :
            # 第一次分割
            s[i] = s[i].replace("\t"," ") # tap替代成space
            s[i] = s[i].strip(" ") # 刪除前後space
            # 是否為整行註解
            if s[i][0] != "." :
                if end_program == True :
                    print("Error! Line ",i+1," >>>>>>>>>>指令在END後面")
                    error += 1
                    continue
                # 是否含有註解
                s[i] = s[i].split(".",1)
                # if len(s[i]) > 1 :
                #     print("[後面有註解]")
                s[i] = s[i][0].strip(" ")
                # 處理索引定址","的空格
                s[i] = s[i].split(",")
                if len(s[i]) > 1 :
                    if len(s[i]) > 2 :
                        print(s[i])
                        print("Error! Line ",i+1," >>>>>>>>>>索引定址格式有誤 : ,打太多囉")
                        error += 1
                        continue
                    elif "BYTE" in s[i][0] or  "WORD" in s[i][0] or  "RESB" in s[i][0] or  "RESW" in s[i][0] :
                        print("Error! Line ",i+1," >>>>>>>>>>後面不能加索引定址")
                        error += 1
                        continue
                    else :
                        # print("[含有索引定址]")
                        s[i] = s[i][0].strip(" ") +","+ s[i][1].strip(" ")
                else :
                    s[i] = s[i][0]
                # 處理byte的型態
                tmp = s[i].split("'")
                if len(tmp) == 3 :
                    for j in range(len(tmp)):
                        if j == 0 :
                            s[i] = tmp[j].strip(" ") + "'"
                        elif tmp[j] != "" :
                            s[i] += tmp[j].strip(" ") + "'"
                elif len(tmp) == 1 :
                    s[i] == s[i][0]
                else :
                    print("Error ! Line ",i+1," >>>>>>>>>> C' '/ X' ' 的格式有誤 ")
                    error += 1
                    continue
                
                # =============做動作區==============

                # 處理data
                slicData = slic_data(s[i],i)
                # True表示結束(讀到END)
                if slicData == True :
                    s[i] = s[i].split(" ")
                    for p in range(len(s[i])):
                        if '' in s[i] :
                            s[i].remove('')
                    s[i].insert(0,"")
                # 有error input
                elif slicData == False : 
                    continue
                else :
                    s[i] = slicData

                # 計算位置
                if s[i][1] != "START" :
                    
                    ad_record = address
                    if_error = count_address(s[i],i)
                    if if_error == False :
                        continue
                    else :
                        keep.append(progFront(s[i],ad_record,if_error))
                        if s[i][1]== "BYTE" or s[i][1] == "WORD" or s[i][1] == "RESB" or s[i][1] == "RESW" or s[i][2] == "":
                            record.append(recordFront(False,keep[len(keep)-1].addR,keep[len(keep)-1].obJCode,False))
                        else :
                            record.append(recordFront(False,keep[len(keep)-1].addR,keep[len(keep)-1].obJCode,True))
                else :
                    keep.append(progFront(s[i],address,""))
                    record.append(recordFront(s[i][1],address,"",""))

                # True表示結束
                if slicData == True :
                    end_addr = search_Label(s[i][2])
                    record.append(recordFront(s[i][1],end_addr,end_addr,False))
                    end_program  = slicData

    # print("===============就一個整理好的Table(包含address、object code)===================")
    # for i in range(len(keep)):
    #     print(show_data(keep[i].data),"\t"," Address : " ,keep[i].addR,"\t", "Object Code",keep[i].obJCode)

    for key,value in symbolTab.items():
        if value.if_def == False :
            for m in range(len(value.line)) :
                print("Error ! Line ",value.line[m]+1," >>>>>>>>>>Operand:",key,"沒有定義到此Label")
            error += 1
    if end_program == False :
        print("Error !>>>>>>>>>> 沒有結束指令 : END")
        error += 1
    if error == 0 :
        recorder(keep[0].data[0],keep[0].addR,keep[len(keep)-1].addR)
        print("執行成功，結果已寫入 Output.txt")


opCodeCon()
read_txt()
# 查看label Table
# for key,value in symbolTab.items():
#     print("'{key}'".format(key = key) ," \t:'{TF},{AR}', \t Line '{L}'" .format( TF = value.if_def, AR = value.addR, L = value.line))



