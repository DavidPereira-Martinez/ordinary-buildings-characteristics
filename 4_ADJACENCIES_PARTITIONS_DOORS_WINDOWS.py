#-------------------------------------------------------------------------------
# Name:        4
# Purpose:     Este script agrupa espacios interiores en apartamentos y edificios,
#               da espesores de muros y dibuja ventanas y puertas
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

#Funcion que dibuja el grafo de la vivienda
def grafo(edificio, vivienda):

    outputb = "AUXILIAR2\\" + str(edificio) + "_7.dbf"
    row2s = arcpy.SearchCursor(outputb)
    for row2 in row2s:
        if row2.DWELLING == vivienda:
            output = "AUXILIAR2\\" + str(edificio) + "_7.shp"
            output2 = "AUXILIAR4\\" + str(row2.FID) + "_1.shp"
            clause = '"FID" = ' + str(row2.FID)
            arcpy.Select_analysis(output, output2, clause)

            output = "AUXILIAR2\\" + str(edificio) + "_4.shp"
            output3 = "AUXILIAR4\\" + str(row2.FID) + "_2.shp"
            clause = '"DWELLING" = ' + str(row2.DWELLING)
            arcpy.Select_analysis(output, output3, clause)

            output = "AUXILIAR4\\" + str(row2.FID) + "_3.shp"
            arcpy.Merge_management([output2, output3], output)

            output3 = "AUXILIAR4\\" + str(row2.FID) + "_4.shp"
            arcpy.PointsToLine_management(output, output3)

            output2 = "AUXILIAR2\\" + str(edificio) + "_8.shp"
            output = "AUXILIAR4\\" + str(row2.FID) + "_5.shp"

            arcpy.Merge_management([output2, output3], output)
            arcpy.Copy_management(output, output2)


def grafo2(edificio):

    auxiliar4 = root + "\\AUXILIAR4"
    os.mkdir(auxiliar4)

    outputb = "AUXILIAR2\\" + str(edificio) + "_4.dbf"
    row2s = arcpy.SearchCursor(outputb)
    for row2 in row2s:
        output = "AUXILIAR2\\" + str(edificio) + "_4.shp"
        output2 = "AUXILIAR4\\" + str(row2.FID) + "_1.shp"
        clause = '"FID" = ' + str(row2.FID)
        arcpy.Select_analysis(output, output2, clause)

        output = "AUXILIAR2\\" + str(edificio) + "_2.shp"
        output3 = "AUXILIAR4\\" + str(row2.FID) + "_3.shp"
        arcpy.Merge_management([output2, output], output3)

        output = "AUXILIAR4\\" + str(row2.FID) + "_4.shp"
        arcpy.PointsToLine_management(output3, output)

        output2 = "AUXILIAR2\\" + str(edificio) + "_5.shp"
        output3 = "AUXILIAR4\\" + str(edificio) + "_5.shp"
        if row2.FID == 0:
            arcpy.Copy_management(output, output2)
        else:
            arcpy.Merge_management([output2, output], output3)
            arcpy.Copy_management(output3, output2)
    shutil.rmtree(auxiliar4)


#Aqui se define la carpeta que va a contener los shapefiles
root = "d:\\Usuario\\Desktop\\PROBA"
env.workspace = root
auxiliar = root + "\\AUXILIAR"
os.mkdir(auxiliar)

#Espesores de muros:
fachada="0,3"
medianera="0,2"
vivienda_escalera="0,1" # Mitad del espesor
particion="0,05" # Mitad del espesor
ventana="0,6" # Mitad del ancho
puerta="0,15" # Mitad del ancho

#Se agrupan los pasillos
arcpy.Select_analysis("INTERIORS.SHP", "AUXILIAR\\P.shp", "ROOM = 0 OR ROOM = 10")
arcpy.Dissolve_management("AUXILIAR\\P.shp", "AUXILIAR\\P2.shp", ["BUILDING", "DWELLING"], [], "SINGLE_PART")
arcpy.Erase_analysis("INTERIORS.SHP", "AUXILIAR\\P2.shp", "AUXILIAR\\INT.shp")
arcpy.Merge_management(["AUXILIAR\\INT.shp", "AUXILIAR\\P2.shp"], "INT_SIMPL.shp")

#Se agrupan los espacios en apartamento
arcpy.Dissolve_management("INT_SIMPL.shp", "DWELLINGS.SHP", ["BUILDING", "DWELLING"],[["SHAPE_AREA", "SUM"], ["YEAR", "MAX"], ["ROOM", "COUNT"], ["LIC", "MAX"],
["BASEMENT", "MAX"], ["GROUNDFLOO", "MAX"], ["FLOORS", "MAX"]], "SINGLE_PART")
arcpy.CalculateField_management("DWELLINGS.dbf", "COUNT_ROOM", "!COUNT_ROOM!-1", "PYTHON_9.3")

