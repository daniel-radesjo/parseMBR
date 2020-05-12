# parseMBR
Parse information and find/carve Master Boot Records (MBR).

```
python parseMBR.py -h
usage: parseMBR.py [-h] [-o <offset>] [-f] [-v] image

Author: Daniel Rådesjö (daniel.radesjo@gmail.com)
        https://github.com/daniel-radesjo/parseMBR

positional arguments:
  image          raw/dd source image

optional arguments:
  -h, --help     show this help message and exit
  -o <offset>    byte offset (default: 0)
  -f             find MBR offsets
  -v, --version  show program's version number and exit
```


Example
```
python parseMBR.py 10-ntfs-disk.dd
Offset  Hex     Length  Description     Value
0       0x0     440     Bootstrap       0x33c08ed0bc...00002c4463
440     0x1b8   4       Disk Signature  0x44b323fc = 0xfc23b344 (LE)
444     0x1bc   2       Reserved        0x0000
446     0x1be   16      Partition 1     0x0001010007fe3f053f00000047780100
446     0x1be   1       Partition flag  0x00 = Inactive
447     0x1bf   1       Start head      0x01 = 1
448     0x1c0   1       Start sector    0x01
449     0x1c1   1       Start cylinder  0x00
450     0x1c2   1       File system ID  0x07 = NTFS
451     0x1c3   1       End head        0xfe = 254
452     0x1c4   1       End sector      0x3f
453     0x1c5   1       End cylinder    0x05
454     0x1c6   4       First sector    0x3f000000 = 0x3f (LE) = sector 63 = 32256 bytes
458     0x1ca   4       Total sectors   0x47780100 = 0x017847 (LE) = 96327 sectors = 47.03MB
462     0x1ce   16      Partition 2     0x0000010607fe3f0b8678010086780100
462     0x1ce   1       Partition flag  0x00 = Inactive
463     0x1cf   1       Start head      0x00 = 0
464     0x1d0   1       Start sector    0x01
465     0x1d1   1       Start cylinder  0x06
466     0x1d2   1       File system ID  0x07 = NTFS
467     0x1d3   1       End head        0xfe = 254
468     0x1d4   1       End sector      0x3f
469     0x1d5   1       End cylinder    0x0b
470     0x1d6   4       First sector    0x86780100 = 0x017886 (LE) = sector 96390 = 49351680 bytes
474     0x1da   4       Total sectors   0x86780100 = 0x017886 (LE) = 96390 sectors = 47.07MB
478     0x1de   16      Partition 3     0x0000...0000 = No partition configured
494     0x1ee   16      Partition 4     0x0000...0000 = No partition configured
510     0x1fe   2       Boot signature  0x55aa
```
