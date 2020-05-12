#!/usr/bin/python
#Parser and finder/carver for Master Boot Record (MBR)
import struct
import sys
import argparse
import os.path

version = "P1.0"

class Partition:

    __data = None

    #[Name, Offset, Length, Value]
    __structure = [
        ["Partition flag", 0, 1, None],
        ["Start head", 1, 1, None],
        ["Start sector", 2, 1, None],
        ["Start cylinder", 3, 1, None],
        ["File system ID", 4, 1, None],
        ["End head", 5, 1, None],
        ["End sector", 6, 1, None],
        ["End cylinder", 7, 1, None],
        ["First sector", 8, 4, None],
        ["Total sectors", 12, 4, None]
    ]

    #Reference: https://www.garykessler.net/software/index.html
    __type = { 
        b'\x00':"Empty",
        b'\x01':"FAT12,CHS",
        b'\x04':"FAT16 16-32MB,CHS",
        b'\x05':"Microsoft Extended",
        b'\x06':"FAT16 32MB,CHS",
        b'\x07':"NTFS",
        b'\x0b':"FAT32,CHS",
        b'\x0c':"FAT32,LBA",
        b'\x0e':"FAT16, 32MB-2GB,LBA",
        b'\x0f':"Microsoft Extended, LBA",
        b'\x11':"Hidden FAT12,CHS",
        b'\x14':"Hidden FAT16,16-32MB,CHS",
        b'\x16':"Hidden FAT16,32MB-2GB,CHS",
        b'\x18':"AST SmartSleep Partition",
        b'\x1b':"Hidden FAT32,CHS",
        b'\x1c':"Hidden FAT32,LBA",
        b'\x1e':"Hidden FAT16,32MB-2GB,LBA",
        b'\x27':"PQservice",
        b'\x39':"Plan 9 partition",
        b'\x3c':"PartitionMagic recovery partition",
        b'\x42':"Microsoft MBR,Dynamic Disk",
        b'\x44':"GoBack partition",
        b'\x51':"Novell",
        b'\x52':"CP/M",
        b'\x63':"Unix System V",
        b'\x64':"PC-ARMOUR protected partition",
        b'\x82':"Solaris x86 or Linux Swap",
        b'\x83':"Linux",
        b'\x84':"Hibernation",
        b'\x85':"Linux Extended",
        b'\x86':"NTFS Volume Set",
        b'\x87':"NTFS Volume Set",
        b'\x9f':"BSD/OS",
        b'\xa0':"Hibernation",
        b'\xa1':"Hibernation",
        b'\xa5':"FreeBSD",
        b'\xa6':"OpenBSD",
        b'\xa8':"Mac OSX",
        b'\xa9':"NetBSD",
        b'\xab':"Mac OSX Boot",
        b'\xaf':"MacOS X HFS",
        b'\xb7':"BSDI",
        b'\xb8':"BSDI Swap",
        b'\xbb':"Boot Wizard hidden",
        b'\xbe':"Solaris 8 boot partition",
        b'\xd8':"CP/M-86",
        b'\xde':"Dell PowerEdge Server utilities (FAT fs)",
        b'\xdf':"DG/UX virtual disk manager partition",
        b'\xeb':"BeOS BFS",
        b'\xee':"EFI GPT Disk",
        b'\xef':"EFI System Parition",
        b'\xfb':"VMWare File System",
        b'\xfc':"VMWare Swap",
    }

    __flag = {
        b'\x00': "Inactive",
        b'\x80': "Active"
    }

    def __init__(self, data, offset):
        self.__data = data
        self.__offset = offset
        self.parse()

    def __str__(self):
        returnValue = ""

        for item in self.__structure:
            value = item[3].hex()
            decoded_value = ""
            if item[0] == "Partition flag":
                decoded_value = " = " + self.__flag.get(item[3], "Not defined")
            elif item[0].endswith("head"):
                decoded_value = " = " + str(int(struct.unpack("<B", item[3])[0]))
            elif item[0] == "File system ID":
                decoded_value = " = " + self.__type.get(item[3], "Not defined")
            elif item[0] == "First sector":
                decoded_value = " = 0x" + self.zeroes_lstrip(str(struct.pack("<L", *struct.unpack(">L", item[3])).hex())) + " (LE) = sector " + str(int(struct.unpack("<L", item[3])[0])) + " = " + str(512 * int(struct.unpack("<L", item[3])[0])) + " bytes"
            elif item[0] == "Total sectors":
                decoded_value = " = 0x" + self.zeroes_lstrip(str(struct.pack("<L", *struct.unpack(">L", item[3])).hex())) + " (LE) = " + str(int(struct.unpack("<L", item[3])[0])) + " sectors = " + self.getReadableBytes(512 * int(struct.unpack("<L", item[3])[0]))

            returnValue += "\n" + str(self.__offset + item[1]) + "\t" + str(hex(self.__offset + item[1])) + "\t" + str(item[2]) + "\t" + item[0] + "\t0x" + value + decoded_value
        
        return returnValue

    def validate(self):

        returnValue = False

        if self.__data == b"\x00" * 16: #Partition not defined
            returnValue = True
        else:
            for item in self.__structure:
                if item[0] == "Partition flag":
                    if item[3] in self.__flag:
                        returnValue = True
                if item[0] == "First sector":
                    if item[3] == b"\x00\x00\x00\x00":
                        returnValue = False
                if item[0] == "Total sectors":
                    if item[3] == b"\x00\x00\x00\x00":
                        returnValue = False
        
        return returnValue

    def isExtended(self):

        returnValue = False

        for item in self.__structure:
            if item[0] == "File system ID" and item[3] in [b"\x0f"]:
                returnValue = True
                break
        
        return returnValue

    def parse(self):
        for item in self.__structure:
            item[3] = self.__data[item[1]:item[1] + item[2]]

    def zeroes_lstrip(self, value):
        while(value[0:2] == "00"):
            value = value[2:]

        return value

    def getReadableBytes(self,i):

        returnValue = i

        conv = { 
            1024*1024*1024*1024:"TB",
            1024*1024*1024:     "GB",
            1024*1024:          "MB",
            1024:               "kB"
        }
        
        for (key, value) in conv.items():
            if i > key:
                returnValue = str(round(float(i/key),2)) + value
                break

        return returnValue

