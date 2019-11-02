#-------------------------------------------------------------------------------
# Name:        2_ADJACENCIES_PARTY-WALLS.py
# Purpose:     Este script calcula las adyacencias de parcelas y edificios,
#               obteniendo de esta manera los linderos y medianeras respectivamente
#
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

#Aqui se define la carpeta que va a contener las carpetas "RUSTICO" y "URBANO" con los shapefiles
root = "d:\\carpeta"
env.workspace = root
auxiliar = root + "\\AUXILIAR"
os.mkdir(auxiliar)

#Se recortan los lindes y los frentes de parcela, corrigiendo algunos errores graficos
arcpy.FeatureToLine_management("PARCELA.shp", "AUXILIAR\\PARCELA_LINE.shp")
arcpy.Erase_analysis("AUXILIAR\\PARCELA_LINE.shp", "DOMPUB.shp", "AUXILIAR\\LINDEIROS_.shp")
arcpy.Dissolve_management("PARCELA.shp", "AUXILIAR\\MANZANAS_.shp")
arcpy.FeatureToLine_management("AUXILIAR\\MANZANAS_.shp", "AUXILIAR\\MANZANAS_FRONTE.shp")
arcpy.Buffer_analysis("DOMPUB.shp", "AUXILIAR\\DOMPUB_.shp", "0,01", "FULL", "ROUND", "ALL")
arcpy.Intersect_analysis (["AUXILIAR\\DOMPUB_.shp", "AUXILIAR\\MANZANAS_FRONTE.shp"], "AUXILIAR\\MANZANAS_FRONTE2", "ALL", "", "")
arcpy.Erase_analysis("AUXILIAR\\LINDEIROS_.shp", "AUXILIAR\\MANZANAS_FRONTE2.shp", "LINDEIROS.shp")

# Se crean las medianeras y fachadas preliminares de las plantas altas (de edificios entre si para captar medianeras en voladizos)
arcpy.FeatureToLine_management("ALTAS.shp", "AUXILIAR\\ALTAS_LINE.shp")
arcpy.Dissolve_management("ALTAS.shp", "AUXILIAR\\ALTAS_.shp")
arcpy.FeatureToLine_management("AUXILIAR\\ALTAS_.shp", "AUXILIAR\\ALTAS_FACHADA.shp")
arcpy.Erase_analysis("AUXILIAR\\ALTAS_LINE.shp", "AUXILIAR\\ALTAS_FACHADA.shp", "AUXILIAR\\MEDIANERAS_.shp")

#Se crea una capa maestro de lindes y medianeras altas (existen medianeras en vuelos sobre el espacio publico)
arcpy.Merge_management(["AUXILIAR\\MEDIANERAS_.shp", "LINDEIROS.shp"], "AUXILIAR\\MEDIANEIRAS_LINDEIROS_.shp")
arcpy.Dissolve_management("AUXILIAR\\MEDIANEIRAS_LINDEIROS_.shp", "MEDIANEIRAS_LINDEIROS.shp")

# Se crean las medianeras y fachadas de las plantas altas (lo mismo podria hacerse con las otras plantas)
arcpy.Erase_analysis("AUXILIAR\\ALTAS_LINE.shp", "MEDIANEIRAS_LINDEIROS.shp", "FACHADAS.shp")
arcpy.Erase_analysis("AUXILIAR\\ALTAS_LINE.shp", "FACHADAS.shp", "MEDIANERAS.shp")

#Por ultimo se borran las capas auxiliares utilizadas
shutil.rmtree(auxiliar)

#PUNTO DE PARADA PARA QUE EL USUARIO CONTROLE Y SI QUIERE MODIFIQUE LA CAPA
print "Controle las condiciones de adyacencia y modifique la capa MEDIANEIRAS_LINDEIROS.shp"