#Se agrupan los espacios en edificio
arcpy.Dissolve_management("DWELLINGS.SHP", "BUILDINGS.SHP", "BUILDING", [["DWELLING", "COUNT"],["SUM_SHAPE_", "SUM"], ["MAX_YEAR", "MAX"], ["COUNT_ROOM", "SUM"], ["MAX_LIC", "MAX"],
["MAX_BASEME", "MAX"], ["MAX_GROUND", "MAX"], ["MAX_FLOORS", "MAX"]], "SINGLE_PART")
arcpy.CalculateField_management("BUILDINGS.dbf", "COUNT_DWEL", "!COUNT_DWEL!-1", "PYTHON_9.3")


"""#Se crean las fachadas y se crean las superficies de muros
arcpy.FeatureToLine_management("BUILDINGS.SHP", "AUXILIAR\\ALTAS_LINE.shp")
arcpy.Erase_analysis("AUXILIAR\\ALTAS_LINE.shp", "MEDIANERAS.shp", "AUXILIAR\\FACHADAS.shp")
arcpy.Buffer_analysis("AUXILIAR\\FACHADAS.shp", "AUXILIAR\\F.shp", fachada, "FULL", "FLAT", "ALL")
arcpy.Buffer_analysis("MEDIANERAS.shp", "AUXILIAR\\M.shp", medianera, "FULL", "FLAT", "ALL")
arcpy.FeatureToLine_management("DWELLINGS.SHP", "AUXILIAR\\D_LINE.shp")
arcpy.Buffer_analysis("AUXILIAR\\D_LINE.shp", "AUXILIAR\\D.shp", vivienda_escalera, "FULL", "FLAT", "ALL")
arcpy.FeatureToLine_management("INTERIORS.SHP", "AUXILIAR\\I_LINE.shp")
arcpy.Buffer_analysis("AUXILIAR\\I_LINE.shp", "AUXILIAR\\I.shp", particion, "FULL", "FLAT", "ALL")
arcpy.Merge_management(["AUXILIAR\\F.shp", "AUXILIAR\\M.shp", "AUXILIAR\\D.shp", "AUXILIAR\\I.shp"], "AUXILIAR\\BUFFER.shp")
arcpy.Intersect_analysis(["BUILDINGS.shp", "AUXILIAR\\BUFFER.shp"], "AUXILIAR\\W.shp")
arcpy.Dissolve_management("AUXILIAR\\W.shp", "WALLS.shp", "BUILDING", [], "SINGLE_PART")
arcpy.Erase_analysis("INTERIORS.shp", "AUXILIAR\\BUFFER.shp", "INT_SURFACES.shp")

#Se crean las ventanas en fachada y las puertas entre pasillos y estancias
arcpy.Intersect_analysis(["AUXILIAR\\FACHADAS.shp", "INTERIORS.shp"], "AUXILIAR\\V.shp")
arcpy.FeatureToPoint_management("AUXILIAR\\V.shp", "AUXILIAR\\V2.shp", "INSIDE")
arcpy.Buffer_analysis("AUXILIAR\\V2.shp", "AUXILIAR\\V3.shp", ventana, "FULL", "ROUND", "ALL")
arcpy.Intersect_analysis(["AUXILIAR\\V.shp", "AUXILIAR\\V3.shp"], "AUXILIAR\\V4.shp")
arcpy.Buffer_analysis("AUXILIAR\\V4.shp", "AUXILIAR\\V5.shp", fachada, "FULL", "FLAT", "ALL")
arcpy.Intersect_analysis(["AUXILIAR\\V5.shp", "WALLS.shp"], "WINDOWS.shp")

arcpy.Dissolve_management("AUXILIAR\\P2.shp", "AUXILIAR\\P2B.shp", [], [], "SINGLE_PART")
arcpy.FeatureToLine_management("AUXILIAR\\P2B.shp", "AUXILIAR\\P2B_LINE.shp")
arcpy.Intersect_analysis(["AUXILIAR\\P2B_LINE.shp", "AUXILIAR\\I_LINE.shp"], "AUXILIAR\\P3.shp")
arcpy.FeatureToLine_management("AUXILIAR\\P.shp", "AUXILIAR\\P_LINE.shp")
arcpy.FeatureToLine_management("AUXILIAR\\P2.shp", "AUXILIAR\\P2_LINE.shp")
arcpy.Erase_analysis("AUXILIAR\\P_LINE.shp", "AUXILIAR\\P2_LINE.shp", "AUXILIAR\\P4.shp")
arcpy.Merge_management(["AUXILIAR\\P3.shp", "AUXILIAR\\P4.shp"], "AUXILIAR\\P5.shp")
arcpy.Erase_analysis("AUXILIAR\\P5.shp", "AUXILIAR\\FACHADAS.shp", "AUXILIAR\\P5B.shp")
arcpy.Erase_analysis("AUXILIAR\\P5B.shp", "MEDIANERAS.shp", "AUXILIAR\\P5C.shp")

arcpy.FeatureToPoint_management("AUXILIAR\\P5C.shp", "AUXILIAR\\P6.shp", "INSIDE")
arcpy.Buffer_analysis("AUXILIAR\\P6.shp", "AUXILIAR\\P7.shp", puerta, "FULL", "FLAT", "ALL")
arcpy.Intersect_analysis(["AUXILIAR\\P5.shp", "AUXILIAR\\P7.shp"], "AUXILIAR\\P8.shp")
arcpy.Buffer_analysis("AUXILIAR\\P8.shp", "AUXILIAR\\P9.shp", medianera, "FULL", "FLAT", "ALL")
arcpy.Intersect_analysis(["AUXILIAR\\P9.shp", "WALLS.shp"], "DOORS.shp")
"""
#Se crean los grafos de los apartamentos y del edificio
"""auxiliar = root + "\\AUXILIAR2"
os.mkdir(auxiliar)
auxiliar = root + "\\AUXILIAR3"
os.mkdir(auxiliar)
rows = arcpy.SearchCursor("BUILDINGS.dbf")
for row in rows:
    clause = "BUILDING = " + str(row.BUILDING)
    output = "AUXILIAR2\\" + str(row.BUILDING) + ".shp"
    arcpy.Select_analysis("INT_SIMPL.shp", output, clause)

    output2 = "AUXILIAR2\\" + str(row.BUILDING) + "_1.shp"
    clause = "ROOM = 20"
    arcpy.Select_analysis(output, output2, clause)
    output3 = "AUXILIAR2\\" + str(row.BUILDING) + "_2.shp"
    arcpy.FeatureToPoint_management(output2, output3)

    output2 = "AUXILIAR2\\" + str(row.BUILDING) + "_3.shp"
    clause = "(ROOM = 0 OR ROOM = 10) AND DWELLING > 0"
    arcpy.Select_analysis(output, output2, clause)
    output = "AUXILIAR2\\" + str(row.BUILDING) + "_4.shp"
    arcpy.FeatureToPoint_management(output2, output)
    grafo2(row.BUILDING)

    output = "AUXILIAR2\\" + str(row.BUILDING) + ".shp"
    output2 = "AUXILIAR2\\" + str(row.BUILDING) + "_6.shp"
    clause = "ROOM <> 0 AND ROOM <> 10 AND ROOM <> 20"
    arcpy.Select_analysis(output, output2, clause)

    output = "AUXILIAR2\\" + str(row.BUILDING) + "_7.shp"
    arcpy.FeatureToPoint_management(output2, output)

    auxiliar4 = root + "\\AUXILIAR4"
    os.mkdir(auxiliar4)
    output = "AUXILIAR2\\" + str(row.BUILDING) + "_5.shp"
    output2 = "AUXILIAR2\\" + str(row.BUILDING) + "_8.shp"
    arcpy.Select_analysis(output, output2, "FID = -1") #crea capa en blanco

    outputb = "AUXILIAR2\\" + str(row.BUILDING) + "_4.dbf"
    row3s = arcpy.SearchCursor(outputb)
    for row3 in row3s:
        grafo(row.BUILDING, row3.DWELLING)
    shutil.rmtree(auxiliar4)


    #En esta parte se agrupan las capas de cada edificio en una sola capa de conjunto
    output = "AUXILIAR2\\" + str(row.BUILDING) + "_2.shp"
    output2 = "AUXILIAR2\\" + str(row.BUILDING) + "_4.shp"
    output3 = "AUXILIAR2\\" + str(row.BUILDING) + "_5.shp"
    output4 = "AUXILIAR2\\" + str(row.BUILDING) + "_7.shp"
    output5 = "AUXILIAR2\\" + str(row.BUILDING) + "_8.shp"
    if row.FID == 0:
        arcpy.Copy_management(output, "STAIRS.shp")
        arcpy.Copy_management(output2, "CORRIDOR.shp")
        arcpy.Copy_management(output3, "GRAPH_B.shp")
        arcpy.Copy_management(output4, "ROOMS.shp")
        arcpy.Copy_management(output5, "GRAPH_D.shp")

    else:
        arcpy.Merge_management(["STAIRS.shp", output], "AUXILIAR2\\STAIRS.shp")
        arcpy.Copy_management("AUXILIAR2\\STAIRS.shp", "STAIRS.shp")
        arcpy.Merge_management(["CORRIDOR.shp", output2], "AUXILIAR2\\CORRIDOR.shp")
        arcpy.Copy_management("AUXILIAR2\\CORRIDOR.shp", "CORRIDOR.shp")
        arcpy.Merge_management(["GRAPH_B.shp", output3], "AUXILIAR2\\GRAPH_B.shp")
        arcpy.Copy_management("AUXILIAR2\\GRAPH_B.shp", "GRAPH_B.shp")
        arcpy.Merge_management(["ROOMS.shp", output4], "AUXILIAR2\\ROOMS.shp")
        arcpy.Copy_management("AUXILIAR2\\ROOMS.shp", "ROOMS.shp")
        arcpy.Merge_management(["GRAPH_D.shp", output5], "AUXILIAR2\\GRAPH_D.shp")
        arcpy.Copy_management("AUXILIAR2\\GRAPH_D.shp", "GRAPH_D.shp")

    print row.BUILDING
"""
#Por ultimo se borran las capas auxiliares utilizadas
#shutil.rmtree(auxiliar)







