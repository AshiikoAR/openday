# -*- coding: utf-8 -*-

# @autor: Matheus Felipe
# @github: github.com/matheusfelipeog

class Calculador(object):
    # PT: Classe responsável por realizar todos os cálculos da calculadora
    # EN: Class responsible for performing all calculator computations
    # FR: Classe responsable d'effectuer tous les calculs de la calculatrice

    def calculation(self, calc):
        # PT: Responsável por receber o cálculo a ser realizado e retornar o resultado ou sentinel em erro
        # EN: Responsible for receiving the calculation and returning result or neutral error sentinel
        # FR: Responsable de recevoir le calcul et de retourner le résultat ou un sentinel d'erreur neutre
        return self.__calculation_validation(calc=calc)

    def __calculation_validation(self, calc):
        # PT: Valida se o cálculo informado pode ser realizado; retorna "__ERR__" em caso de falha
        # EN: Validate whether the given calculation can be performed; returns "__ERR__" on failure
        # FR: Valide si le calcul donné peut être effectué ; renvoie "__ERR__" en cas d'échec
        try:
            result = eval(calc)
            return self.__format_result(result=result)
        except (NameError, ZeroDivisionError, SyntaxError, ValueError):
            # PT: Retorna sentinel neutral em caso de erro (GUI fará a localização)
            # EN: Return neutral sentinel on error (GUI will localize)
            # FR: Retourne un sentinel neutre en cas d'erreur (l'interface localisera)
            return "__ERR__"

    def __format_result(self, result):
        # PT: Formata o resultado em notação científica se for muito grande e retorna string
        # EN: Format the result in scientific notation if too large and return as string
        # FR: Formate le résultat en notation scientifique s'il est trop grand et renvoie une chaîne
        result = str(result)
        if len(result) > 15:
            result = '{:5.5E}'.format(float(result))
        return result
