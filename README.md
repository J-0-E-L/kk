# kk
A tool that automates the creation of Kris Kringle allocations, respecting user-defined rules.

## Usage
Run using ```./kk.py <filename>```, where ```<filename>``` contains the schematic for the Kris Kringle. Ensure that all packages listed in requirements.txt are accessible in the active python3 environment.

## Schematics
There are four operators in the schematic language:
- Add to group (```:```). e.g. ```G: A, B, C``` adds members ```A```, ```B```, ```C``` to group ```G```.
- Add to buy group (```->```). e.g. ```A -> B, C``` forces ```A``` to buy for ```B``` or ```C```. Subsequent uses of ```->``` may expand the allowable options for ```A```.
- Add to avoid group (```-x```). e.g. ```A -x B, C``` disallows ```A``` from buying for ```B``` and ```C```.
- Expand to members (```.```). e.g. if previously ```G: A, B```, then ```G -x .``` expands to the three commands ```A -x A```, ```B -x B```, and ```C -x C```.

Note that any name that is not the name of a group is interpreted as a participant in the Kris Kringle.
