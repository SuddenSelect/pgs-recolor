import os.path
import sys
from pathlib import Path


class PGSPaletteGrayscaler:

    def __init__(self, pgs_bytes):
        self.segment_type_palette = int('0x14', 16)
        self.header_size = 13
        self.pgs_bytes = pgs_bytes

    def __find_next_segment_by_magic_number(self, current_segment_location):
        for i in range(current_segment_location+2, len(self.pgs_bytes)):
            if self.pgs_bytes[i:i + 2] == b'PG':
                return i
        raise Exception(f'panic - next segment was not found, starting from byte {current_segment_location}')

    def __next_segment(self):
        i = 0
        while i < len(self.pgs_bytes):
            if self.pgs_bytes[i:i + 2] != b'PG':
                raise Exception('panic')
            segment_size = self.header_size + int.from_bytes(self.pgs_bytes[i + 11:i + 13], byteorder='big')
            if i+segment_size < len(self.pgs_bytes) and self.pgs_bytes[i + segment_size:i + segment_size + 2] != b'PG':
                next_segment_magic_number_location = self.__find_next_segment_by_magic_number(i)
                print(f'WARNING: declared segment size was {segment_size}, but it seems to be {next_segment_magic_number_location - i} at byte {i}')
                segment_size = next_segment_magic_number_location - i
            segment = self.pgs_bytes[i:i + segment_size]
            segment_type = self.pgs_bytes[i + 10]
            i += segment_size
            yield segment_type, segment

    @staticmethod
    def __transform_segment(segment):
        modified_segment = segment[:15]
        for palette in range(15, len(segment), 5):
            id_y_cr_cb_alpha = bytearray(segment[palette:palette+5])
            id_y_cr_cb_alpha[2:4] = [128, 128]  # changing color to grayscale in YCrCb color space
            modified_segment += id_y_cr_cb_alpha
        if len(segment) != len(modified_segment):
            raise Exception('panic - different size of modified segment')
        return modified_segment

    def grayscale(self):
        modified_pgs = bytes()
        for segment_type, segment in self.__next_segment():
            if segment_type == self.segment_type_palette:
                modified_pgs += self.__transform_segment(segment)
            else:
                modified_pgs += segment
        if len(self.pgs_bytes) != len(modified_pgs):
            raise Exception('panic - different size of pgs_bytes')
        return modified_pgs


def modify_subtitles(files, suffix='_bw'):
    for file in files:
        name_file_src, name_file_ext = os.path.splitext(os.path.basename(file))
        file_path_src = os.path.join(os.path.dirname(file), name_file_src + name_file_ext)
        file_path_dst = os.path.join(os.path.dirname(file), name_file_src + suffix + name_file_ext)
        with open(file_path_src, 'rb') as pgs_src:
            magic_number = pgs_src.read(2)
            pgs_src.seek(0, 0)
            if magic_number == b'PG':
                with open(file_path_dst, 'wb') as pgs_dst:
                    print(f'PGS: {name_file_src+name_file_ext}')
                    grayscaler = PGSPaletteGrayscaler(pgs_src.read())
                    try:
                        pgs_dst.write(grayscaler.grayscale())
                    except Exception as e:
                        print(f'ERROR: {str(e)}')
            else:
                print(f'Not a PGS file: {name_file_src+name_file_ext}')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if '*' in os.path.basename(arg):
                files = [x for x in Path(os.path.dirname(arg)).glob(os.path.basename(arg))]
            else:
                files = [arg]
            modify_subtitles(files)
    else:
        print('no input given')
