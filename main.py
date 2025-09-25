# -*- coding: utf-8 -*-

# @autor: Matheus Felipe
# @github: github.com/matheusfelipeog

# PT: Builtins
# EN: Builtins
# FR: Noyaux
import tkinter as tk

# PT: Módulo próprio (interface principal)
# EN: Local module (main interface)
# FR: Module local (interface principale)
from app.calculadora import Calculadora

if __name__ == '__main__':
    # PT: Cria a janela principal e inicia a calculadora
    # EN: Create the main window and start the calculator
    # FR: Crée la fenêtre principale et lance la calculatrice
    master = tk.Tk()
    main = Calculadora(master)
    main.start()
