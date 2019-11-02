#-------------------------------------------------------------------------------
# Name:        1_FOOTPRINTS.py
# Purpose:     Este script importa entidades del catastro de un municipio y las
#               convierte en entidades utiles para el analisis morfologico
#
# Author:      David Pereira-Martinez (david.pereira@udc.es)
#
# Created:     15/10/2019
# Licence:     (CC BY-NC 2.0)
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()

# import system modules
import arcpy
from arcpy import env
import os
import shutil
arcpy.env.overwriteOutput = True

#Aqui se define la carpeta que va a contener las carpetas "RUSTICO" y "URBANO" con los shapefiles, el archivo conversor "ALTURAS.dbf"
root = "d:\\carpeta"
env.workspace = root
auxiliar = root + "\\AUXILIAR"
os.mkdir(auxiliar)

#Aqui se crea una nueva capa de PARCELAS privadas y de DOMinioPUBlico
#En la capa de DOMinioPUBlico se borran las entidades menores de 1m2 (basura)
arcpy.Erase_analysis("RUSTICO\\PARCELA.shp", "URBANO\\PARCELA.shp","AUXILIAR\\RECORTE.shp")

arcpy.Merge_management(["URBANO\\PARCELA.shp", "AUXILIAR\\RECORTE.shp"], "AUXILIAR\\PARCELA_.shp")

clause = "TIPO='X'"
arcpy.Select_analysis("AUXILIAR\\PARCELA_.shp", "AUXILIAR\\DOMPUB_.shp", clause)

arcpy.MultipartToSinglepart_management ("AUXILIAR\\DOMPUB_.shp", "AUXILIAR\\DOMPUB_2.shp")
arcpy.CalculateAreas_stats("AUXILIAR\\DOMPUB_2.shp", "AUXILIAR\\DOMPUB_3.shp")
clause = "F_AREA > 1"
arcpy.Select_analysis("AUXILIAR\\DOMPUB_3.shp", "AUXILIAR\\DOMPUB_4.shp", clause)
arcpy.Dissolve_management("AUXILIAR\\DOMPUB_4.shp", "AUXILIAR\\DOMPUB_5.shp")
arcpy.MultipartToSinglepart_management ("AUXILIAR\\DOMPUB_5.shp", "DOMPUB")

clause = "TIPO<>'X'"
arcpy.Select_analysis("AUXILIAR\\PARCELA_.shp", "PARCELA.shp", clause)

#EQUIVALENCIA A LA DESCRIPCION DE ALTURAS DEL CATASTRO
#Existen tienen variaciones entre las categorias de alturas de los municipios
arcpy.Merge_management(["URBANO\\CONSTRU.shp", "RUSTICO\\CONSTRU.shp"], "AUXILIAR\\CONSTRU_.shp")

clause = "NUMSYMBOL <13"
arcpy.Select_analysis("AUXILIAR\\CONSTRU_.shp", "AUXILIAR\\CONSTRU_2.shp", clause)

arcpy.JoinField_management("AUXILIAR\\CONSTRU_2.shp", "CONSTRU", "_ALTURAS.dbf", "CONSTRU",
                           ["SOTOS", "BAIXA", "ALTAS"])

#Aqui se crea una nueva capa CONSTRU, sin suelo y otras no-construcciones (sin disolver)
clause = "SOTOS<>0 OR BAIXA<>0 OR ALTAS<>0"
arcpy.Select_analysis("AUXILIAR\\CONSTRU_2.shp", "CONSTRU.shp", clause)

#Aqui se crea una nueva capa plantas SOTANO (disuelta por REFerenciaCATastral)
arcpy.Select_analysis("AUXILIAR\\CONSTRU_2.shp", "AUXILIAR\\SOTOS_.shp", "SOTOS<>0")
arcpy.Dissolve_management("AUXILIAR\\SOTOS_.shp", "SOTOS.shp","REFCAT", [["AREA", "SUM"]], "SINGLE_PART")

#Aqui se crea una nueva capa plantas ALTAS (disuelta por REFerenciaCATastral)
clause = "NUMSYMBOL <12"
arcpy.Select_analysis("AUXILIAR\\CONSTRU_2.shp", "AUXILIAR\\CONSTRU_3.shp", clause)
arcpy.Select_analysis("AUXILIAR\\CONSTRU_3.shp", "AUXILIAR\\ALTAS_.shp", "ALTAS<>0")
arcpy.Dissolve_management("AUXILIAR\\ALTAS_.shp", "ALTAS.shp","REFCAT", [["AREA", "SUM"]], "SINGLE_PART")

#Aqui se crea una nueva capa plantas bajas BAIXOS (disuelta por REFerenciaCATastral)
arcpy.Erase_analysis("AUXILIAR\\CONSTRU_3.shp", "DOMPUB.shp", "AUXILIAR\\CONSTRU_4.shp")
arcpy.Select_analysis("AUXILIAR\\CONSTRU_4.shp", "AUXILIAR\\BAIXOS_.shp", "BAIXA<>0")
arcpy.Dissolve_management("AUXILIAR\\BAIXOS_.shp", "BAIXOS.shp","REFCAT", [["AREA", "SUM"]], "SINGLE_PART")


#Aqui se exportan las 5 capas a CAD con los mismos nombres
arcpy.ExportCAD_conversion("ALTAS.shp", "DWG_R2010", "ALTAS.dwg", "USE_FILENAMES_IN_TABLES")
arcpy.ExportCAD_conversion("BAIXOS.shp", "DWG_R2010", "BAIXOS.dwg", "USE_FILENAMES_IN_TABLES")
arcpy.ExportCAD_conversion("CONSTRU.shp", "DWG_R2010", "CONSTRU.dwg", "USE_FILENAMES_IN_TABLES")
arcpy.ExportCAD_conversion("DOMPUB.shp", "DWG_R2010", "DOMPUB.dwg", "USE_FILENAMES_IN_TABLES")
arcpy.ExportCAD_conversion("PARCELA.shp", "DWG_R2010", "PARCELA.dwg", "USE_FILENAMES_IN_TABLES")


#Por ultimo se borran las capas auxiliares utilizadas
shutil.rmtree(auxiliar)


