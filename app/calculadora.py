# -*- coding: utf-8 -*-

# @autor: Matheus Felipe
# @github: github.com/matheusfelipeog

# PT: Builtins (importações padrão)
# EN: Builtins (standard imports)
# FR: Noyaux (imports standard)
import sys
import os
import platform

# PT: GUI toolkit
# EN: GUI toolkit
# FR: Boîte à outils GUI
import tkinter as tk
from tkinter import Menu, FALSE

# PT: Utilitários
# EN: Utilities
# FR: Utilitaires
from functools import partial
from json import load as json_load
from json import dump as json_dump
from datetime import datetime
import csv

from copy import deepcopy

# PT: Módulos próprios (lógica e traduções)
# EN: Local modules (logic and translations)
# FR: Modules locaux (logique et traductions)
from .calculador import Calculador
from .i18n import translations


class Calculadora(object):
    """Classe para criação do layout da calculadora e funcionalidades."""
    # PT: Classe para criação do layout da calculadora e funcionalidades
    # EN: Class to create the calculator layout and functionality
    # FR: Classe pour créer la mise en page et les fonctionnalités de la calculatrice

    def __init__(self, master):
        self.master = master
        self.calc = Calculador()

        self.settings = self._load_settings()
        # PT: Código do idioma atual: 'en', 'pt', 'fr'
        # EN: Current language code: 'en', 'pt', 'fr'
        # FR: Code de langue actuel : 'en', 'pt', 'fr'
        self.current_language = self.settings.get('current_language', 'en')
        self._t = translations.get(self.current_language, translations.get('en', {}))

        # PT: Seleção de tema
        # EN: Theme selection
        # FR: Sélection du thème
        if platform.system() == 'Darwin':
            self.theme = self._get_theme('Default Theme For MacOS')
        else:
            self.theme = self._get_theme(self.settings.get('current_theme', 'Dark'))

        # Historique des calculs (history restored before UI shown)
        self._history = self._load_history()

        # PT: Janela principal (usa título traduzido)
        # EN: Main window (uses translated title)
        # FR: Fenêtre principale (utilise le titre traduit)
        self.master.title(self._t.get('title', 'Calculator Tk'))
        self.master.maxsize(width=335, height=415)
        self.master.minsize(width=335, height=415)
        self.master.geometry('-150+100')
        self.master['bg'] = self.theme['master_bg']

        # PT: Frame do input
        # EN: Input frame
        # FR: Cadre de saisie
        self._frame_input = tk.Frame(self.master, bg=self.theme['frame_bg'], pady=4)
        self._frame_input.pack(fill='x')

        # PT: Frame dos botões
        # EN: Buttons frame
        # FR: Cadre des boutons
        self._frame_buttons = tk.Frame(self.master, bg=self.theme['frame_bg'], padx=2)
        self._frame_buttons.pack()

        # PT: Inicializa a UI
        # EN: Initialize the UI
        # FR: Initialise l'interface
        self._create_input(self._frame_input)
        self._create_buttons(self._frame_buttons)
        self._create_menu(self.master)

    @staticmethod
    def _load_settings():
        # PT: Carrega configurações do arquivo JSON
        # EN: Load settings from JSON file
        # FR: Charger les paramètres depuis le fichier JSON
        with open('./app/settings/settings.json', mode='r', encoding='utf-8') as f:
            return json_load(f)

    def _get_theme(self, name='Dark'):
        # PT: Retorna configuração de estilo para o tema especificado
        # EN: Return style configuration for the specified theme
        # FR: Retourne la configuration de style pour le thème spécifié
        list_of_themes = self.settings.get('themes', [])
        found_theme = None
        for t in list_of_themes:
            if name == t.get('name'):
                found_theme = deepcopy(t)
                break
        return found_theme or {}

    def _create_input(self, master):
        # PT: Entrada usada como display
        # EN: Entry used as display
        # FR: Entrée utilisée comme affichage
        self._entrada = tk.Entry(master, cnf=self.theme.get('INPUT', {}))
        self._entrada.insert(0, 0)
        self._entrada.pack(side='right', padx=4)

    def _create_menu(self, master):
        # PT: Menu superior: Configuração -> Idioma, Tema, Sair
        # EN: Top menu: Configuration -> Language, Theme, Exit
        # FR: Menu supérieur : Configuration -> Langue, Thème, Quitter
        self.master.option_add('*tearOff', FALSE)
        calc_menu = Menu(self.master)
        self.master.config(menu=calc_menu)

        config = Menu(calc_menu)
        # PT: Submenu Idioma (acima de Tema)
        # EN: Language submenu (above Theme)
        # FR: Sous-menu Langue (au-dessus du Thème)
        lang_menu = Menu(config)
        # PT: Ordem exata: inglês, português, francês
        # EN: Exact order: english, portuguese, french
        # FR: Ordre exact : anglais, portugais, français
        lang_order = [
            ('en', self._t.get('language_names', {}).get('en', 'English')),
            ('pt', self._t.get('language_names', {}).get('pt', 'Portuguese')),
            ('fr', self._t.get('language_names', {}).get('fr', 'Français')),
        ]
        for code, label in lang_order:
            if code == self.current_language:
                # disable the current language option
                lang_menu.add_command(label=label, state='disabled')
            else:
                lang_menu.add_command(label=label, command=partial(self._change_language, code))

        # PT: Submenu Tema (mesma interface que a lista de temas)
        # EN: Theme submenu (same interface as the theme list)
        # FR: Sous-menu Thème (même interface que la liste des thèmes)
        theme = Menu(config)
        theme_incompatible = ['Default Theme For MacOS']
        current_theme_name = self.settings.get('current_theme', 'Dark')
        for t in self.settings.get('themes', []):
            name = t.get('name')
            if not name or name in theme_incompatible:
                continue
            if name == current_theme_name:
                # disable the current theme option
                theme.add_command(label=name, state='disabled')
            else:
                theme.add_command(label=name, command=partial(self._change_theme_to, name))

        # PT: Monta o menu de configuração: Idioma acima de Tema
        # EN: Assemble the configuration menu: Language above Theme
        # FR: Assemble le menu de configuration : Langue au-dessus du Thème
        calc_menu.add_cascade(label=self._t.get('menu_configuration', 'Configuration'), menu=config)
        config.add_cascade(label=self._t.get('menu_language', 'Language'), menu=lang_menu)
        config.add_cascade(label=self._t.get('menu_theme', 'Theme'), menu=theme)

        config.add_separator()
        config.add_command(label=self._t.get('menu_exit', 'Exit'), command=self._exit)

        # History menu (localized labels with safe fallback)
        history = Menu(calc_menu)
        calc_menu.add_cascade(label=self._t.get('menu_history', 'History'), menu=history)
        history.add_command(label=self._t.get('history_show', 'Show...'), command=self._show_history)
        history.add_command(label=self._t.get('history_clear', 'Clear'), command=self._clear_history)
        history.add_command(label=self._t.get('history_export_csv', 'Export CSV'), command=self._export_history_csv)

    def _change_theme_to(self, name='Dark'):
        # PT: Altera o tema nas configurações e reinicia o app
        # EN: Change theme in settings and reload the app
        # FR: Change le thème dans les paramètres et recharge l'application
        self.settings['current_theme'] = name
        with open('./app/settings/settings.json', 'w', encoding='utf-8') as outfile:
            json_dump(self.settings, outfile, indent=4, ensure_ascii=False)
        self._reload_app()

    def _create_buttons(self, master):
        # PT: Cria botões (visuais e bindings) - mesma lógica original
        # EN: Create buttons (visual & bindings) - same original logic
        # FR: Crée les boutons (visuel & liaisons) - même logique originale
        self.theme.setdefault('BTN_NUMERICO', {}).update(self.settings.get('global', {}))
        self.theme.setdefault('BTN_OPERADOR', {}).update(self.settings.get('global', {}))
        self.theme.setdefault('BTN_DEFAULT', {}).update(self.settings.get('global', {}))
        self.theme.setdefault('BTN_CLEAR', {}).update(self.settings.get('global', {}))

        # PT: Botões numéricos
        # EN: Numeric buttons
        # FR: Boutons numériques
        self._BTN_NUM_0 = tk.Button(master, text=0, cnf=self.theme['BTN_NUMERICO'])
        self._BTN_NUM_1 = tk.Button(master, text=1, cnf=self.theme['BTN_NUMERICO'])
        self._BTN_NUM_2 = tk.Button(master, text=2, cnf=self.theme['BTN_NUMERICO'])
        self._BTN_NUM_3 = tk.Button(master, text=3, cnf=self.theme['BTN_NUMERICO'])
        self._BTN_NUM_4 = tk.Button(master, text=4, cnf=self.theme['BTN_NUMERICO'])
        self._BTN_NUM_5 = tk.Button(master, text=5, cnf=self.theme['BTN_NUMERICO'])
        self._BTN_NUM_6 = tk.Button(master, text=6, cnf=self.theme['BTN_NUMERICO'])
        self._BTN_NUM_7 = tk.Button(master, text=7, cnf=self.theme['BTN_NUMERICO'])
        self._BTN_NUM_8 = tk.Button(master, text=8, cnf=self.theme['BTN_NUMERICO'])
        self._BTN_NUM_9 = tk.Button(master, text=9, cnf=self.theme['BTN_NUMERICO'])

        # PT: Botões operadores
        # EN: Operator buttons
        # FR: Boutons opérateurs
        self._BTN_SOMA = tk.Button(master, text='+', cnf=self.theme['BTN_OPERADOR'])
        self._BTN_SUB = tk.Button(master, text='-', cnf=self.theme['BTN_OPERADOR'])
        self._BTN_DIV = tk.Button(master, text='/', cnf=self.theme['BTN_OPERADOR'])
        self._BTN_MULT = tk.Button(master, text='*', cnf=self.theme['BTN_OPERADOR'])
        self._BTN_EXP = tk.Button(master, text='^', cnf=self.theme['BTN_OPERADOR'])
        self._BTN_RAIZ = tk.Button(master, text='√', cnf=self.theme['BTN_OPERADOR'])

        # PT: Botões de função
        # EN: Function buttons
        # FR: Boutons fonctionnels
        self._BTN_ABRE_PARENTESE = tk.Button(master, text='(', cnf=self.theme['BTN_DEFAULT'])
        self._BTN_FECHA_PARENTESE = tk.Button(master, text=')', cnf=self.theme['BTN_DEFAULT'])
        self._BTN_CLEAR = tk.Button(master, text='C', cnf=self.theme['BTN_DEFAULT'])
        self._BTN_DEL = tk.Button(master, text='<', cnf=self.theme['BTN_CLEAR'])
        self._BTN_RESULT = tk.Button(master, text='=', cnf=self.theme['BTN_OPERADOR'])
        self._BTN_DOT = tk.Button(master, text='.', cnf=self.theme['BTN_DEFAULT'])

        # PT: Botões vazios (futuro)
        # EN: Empty buttons (future)
        # FR: Boutons vides (futur)
        self._BTN_VAZIO1 = tk.Button(master, text='', cnf=self.theme['BTN_OPERADOR'])
        self._BTN_VAZIO2 = tk.Button(master, text='', cnf=self.theme['BTN_OPERADOR'])

        # PT: Posicionamento em grid
        # EN: Grid placement
        # FR: Placement en grille
        self._BTN_CLEAR.grid(row=0, column=0, padx=1, pady=1)
        self._BTN_ABRE_PARENTESE.grid(row=0, column=1, padx=1, pady=1)
        self._BTN_FECHA_PARENTESE.grid(row=0, column=2, padx=1, pady=1)
        self._BTN_DEL.grid(row=0, column=3, padx=1, pady=1)

        self._BTN_NUM_7.grid(row=1, column=0, padx=1, pady=1)
        self._BTN_NUM_8.grid(row=1, column=1, padx=1, pady=1)
        self._BTN_NUM_9.grid(row=1, column=2, padx=1, pady=1)
        self._BTN_MULT.grid(row=1, column=3, padx=1, pady=1)

        self._BTN_NUM_4.grid(row=2, column=0, padx=1, pady=1)
        self._BTN_NUM_5.grid(row=2, column=1, padx=1, pady=1)
        self._BTN_NUM_6.grid(row=2, column=2, padx=1, pady=1)
        self._BTN_SUB.grid(row=2, column=3, padx=1, pady=1)

        self._BTN_NUM_1.grid(row=3, column=0, padx=1, pady=1)
        self._BTN_NUM_2.grid(row=3, column=1, padx=1, pady=1)
        self._BTN_NUM_3.grid(row=3, column=2, padx=1, pady=1)
        self._BTN_SOMA.grid(row=3, column=3, padx=1, pady=1)

        self._BTN_DOT.grid(row=4, column=0, padx=1, pady=1)
        self._BTN_NUM_0.grid(row=4, column=1, padx=1, pady=1)
        self._BTN_RESULT.grid(row=4, column=2, padx=1, pady=1)
        self._BTN_DIV.grid(row=4, column=3, padx=1, pady=1)

        self._BTN_VAZIO1.grid(row=5, column=0, padx=1, pady=1)
        self._BTN_VAZIO2.grid(row=5, column=1, padx=1, pady=1)
        self._BTN_EXP.grid(row=5, column=2, padx=1, pady=1)
        self._BTN_RAIZ.grid(row=5, column=3, padx=1, pady=1)

        # PT: Bindings / comandos dos botões
        # EN: Buttons bindings / commands
        # FR: Liaisons des boutons / commandes
        self._BTN_NUM_0['command'] = partial(self._set_values_in_input, 0)
        self._BTN_NUM_1['command'] = partial(self._set_values_in_input, 1)
        self._BTN_NUM_2['command'] = partial(self._set_values_in_input, 2)
        self._BTN_NUM_3['command'] = partial(self._set_values_in_input, 3)
        self._BTN_NUM_4['command'] = partial(self._set_values_in_input, 4)
        self._BTN_NUM_5['command'] = partial(self._set_values_in_input, 5)
        self._BTN_NUM_6['command'] = partial(self._set_values_in_input, 6)
        self._BTN_NUM_7['command'] = partial(self._set_values_in_input, 7)
        self._BTN_NUM_8['command'] = partial(self._set_values_in_input, 8)
        self._BTN_NUM_9['command'] = partial(self._set_values_in_input, 9)

        self._BTN_SOMA['command'] = partial(self._set_operator_in_input, '+')
        self._BTN_SUB['command'] = partial(self._set_operator_in_input, '-')
        self._BTN_MULT['command'] = partial(self._set_operator_in_input, '*')
        self._BTN_DIV['command'] = partial(self._set_operator_in_input, '/')
        self._BTN_EXP['command'] = partial(self._set_operator_in_input, '**')
        self._BTN_RAIZ['command'] = partial(self._set_operator_in_input, '**(1/2)')

        self._BTN_DOT['command'] = partial(self._set_dot_in_input, '.')
        self._BTN_ABRE_PARENTESE['command'] = self._set_open_parent
        self._BTN_FECHA_PARENTESE['command'] = self._set_close_parent
        self._BTN_DEL['command'] = self._del_last_value_in_input
        self._BTN_CLEAR['command'] = self._clear_input
        self._BTN_RESULT['command'] = self._evaluate_and_display

    def _localized_error(self):
        # PT: Retorna o texto de erro localizado para o idioma atual
        # EN: Return localized error text for current language
        # FR: Retourne le texte d'erreur localisé pour la langue actuelle
        return translations.get(self.current_language, translations.get('en', {})).get('error', 'Error')

    def _is_entry_error(self):
        # PT: Verifica se o conteúdo do campo é a mensagem de erro localizada
        # EN: Check whether the entry content is the localized error message
        # FR: Vérifie si le contenu de l'entrée est le message d'erreur localisé
        return self._entrada.get() == self._localized_error()

    def _insert_value_safe(self, value):
        # PT: Helper para inserir valores numéricos (interno)
        # EN: Helper to insert numeric values (internal)
        # FR: Fonction d'aide pour insérer des valeurs numériques (interne)
        if self._is_entry_error():
            self._entrada.delete(0, len(self._entrada.get()))

        if self._entrada.get() == '0':
            self._entrada.delete(0)
            self._entrada.insert(0, value)
        elif self._lenght_max(self._entrada.get()):
            self._entrada.insert(len(self._entrada.get()), value)

    def _set_values_in_input(self, value):
        # PT: Wrapper mantido para compatibilidade de nomes
        # EN: Wrapper kept for name compatibility
        # FR: Wrapper conservé pour compatibilité des noms
        self._insert_value_safe(value)

    def _set_dot_in_input(self, dot):
        # PT: Inserir separador decimal
        # EN: Insert decimal separator
        # FR: Insérer le séparateur décimal
        if self._is_entry_error():
            return
        if self._entrada.get() and self._entrada.get()[-1] not in '.+-/*' and self._lenght_max(self._entrada.get()):
            self._entrada.insert(len(self._entrada.get()), dot)

    def _set_open_parent(self):
        # PT: Inserir parêntese de abertura no input
        # EN: Insert opening parenthesis into input
        # FR: Insérer une parenthèse ouvrante dans l'entrée
        if self._is_entry_error():
            return
        if self._entrada.get() == '0':
            self._entrada.delete(0)
            self._entrada.insert(len(self._entrada.get()), '(')
        elif self._entrada.get() and self._entrada.get()[-1] in '+-/*' and self._lenght_max(self._entrada.get()):
            self._entrada.insert(len(self._entrada.get()), '(')

    def _set_close_parent(self):
        # PT: Inserir parêntese de fechamento no input
        # EN: Insert closing parenthesis into input
        # FR: Insérer une parenthèse fermante dans l'entrée
        if self._is_entry_error():
            return
        if self._entrada.get().count('(') <= self._entrada.get().count(')'):
            return
        if self._entrada.get() and self._entrada.get()[-1] not in '+-/*(' and self._lenght_max(self._entrada.get()):
            self._entrada.insert(len(self._entrada.get()), ')')

    def _clear_input(self):
        # PT: Limpa o input e insere '0'
        # EN: Clear the input and insert '0'
        # FR: Efface l'entrée et insère '0'
        self._entrada.delete(0, len(self._entrada.get()))
        self._entrada.insert(0, 0)

    def _del_last_value_in_input(self):
        # PT: Apaga o último caractere do input
        # EN: Delete the last character from the input
        # FR: Supprime le dernier caractère de l'entrée
        if self._is_entry_error():
            return
        if len(self._entrada.get()) == 1:
            self._entrada.delete(0)
            self._entrada.insert(0, 0)
        else:
            self._entrada.delete(len(self._entrada.get()) - 1)

    def _set_operator_in_input(self, operator):
        # PT: Inserir operador matemático no input (evita repetições)
        # EN: Insert math operator into input (prevents repeats)
        # FR: Insère un opérateur mathématique dans l'entrée (évite les répétitions)
        if self._is_entry_error():
            return
        if self._entrada.get() == '':
            return
        if self._entrada.get()[-1] not in '+-*/' and self._lenght_max(self._entrada.get()):
            self._entrada.insert(len(self._entrada.get()), operator)

    def _evaluate_and_display(self):
        # PT: Avalia expressão e exibe resultado; localiza mensagens de erro
        # EN: Evaluate expression and display result; localize error messages
        # FR: Évaluer l'expression et afficher le résultat ; localiser les messages d'erreur
        if self._is_entry_error():
            return
        expr = self._entrada.get()
        result = self.calc.calculation(expr)
        # PT: Se o core retornou sentinel neutral, exibe mensagem de erro localizada
        # EN: If core returned neutral sentinel, display localized error message
        # FR: Si le core a renvoyé un sentinel neutre, afficher le message d'erreur localisé
        if result == "__ERR__":
            self._set_result_in_input(result=self._localized_error())
        else:
            self._set_result_in_input(result=result)
            # append to history only if valid result
            try:
                if result is not None and result != "__ERR__":
                    self._append_history(expr, result)
            except Exception:
                pass

    def _set_result_in_input(self, result=0):
        # PT: Define o texto no input (inclui mensagens de erro localizadas)
        # EN: Set the text in the input (includes localized error messages)
        # FR: Définit le texte dans l'entrée (inclut les messages d'erreur localisés)
        self._entrada.delete(0, len(self._entrada.get()))
        self._entrada.insert(0, result)

    def _lenght_max(self, data_in_input):
        # PT: Verifica se o input atingiu o número máximo de caracteres
        # EN: Check whether the input reached the maximum number of characters
        # FR: Vérifie si l'entrée a atteint le nombre maximal de caractères
        if len(str(data_in_input)) >= 15:
            return False
        return True

    # ---------- History utilities ----------
    def _history_file_path(self):
        return './app/settings/history.json'

    def _load_history(self):
        try:
            with open(self._history_file_path(), mode='r', encoding='utf-8') as f:
                import json as _json
                data = _json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except FileNotFoundError:
            return []
        except Exception:
            return []

    def _save_history(self):
        try:
            with open(self._history_file_path(), mode='w', encoding='utf-8') as f:
                import json as _json
                _json.dump(self._history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _append_history(self, expr, result):
        try:
            entry = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'expression': str(expr),
                'result': str(result),
            }
            self._history.append(entry)
            if len(self._history) > 200:
                self._history = self._history[-200:]
            self._save_history()
        except Exception:
            pass

    def _clear_history(self):
        self._history = []
        self._save_history()

    def _export_history_csv(self):
        try:
            path = './app/settings/history.csv'
            with open(path, mode='w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow([self._t.get('history_col_time', 'time'),
                            self._t.get('history_col_expression', 'expression'),
                            self._t.get('history_col_result', 'result')])
                for e in self._history:
                    w.writerow([e.get('time', ''), e.get('expression', ''), e.get('result', '')])
            self._flash_info(self._t.get('export_success_title', 'Export successful'),
                             self._t.get('export_success_msg', f'Exported to {path}'))
        except Exception as e:
            self._flash_info(self._t.get('export_error_title', 'Export error'),
                             str(e))

    def _flash_info(self, title, message):
        try:
            top = tk.Toplevel(self.master)
            top.title(title)
            tk.Label(top, text=message, padx=12, pady=8).pack()
            tk.Button(top, text=self._t.get('ok', 'OK'), command=top.destroy).pack(pady=6)
            top.resizable(False, False)
        except Exception:
            pass

    def _show_history(self):
        win = tk.Toplevel(self.master)
        win.title(self._t.get('history_window_title', 'History'))
        win.geometry('360x420')
        frame = tk.Frame(win, bg=self.theme.get('frame_bg', '#ffffff'))
        frame.pack(fill='both', expand=True)
        listbox = tk.Listbox(frame)
        listbox.pack(fill='both', expand=True, padx=8, pady=8)
        for e in self._history:
            listbox.insert('end', f"{e.get('time','')}  |  {e.get('expression','')} = {e.get('result','')}")
        def copy_selected_to_input(event=None):
            try:
                sel = listbox.get(listbox.curselection())
                if '|' in sel and '=' in sel:
                    expr = sel.split('|',1)[1].split('=',1)[0].strip()
                    self._entrada.delete(0, len(self._entrada.get()))
                    self._entrada.insert(0, expr)
            except Exception:
                pass
        listbox.bind('<Double-Button-1>', copy_selected_to_input)
        btns = tk.Frame(win)
        btns.pack(fill='x', padx=8, pady=8)
        tk.Button(btns, text=self._t.get('history_copy_btn', 'Copy to input'), command=copy_selected_to_input).pack(side='left')
        tk.Button(btns, text=self._t.get('close', 'Close'), command=win.destroy).pack(side='right')
        win.resizable(False, False)

    # ---------- End history utilities ----------

    def start(self):
        # PT: Mensagem exibida no terminal quando a calculadora inicia
        # EN: Message printed to terminal when calculator starts
        # FR: Message affichée dans le terminal lorsque la calculatrice démarre
        print(self._t.get('start_message', 'Calculator started...'))
        self.master.mainloop()

    def _reload_app(self):
        # PT: Reinicia o aplicativo executando o mesmo processo Python
        # EN: Reload the app by exec'ing the Python process
        # FR: Recharge l'application en exécutant à nouveau le processus Python
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def _realod_app(self):
        # PT: Nome legado mantido (chama o reload real)
        # EN: Legacy name kept (calls the real reload)
        # FR: Nom hérité conservé (appelle le vrai rechargement)
        self._reload_app()

    def _exit(self):
        # PT: Sai da aplicação
        # EN: Exit the application
        # FR: Quitter l'application
        exit()

    def _change_language(self, lang_code):
        # PT: Escreve a escolha no settings e reinicia para aplicar o novo idioma
        # EN: Write choice to settings and restart to apply the new language
        # FR: Écrit le choix dans les paramètres et redémarre pour appliquer la nouvelle langue
        self.settings['current_language'] = lang_code
        with open('./app/settings/settings.json', 'w', encoding='utf-8') as outfile:
            json_dump(self.settings, outfile, indent=4, ensure_ascii=False)
        self._reload_app()