class MBR:

    __data = None

    #[Name, Offset, Length, Value]
    __structure = [
        ["Bootstrap", 0, 440, None],
        ["Disk Signature", 440, 4, None],
        ["Reserved", 444, 2, None],
        ["Partition 1", 446 + (1-1) * 16, 16, None],
        ["Partition 2", 446 + (2-1) * 16, 16, None],
        ["Partition 3", 446 + (3-1) * 16, 16, None],
        ["Partition 4", 446 + (4-1) * 16, 16, None],
        ["Boot signature", 510, 2, None]
    ]

    def __init__(self, data):
        self.__data = data
        self.parse()

    def parse(self):
        for item in self.__structure:
            item[3] = self.__data[item[1]:item[1] + item[2]]

    def validate(self):
        returnValue = False

        if self.__data != b"\x00" * 512: #empty sector

            #Validate that not all partitions is of typ 0x00 (false positive)
            for i in range(4): 
                if self.__data[446+16*i+4:446+16*i+4+1] != b"\x00":
                    returnValue = True
                    break

            for item in self.__structure:
                if item[0] == "Reserved" and item[3] == b"\x00\x00": #Reserved = 0x0000
                    returnValue &= True
                elif item[0].startswith("Partition"):
                    returnValue &= Partition(item[3], item[1]).validate() #Validate partitions
                elif item[0] == "Boot signature" and item[3] != b"\x55\xaa": #Boot signature (last two bytes) = 0x55aa
                    returnValue = False

        return returnValue

    def __str__(self):

        returnValue = "Offset\tHex\tLength\tDescription\tValue"

        for item in self.__structure:

            decoded_value = ""
            value = item[3].hex()

            if item[0] == 'Bootstrap':
                value = item[3].hex()[0:10] + "..." + item[3].hex()[-10:]
            elif item[0].startswith("Partition"):
                if value == "00" * 16:
                    value = item[3].hex()[0:4] + "..." + item[3].hex()[-4:]
                    decoded_value = " = No partition configured"
                else:
                    decoded_value = str(Partition(item[3], item[1]))
            elif item[0] == "Disk Signature":
                decoded_value = " = 0x" + str(struct.pack("<L", *struct.unpack(">L", item[3])).hex()) + " (LE)"

            returnValue += "\n" + str(item[1]) + '\t' + str(hex(item[1])) + '\t' + str(item[2]) + '\t' + item[0] + "\t0x" + str(value) + decoded_value

        return returnValue

def readFile(filename, offset):
    if os.path.exists(filename):
        f = open(filename, "rb")
        f.seek(offset)
        return f
    else:
        print("File " + filename + " doesn't exists")
        exit()

def findMBR(filename, offset):
    f = readFile(args.image, int(args.o))

    header = True

    while bytes := f.read(512):
        
        if bytes != b"\x00" * 512: #empty sector

            mbr = MBR(bytes)

            if mbr.validate():
                if header:
                    print("{:<14}{:<12}{:<12}{:<12}{:<12}{:<12}{:<8}".format("Offset", "DiskSign", "Part 1", "Part 2", "Part 3", "Part 4", "BootSign"))
                    header = False
                
                print("{:<14}{:<12}{:<12}{:<12}{:<12}{:<12}{:<8}".format(str(f.tell() - 512),   #Offset
                    "0x" + str(struct.pack("<L", *struct.unpack(">L", bytes[440:444])).hex()),  #Disk signature
                    str(int(struct.unpack("<L", bytes[446+16*0+8:446+16*0+8+4])[0])),           #Part 1, first sector
                    str(int(struct.unpack("<L", bytes[446+16*1+8:446+16*1+8+4])[0])),           #Part 2, first sector
                    str(int(struct.unpack("<L", bytes[446+16*2+8:446+16*2+8+4])[0])),           #Part 3, first sector
                    str(int(struct.unpack("<L", bytes[446+16*3+8:446+16*3+8+4])[0])),           #Part 4, first sector
                    "0x" + bytes[-2:].hex())                                                    #Boot signature 
                )

    f.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog = "parseMBR.py", description="(c) Daniel Rådesjö 2020")
    parser.add_argument("image", action="store", type=str, help="raw/dd source image")
    parser.add_argument("-o", help="byte offset (default: 0)", default="0", metavar="<offset>", type=int)
    parser.add_argument("-f", help="find MBR offsets", action="store_true")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + version)
    args = parser.parse_args()

    if(args.f): #Find/Carve MBR
        findMBR(args.image, int(args.o))
    else: #List MBR values from filename and offset
        f = readFile(args.image, int(args.o))
        mbr = MBR(f.read(512))
        f.close()

        if mbr.validate():
            print(str(mbr))
        else:
            print("Error parsing MBR")
