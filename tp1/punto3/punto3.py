# -*- coding: utf-8 -*-
import sys
import os
import unicodedata
import string

# Agrego al path la carpeta modulos
sys.path.insert(0, os.path.abspath("../punto1"))
import punto1

if __name__ == "__main__":
	punto1.menu()