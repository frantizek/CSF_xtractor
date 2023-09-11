# Herramienta para obtener los datos basicos desde una Constancia de Situacion Fiscal 

## Descripcion del Proyecto

La herramienta debe de:

- Validar si hay un PDF valido del cual se puede extraer los datos fiscales
- Si es un PDF valido, obtener los siguientes datos:
   * Nombre
       - Campo Obligatorio
       - Cadena de caracteres de longitud variable
   * Codigo
       - Campo opcional
       - Definido por el usuario
       - Campo Obligatorio por Factupronto
   * RFC
       - Campo Obligatorio
   * Regimenfiscal
       - Campo Opcional
       - Se leen caracteres y se tiene que usar una tabla para guardar el codigo de tres digitos
   * FormadePago
       - Campo Opcional
       - Se leen caracteres y se tiene que usar una tabla para guardar el codigo de dos digitos
   * MetododePago
       - Campo Opcional
       - Se leen caracteres y se tiene que usar una tabla para guardar el codigo de tres caracteres
   * Telefono
       - Campo Opcional
       - Validar que sea un numero valido de 10 caracteres (en caso de que este dividido en dos por la clave lada, se tiene que concatenar lada + numero)
   * Email
       - Campo Opcional
       - Se leen caracteres y se tiene validar que sea una direccion de correo electronico valida
   * Calle
       - Campo Opcional
   * NumExterior
       - Campo Opcional
   * NumInterior
       - Campo Opcional
   * Pais
       - El unico valor posible es MEXICO 
   * CodigoPostal
       - Campo Obligatorio
       - Se leen caracteres y se tiene validar que sea un numero entre 00000 y 99999
   * Estado
       - Campo Opcional
   * Ciudad
       - Campo Opcional
   * Municipio
       - Campo Opcional
   * Localidad
       - Campo Opcional
   * Colonia
       - Campo Opcional
   * CuentacontableIngresos
       - Campo Opcional
       - No se posee informacion del tipo de dato
   * CuentacontabledeProvision
       - Campo Opcional
       - No se posee informacion del tipo de dato
- Se guardan los datos conforme a la plantilla de ejemplo con el formato de archivo xlsx

Se puede hacer esta lectura de datos de manera individual o se puede mandar como parametro un directorio que contenga varios PDFs y se agrega cada resultado como una nueva fila en el archivo xlsx.
