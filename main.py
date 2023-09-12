"""Modulos que proveen las funciones que requiere el script."""
import argparse
import os
import re
import csv
from pathlib import Path
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pypdf import PdfReader

# El formato que uso es unica y exclusivamente para
# importar posteriormente en la herramienta evo factupronto
datos_csf = {'nombre': '',
             'codigo': '',
             'rfc': '',
             'regimenfiscal': '',
             'formadepago': '',
             'metododepago': '',
             'telefono': '',
             'email': '',
             'calle': '',
             'numexterior': '',
             'numinterior': '',
             'pais': '',
             'codigopostal': '',
             'estado': '',
             'ciudadmunicipio': '',
             'localidad': '',
             'colonia': '',
             'cuentacontableingresos': '',
             'cuentacontabledeprovision': ''
            }

# TODO: frantizek
#       Quitar las estructuras o constantes y usar un solo archivo de referencia

CFDI_4 = {
    'RÉGIMEN GENERAL DE LEY PERSONAS MORALES': 601,
    'PERSONAS MORALES CON FINES NO LUCRATIVOS': 603,
    'SUELDOS Y SALARIOS E INGRESOS ASIMILADOS A SALARIOS': 605,
    'RÉGIMEN DE SUELDOS Y SALARIOS E INGRESOS ASIMILADOS A SALARIOS': 605,
    'ARRENDAMIENTO': 606,
    'RÉGIMEN DE ENAJENACIÓN O ADQUISICIÓN DE BIENES': 607,
    'DEMÁS INGRESOS': 608,
    'RESIDENTES EN EL EXTRANJERO SIN ESTABLECIMIENTO PERMANENTE EN MÉXICO': 610,
    'INGRESOS POR DIVIDENDOS (SOCIOS Y ACCIONISTAS)': 611,
    'RÉGIMEN DE LAS PERSONAS FÍSICAS CON ACTIVIDADES EMPRESARIALES Y PROFESIONALES': 612,
    'INGRESOS POR INTERESES': 614,
    'RÉGIMEN DE LOS INGRESOS POR OBTENCIÓN DE PREMIOS': 615,
    'SIN OBLIGACIONES FISCALES': 616,
    'SOCIEDADES COOPERATIVAS DE PRODUCCIÓN QUE OPTAN POR DIFERIR SUS INGRESOS': 620,
    'INCORPORACIÓN FISCAL': 621,
    'RÉGIMEN DE INCORPORACIÓN FISCAL': 621,
    'ACTIVIDADES AGRÍCOLAS, GANADERAS, SILVÍCOLAS Y PESQUERAS': 622,
    'OPCIONAL PARA GRUPOS DE SOCIEDADES': 623,
    'COORDINADOS': 624,
    'RÉGIMEN DE LAS ACTIVIDADES EMPRESARIALES CON INGRESOS A TRAVÉS DE PLATAFORMAS TECNOLÓGICAS': 625,
    'RÉGIMEN SIMPLIFICADO DE CONFIANZA': 626
}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_info(path):
    """Obtiene la cantidad de paginas del PDF.
       Validando con esto que por lo menos sea un archivo PDF valido."""
    with open(path, 'rb') as f:
        pdf = PdfReader(f)
        if len(pdf.pages) > 0:
            print(len(pdf.pages))
            return True
        else:
            return False

def eliminar_elementos_vacios_y_con_pagina(lista):
    """Elimina los elementos vacios de la lista.
       Tambien busca los elementos que contienen la palabra
       PAGINA y los quita."""
    nueva_lista = []
    for item in lista:
        if item and "Página" not in item:
            nueva_lista.append(item)
    return nueva_lista


def extraer_numero_consecutivo(archivo):
    """Extrae el numero almacenado en el archivo."""
    with open(archivo, "r") as f:
        numero = int(f.read())
    return numero


def decrementar_numero(numero):
    """Decrementa el numero en una unidad."""
    return numero - 1


def guardar_numero(archivo, numero):
    """Guarda el numero con el nuevo valor en el archivo."""
    with open(archivo, "w") as f:
        f.write(str(numero))


class PdfConverter:

    def __init__(self, file_path):
        self.file_path = file_path

    # convert pdf file to a string which has space among words
    def convert_pdf_to_txt(self):
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'  # 'utf16','utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = open(self.file_path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                      password=password, caching=caching,
                                      check_extractable=True):
            interpreter.process_page(page)
        fp.close()
        device.close()
        str = retstr.getvalue()
        retstr.close()
        return str

