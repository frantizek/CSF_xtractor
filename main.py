import re
import random
from pypdf import PdfReader

reader = PdfReader("example.pdf")

'''
El formato que se usa es unica y exclusivamente para evo factupronto
'''
datos_csf = { 'nombre': '', 'codigo': '', 'rfc': '', 'regimenfiscal': '', 'formadepago': '', 'metododepago': '',
              'telefono': '', 'email': '', 'calle': '', 'numexterior': '', 'numinterior': '', 'pais': '',
              'codigopostal': '', 'estado': '', 'ciudadmunicipio': '', 'localidad': '', 'colonia': '',
              'cuentacontableingresos': '', 'cuentacontabledeprovision': ''
            }
'''
En teoria, ya no se va a estar usando del formato cfdi 3.3 
por el momento dejo comentada esta seccion

TODO: frantizek
quitar las estructuras o constantes y usar un solo archivo de referencia

CFDI_3_3 = {
                601: 'General de Ley Personas Morales',
                603: 'Personas Morales con Fines no Lucrativos',
                605: 'Sueldos y Salarios e Ingresos Asimilados a Salarios',
                606: 'Arrendamiento',
                607: 'Régimen de Enajenación o Adquisición de Bienes',
                608: 'Demás ingresos',
                609: 'Consolidación',
                610: 'Residentes en el Extranjero sin Establecimiento Permanente en México',
                611: 'Ingresos por Dividendos (socios y accionistas)',
                612: 'Personas Físicas con Actividades Empresariales y Profesionales',
                614: 'Ingresos por intereses',
                615: 'Régimen de los ingresos por obtención de premios',
                616: 'Sin obligaciones fiscales',
                620: 'Sociedades Cooperativas de Producción que optan por diferir sus ingresos',
                621: 'Incorporación Fiscal',
                622: 'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras',
                623: 'Opcional para Grupos de Sociedades',
                624: 'Coordinados',
                625: 'Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas',
                626: 'Régimen Simplificado de Confianza',
                628: 'Hidrocarburos',
                629: 'De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales',
                630: 'Enajenación de acciones en bolsa de valores'
            }
'''

CFDI_4_0 = {
                601: 'General de Ley Personas Morales',
                603: 'Personas Morales con Fines no Lucrativos',
                605: 'Sueldos y Salarios e Ingresos Asimilados a Salarios',
                606: 'Arrendamiento',
                607: 'Régimen de Enajenación o Adquisición de Bienes',
                608: 'Demás ingresos',
                610: 'Residentes en el Extranjero sin Establecimiento Permanente en México',
                611: 'Ingresos por Dividendos (socios y accionistas)',
                612: 'Personas Físicas con Actividades Empresariales y Profesionales',
                614: 'Ingresos por intereses',
                615: 'Régimen de los ingresos por obtención de premios',
                616: 'Sin obligaciones fiscales',
                620: 'Sociedades Cooperativas de Producción que optan por diferir sus ingresos',
                621: 'Incorporación Fiscal',
                622: 'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras',
                623: 'Opcional para Grupos de Sociedades',
                624: 'Coordinados',
                625: 'Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas',
                626: 'Régimen Simplificado de Confianza'
            }

CFDI_4 = {
                'Régimen General de Ley Personas Morales' : 601,
                'Personas Morales con Fines no Lucrativos' : 603,
                'Sueldos y Salarios e Ingresos Asimilados a Salarios' : 605,
                'Arrendamiento' : 606,
                'Régimen de Enajenación o Adquisición de Bienes' : 607,
                'Demás ingresos' : 608,
                'Residentes en el Extranjero sin Establecimiento Permanente en México' : 610,
                'Ingresos por Dividendos (socios y accionistas)' : 611,
                'Régimen de las Personas Físicas con Actividades Empresariales y Profesionales' : 612,
                'Ingresos por intereses' : 614,
                'Régimen de los ingresos por obtención de premios' : 615,
                'Sin obligaciones fiscales' : 616,
                'Sociedades Cooperativas de Producción que optan por diferir sus ingresos' : 620,
                'Incorporación Fiscal' : 621,
                'Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras' : 622,
                'Opcional para Grupos de Sociedades' : 623,
                'Coordinados' : 624,
                'Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas' : 625,
                'Régimen Simplificado de Confianza' : 626
            }

'''
Variable para guardar todos los datos del PDF
'''
pdf_to_list_content = []

for page in reader.pages:
    text = page.extract_text()

    '''
    Se usa el caracter de nueva linea, para ir delimitando los datos
    '''
    xs = text.split("\n")

    '''
    El primer elemento del PDF suele ser el numero de pagina por lo que lo eliminamos
    '''
    if 'Página  [' in xs[0]:
        xs.pop(0)

    pdf_to_list_content.extend(xs)

'''
En este punto ya se tienen todos los datos del PDF en una lista, para poder separar los datos
'''
#print(pdf_to_list_content)

