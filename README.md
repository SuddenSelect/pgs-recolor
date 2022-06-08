# pgs-recolor

## Usage

1. Get Python 3
2. Get the subtitle files
3. Run `python pgs-recolor.py /path/to/files/*.sup` -> outputs files with `_bw` suffix in the same directory
4. Use the `*_bw.sup` subtitle files

## What is this?

Quick, dirty and dumb simple script changing ugly yellow PGS subtitles to more tolerable grayscale. 

Inspired by:
- [pgsreader](https://github.com/EzraBC/pgsreader) (seriously, understanding the format and prototyping would have been much more challenging without it),
- lack of tooling allowing modification of PGS subtitles (or at least I did not found anything promising)
- media players that cannot change colors of PGS subtitles in-flight.


## Theory

PGS format (usually with '.sup' extension) is a binary format containing equally binary images of subtitles.
Any significant modification (like fonts or shadows) requires migration to a normal text-based subtitle format via OCR
and playing with styles. For my purposes however, only changing the ugly piss-yellow color would suffice.

Luckily, PGS stores color information as palettes. 
If text images reference "piss-yellow", we can just redefine what "piss-yellow" is.
Leveraging the palette format (YCrCb) makes things even simpler - 
we can just drop all color information whatsoever and leave only the glorious grayscale by setting Cr and Cb to 128 and
leaving luma Y intact. 
If the luma happens to be too gray - moving it away from 128 towards black or white would also be relatively simple.

The obvious downside is of course throwing away any color-coding of dialogs or signs. But I can live with that.


## Presentation Graphic Stream BluRay Subtitle Format

### Segment Header

13 bytes

Name|Size in bytes|Description
---|---|---
Magic Number|2|"PG" (0x5047)
PTS|4|Presentation Timestamp
DTS|4|Decoding Timestamp
Segment Type|1|0x14: Palette Definition Segment <br> 0x15: Object Definition Segment  <br> 0x16: Presentation Composition Segment <br> 0x17: Window Definition Segment <br> 0x80: End of Display Set Segment
Segment Size|2|Size of the segment


### Palette Definition Segment

2 bytes + 5 repeating bytes

[r] - indicates repetition

Name|Size in bytes|Definition
---|---|---
Palette ID|1|ID of the palette
Palette Version Number|1|Version of this palette within the Epoch
[r] Palette Entry ID|1|Entry number of the palette
[r] Luminance (Y)|1|Luminance (Y value)
[r] Color Difference Red (Cr)|1|Color Difference Red (Cr value)
[r] Color Difference Blue (Cb)|1|Color Difference Blue (Cb value)
[r] Transparency (Alpha)|1|Transparency (Alpha value)