def extract_info_from_pdf(current_CSF):
    pdfConverter = PdfConverter(current_CSF)

    current_pdf = pdfConverter.convert_pdf_to_txt().replace(
        "\n\n", "\n").replace("\x0c", "").split("\n")
    new_list = eliminar_elementos_vacios_y_con_pagina(current_pdf)

    current_pdf.clear()

    is_persona_moral = True

    UPPER_list = [x.upper() for x in new_list]
    new_list.clear()

    if [s for s in UPPER_list if "SEGUNDO APELLIDO:" in s]:
        is_persona_moral = False

    # Is there a better way to clean this data structure???
    for k in datos_csf:
        datos_csf[k] = ''

    # Datos comunes, no importa si el regimen fiscal es persona fisica o cualquier otro
    datos_csf['pais'] = 'MÉXICO'
    datos_csf['formadepago'] = 99
    datos_csf['metododepago'] = 'PPD'

    # Nombre de la Constancia de Situacion Fiscal es indiferente al tipo de persona
    if UPPER_list.index('NOMBRE, DENOMINACIÓN O RAZÓN ') - UPPER_list.index(
            'REGISTRO FEDERAL DE CONTRIBUYENTES') == 2:
        datos_csf['nombre'] = UPPER_list[UPPER_list.index(
            'NOMBRE, DENOMINACIÓN O RAZÓN ') - 1].upper()
    elif UPPER_list.index('NOMBRE, DENOMINACIÓN O RAZÓN ') - UPPER_list.index(
            'REGISTRO FEDERAL DE CONTRIBUYENTES') > 2:
        partial_name = ""
        for name_counter in range(UPPER_list.index('REGISTRO FEDERAL DE CONTRIBUYENTES') + 1,
                                  (UPPER_list.index('NOMBRE, DENOMINACIÓN O RAZÓN '))):
            partial_name = partial_name + UPPER_list[name_counter].upper()
        datos_csf['nombre'] = partial_name

    datos_csf['codigopostal'] = int(
        re.findall(r'\d+', [s for s in UPPER_list if "CÓDIGO POSTAL:" in s][0])[0])

    archivo = "dnt_consecutivo_latest.txt"

    numero = extraer_numero_consecutivo(archivo)
    numero = decrementar_numero(numero)
    guardar_numero(archivo, numero)
    datos_csf['codigo'] = "dnt" + str(numero)

    datos_csf['estado'] = re.search('NOMBRE DE LA ENTIDAD FEDERATIVA: (.*)',
                                    [s for s in UPPER_list if "NOMBRE DE LA ENTIDAD FEDERATIVA: " in s]
                                    [0]).group(1).upper()
    datos_csf['colonia'] = re.search('NOMBRE DE LA COLONIA: (.*)',
                                     [s for s in UPPER_list if 'NOMBRE DE LA COLONIA: '
                                      in s][0]).group(1).upper()
    datos_csf['localidad'] = re.search('NOMBRE DE LA LOCALIDAD:(.*)',
                                       [s for s in UPPER_list if 'NOMBRE DE LA LOCALIDAD:'
                                        in s][0]).group(1).upper().lstrip()
    datos_csf['ciudadmunicipio'] = re.search('NOMBRE DEL MUNICIPIO O DEMARCACIÓN TERRITORIAL: (.*)',
                                             [s for s in UPPER_list if
                                              'NOMBRE DEL MUNICIPIO O DEMARCACIÓN TERRITORIAL: '
                                              in s][0]).group(1).upper()

    datos_csf['calle'] = re.search('NOMBRE DE VIALIDAD: (.*)',
                                   [s for s in UPPER_list
                                    if 'NOMBRE DE VIALIDAD: ' in s][0]).group(1)
    datos_csf['numexterior'] = re.search('NÚMERO EXTERIOR:(.*)',
                                         [s for s in UPPER_list if 'NÚMERO EXTERIOR:'
                                          in s][0]).group(1).lstrip()
    datos_csf['numinterior'] = re.search('NÚMERO INTERIOR:(.*)',
                                         [s for s in UPPER_list
                                          if 'NÚMERO INTERIOR:'
                                          in s][0]).group(1)

    if is_persona_moral:

        if UPPER_list[1] == UPPER_list[UPPER_list.index(
                'DATOS DE IDENTIFICACIÓN DEL CONTRIBUYENTE: ') - 1] \
                and \
                UPPER_list[1] == UPPER_list[UPPER_list.index(
            'DENOMINACIÓN/RAZÓN SOCIAL:') - 1]:
            datos_csf['rfc'] = UPPER_list[1]
        if UPPER_list.index('RÉGIMEN') - UPPER_list.index('REGÍMENES:  ') == 2:
            datos_csf['regimenfiscal'] = CFDI_4[UPPER_list[UPPER_list.index(
                'RÉGIMEN') - 1].upper()]
        elif UPPER_list.index('RÉGIMEN') - UPPER_list.index('REGÍMENES:  ') > 2:
            # aparentemente hay algunas CSF que tienen mucho historial
            # en cuanto a los regimenes que han usado
            # por lo que hay que tener en cuenta que pueden ser muchas lineas
            datos_csf['regimenfiscal'] = CFDI_4[UPPER_list[UPPER_list.index(
                'RÉGIMEN') + 3].upper()]
        else:
            datos_csf['regimenfiscal'] = CFDI_4[UPPER_list[UPPER_list.index(
                'RÉGIMEN') + 1].upper()]
    else:
        if UPPER_list[1] == UPPER_list[UPPER_list.index(
                'DATOS DE IDENTIFICACIÓN DEL CONTRIBUYENTE: ') - 1] and \
                UPPER_list[1] == UPPER_list[UPPER_list.index(
            'SEGUNDO APELLIDO:') + 1]:
            datos_csf['rfc'] = UPPER_list[1]
        if UPPER_list.index('RÉGIMEN') - UPPER_list.index('REGÍMENES:  ') == 2:
            datos_csf['regimenfiscal'] = CFDI_4[UPPER_list[UPPER_list.index(
                'RÉGIMEN') - 1].upper()]
        else:
            datos_csf['regimenfiscal'] = CFDI_4[UPPER_list[UPPER_list.index(
                'RÉGIMEN') + 1].upper()]

    # Al momento no hay absolutamente NADA que garantize
    # que los datos de telefono o correo esten presentes
    # por lo que ahorita no creo que sea necesario incorporarlos

    print(datos_csf)
    if datos_csf['email'] == '':
        print(f"{bcolors.WARNING}ADVERTENCIA: El campo 'email' esta vacio. "
              f"Se requiere llenar manualmente.{bcolors.ENDC}")

    if os.path.exists('plantilla_clientes.csv'):
        plantilla_creada = True
    else:
        plantilla_creada = False

    with open('plantilla_clientes.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if not plantilla_creada:
            field = ["Nombre",
                     "Codigo",
                     "RFC",
                     "Regimenfiscal",
                     "FormadePago",
                     "MetododePago",
                     "Telefono",
                     "Email",
                     "Calle",
                     "NumExterior",
                     "NumInterior",
                     "Pais",
                     "CodigoPostal",
                     "Estado",
                     "CiudadMunicipio",
                     "Localidad",
                     "Colonia",
                     "CuentacontableIngresos",
                     "CuentacontabledeProvision"]
            writer.writerow(field)
        writer.writerow([
            datos_csf['nombre'],
            datos_csf["codigo"],
            datos_csf["rfc"],
            datos_csf["regimenfiscal"],
            datos_csf["formadepago"],
            datos_csf["metododepago"],
            datos_csf["telefono"],
            datos_csf["email"],
            datos_csf["calle"],
            datos_csf["numexterior"],
            datos_csf["numinterior"],
            datos_csf["pais"],
            datos_csf["codigopostal"],
            datos_csf["estado"],
            datos_csf["ciudadmunicipio"],
            datos_csf["localidad"],
            datos_csf["colonia"],
            datos_csf["cuentacontableingresos"],
            datos_csf["cuentacontabledeprovision"]
        ])


def main():
    parser = argparse.ArgumentParser(description="Extractor de datos de un PDF con la Constancia de Situacion Fiscal",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-a", "--archivo",
                         action="store_true", help="Procesa un solo archivo")
    parser.add_argument("-d", "--directorio", action="store_true",
                         help="Procesa todos los archivos dentro de un directorio")
    parser.add_argument("src", help="Nombre del archivo o directorio a procesar")
    args = parser.parse_args()
    config = vars(args)

    if args.directorio and os.path.isdir(args.src):
        target_dir = Path(args.src)
        for entry in target_dir.iterdir():
            extract_info_from_pdf(os.path.join(args.src, entry.name))
    elif args.archivo and os.path.exists(args.src):
        if os.path.getsize(args.src) > 0:
            if not get_info(args.src):
                raise SystemExit(1)
            else:
                extract_info_from_pdf(args.src)
    else:
        print("El directorio o archivo no existe, favor de verificar.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
