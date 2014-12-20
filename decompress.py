#!/usr/bin/python3
import argparse
import os.path
from os.path import basename, splitext
import struct

def read_size(compressed):
    values = list(compressed.read(1))
    if not values:
        return 0, None
    back_flag = (values[0] & 0b01000000)
        
    while values[-1] & 0b10000000:
        values += compressed.read(1)
    
    size = 0
    for i, value in enumerate(reversed(values)):
        if i == len(values) - 1:
            mask = 0x3F
        else:
            mask = 0x7F
        size |= (value & mask) << i * 7
    
    if i > 2:
        print('Debug: size[2] >= 0x80', compressed.tell() - 1, len(decompressed), offset)
        
    return back_flag, size
    
def read_offset(compressed):
    values = list(compressed.read(1))
        
    while values[-1] & 0b10000000:
        values += compressed.read(1)
    
    offset = 0
    for i, value in enumerate(reversed(values)):
        offset |= (value & 0x7F) << i * 7
    
    if i > 2:
        print('Debug: offset[2] >= 0x80', compressed.tell() - 1, len(decompressed), offset)

    return offset

def decompress(compressed):
    decompressed = [] # List is much faster because it's mutable

    i = 0

    while True:
        back_flag, size = read_size(compressed)
        
        if size is None:
            break

        if back_flag:
            # Replay n + 3 chars from already decompressed
            offset = read_offset(compressed)
            start = len(decompressed) - offset
            size += 3
            
            for pos in range(start, start + size):
                decompressed += decompressed[pos:pos + 1]
        else:
            decompressed += compressed.read(size)
            
    return bytes(decompressed)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decompress files from Sonic Boom .wiiu.stream')
    parser.add_argument('files', nargs='+', type=argparse.FileType('rb'), help='compressed file')
    parser.add_argument('-d', '--dir', help='output dir', nargs='?')

    args = parser.parse_args()     
    
    for compressed in args.files:
        decompressed = decompress(compressed)
        output_name = compressed.name
        if args.dir:
            output_name = os.path.join(args.dir[0], basename(output_name))

        try:
            if os.path.samefile(compressed.name, output_name):
                output_name = '{}.decompressed{}'.format(*os.path.splitext(output_name))
        except FileNotFoundError:
            pass

        output = open(output_name, 'wb')
        output.write(decompressed)
