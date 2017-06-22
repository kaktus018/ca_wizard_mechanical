# ca_wizard_mechanical
Welcome to the ca_wizard_mechanical GitHub repository!

ca_wizard_mechanical allows the generation of comm-files for simple 3D structural analyses in code_aster with an interactive GUI.

First of all, I would like to point out that I'm no professional programmer, new to Python and GitHub, no FEM/CSD or code_aster expert. Still I started with the development of a small GUI-program that allows the generation of comm-files for code_aster and think that it is worth sharing now.

The functionality is a little bit cut to my own needs (one of them being that I only perform simulations with 3D elements), but I still think that it can be useful to others. I’m happy to receive your feedback and make the code even better. Commits are of course welcome as well.
I recently did some work on the code and wasn’t able to test it a lot (especially with simulations). So there is a good chance one or two bugs might be hiding somewhere.

My personal scope for future development: add logic for modal and maybe buckling analyses, later add non-linear material functionalities (although I have to admit that I never even came in touch with non-linear material models).

To run it, you will need Python v. 3 and the following libraries: os, pickle, shutil, webbrowser, time, re, codecs, xml, urllib and tkinter. Download the files `cawm_gui.py`, `cawm_classes.py`, `matLib.xml` and `__init__.py` and save them at the same location. Then run `cawm_gui.py` in the Python interpreter. Also, take a look at the [user guide](https://github.com/kaktus018/ca_wizard_mechanical/wiki/User-Guide) in the wiki.

For license information, take a look at [LICENSE.txt](LICENSE.txt).

The latest version can be found in the [development branch](https://github.com/kaktus018/ca_wizard_mechanical/tree/development).