'''
El PDF de ejemplo me indica que despues de la seccion de Obligaciones, ya debo de tener todos los datos
que estoy buscando, por lo que elimino los elementos innecesarios
'''
reduced_list_content= pdf_to_list_content[:pdf_to_list_content.index('Obligaciones: ')]
reduced_list_content_1 = reduced_list_content[:reduced_list_content.index('Actividades Económicas: ')]
reduced_list_content_2 = reduced_list_content[reduced_list_content.index('Regímenes:  '):]

pdf_to_list_content.clear()

pdf_to_list_content.extend(reduced_list_content_1)
pdf_to_list_content.extend(reduced_list_content_2)

'''
TODO: frantizek
no usar los indices fijos
'''
if 'Registro Federal de Contribuyentes' in pdf_to_list_content[2] \
        and 'Nombre, denominación o razón ' in pdf_to_list_content[4]:
    datos_csf['nombre'] = pdf_to_list_content[3].upper()
datos_csf['rfc'] = [s for s in pdf_to_list_content if "RFC: " in s][0].split(": ")[1]
datos_csf['codigopostal'] = int(re.findall(r'\d+', [s for s in pdf_to_list_content if "CódigoPostal:" in s][0])[0])
datos_csf['codigo'] = "dnt" + str(random.randrange(900, 8000))



datos_csf['estado'] = re.search('Nombrede laEntidad Federativa:(.*) EntreCalle:',
                                [s for s in pdf_to_list_content if "Nombrede laEntidad Federativa:"
                                in s][0]).group(1).upper()
datos_csf['colonia'] = re.search('No mbrede laColonia:(.*)',
                                  [s for s in pdf_to_list_content if "No mbrede laColonia:"
                                  in s][0]).group(1).upper()
datos_csf['localidad'] = re.search('Nombrede laLocalidad:(.*) NombredelMunicipio o Demarcación Territorial:',
                                    [s for s in pdf_to_list_content if "Nombrede laLocalidad:"
                                    in s][0]).group(1).upper()
datos_csf['ciudadmunicipio'] = re.search('NombredelMunicipio o Demarcación Territorial:(.*)',
                                    [s for s in pdf_to_list_content if "NombredelMunicipio o Demarcación Territorial:"
                                    in s][0]).group(1).upper()
datos_csf['telefono'] = int(re.search('Tel.Fijo Lada:(.*) Número:', [s for s in pdf_to_list_content if "Tel.Fijo "
                                                                     in s][0]).group(1) + re.search(' Número:(.*)',
                                                                    [s for s in pdf_to_list_content if "Tel.Fijo "
                                                                    in s][0]).group(1))
datos_csf['email'] = re.search('CorreoElectrónico:(.*)', [s for s in pdf_to_list_content if "CorreoElectrónico:"
                                                          in s][0]).group(1).lower()
datos_csf['calle'] = re.search('NombredeVialidad:(.*) NúmeroExterior:', [s for s in pdf_to_list_content
                                                                         if "NombredeVialidad:" in s][0]).group(1)
datos_csf['numexterior'] = re.search('NúmeroExterior:(.*)', [s for s in pdf_to_list_content if "NúmeroExterior:"
                                                             in s][0]).group(1)
datos_csf['numinterior'] = re.search('NúmeroInterior:(.*) No mbrede laColonia:', [s for s in pdf_to_list_content
                                                                                  if "NúmeroInterior:"
                                                                                  in s][0]).group(1)

'''
Valores por default
'''
datos_csf['pais'] = 'MEXICO'
datos_csf['formadepago'] = 99
datos_csf['metododepago'] = 'PPD'
'''
TODO: frantizek
no usar los indices fijos
por la forma en que estoy guardando la lista ahorita se que es el ultimo elemento pero no deberia de depender de ello
'''
datos_csf['regimenfiscal'] = CFDI_4[re.split(r'(^\D+)', pdf_to_list_content[-1])[1:][0].rstrip()]

print(datos_csf)

import csv

with open('profiles1.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    field = ["Nombre", "Codigo", "RFC", "Regimenfiscal", "FormadePago", "MetododePago", "Telefono", "Email", "Calle",
             "NumExterior", "NumInterior", "Pais", "CodigoPostal", "Estado", "CiudadMunicipio", "Localidad", "Colonia",
             "CuentacontableIngresos", "CuentacontabledeProvision"]
    writer.writerow(field)
    writer.writerow([datos_csf['nombre'], datos_csf["codigo"], datos_csf["rfc"], datos_csf["regimenfiscal"], datos_csf["formadepago"], datos_csf["metododepago"], datos_csf["telefono"], datos_csf["email"], datos_csf["calle"], datos_csf["numexterior"], datos_csf["numinterior"], datos_csf["pais"], datos_csf["codigopostal"], datos_csf["estado"], datos_csf["ciudadmunicipio"], datos_csf["localidad"], datos_csf["colonia"],datos_csf["cuentacontableingresos"], datos_csf["cuentacontabledeprovision"]])