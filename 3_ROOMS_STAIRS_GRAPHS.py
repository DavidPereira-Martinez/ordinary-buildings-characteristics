#-------------------------------------------------------------------------------
# Name:        3_ROOMS_STAIRS_GRAPHS.py
# Purpose:     Este script calcula:
#              1) Una estimacion de cuartos equivalentes para edifcios corrientes
#              2) Si es un edificio unifamiliar o una estimacion de la division
#              de 1 y 2 apartamentos, con la posicion del nucleo vertical
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
arcpy.env.overwriteOutput = True


#Funcion que dibuja el grafo de la vivienda
def grafo(vivienda):
    output = "AUXILIAR2\\" + str(vivienda) + ".shp"
    output2 = "AUXILIAR3\\" + str(vivienda) + "_20.shp"
    output3 = "AUXILIAR2\\" + str(vivienda) + "_6.shp"
    try:
        arcpy.FeatureToPoint_management(output3, output2)
    except Exception:
        arcpy.FeatureToPoint_management(output, output2)
    output2 = "AUXILIAR3\\" + str(vivienda) + "_21.shp"
    arcpy.Select_analysis("AUXILIAR2\\0_1.shp", output2, "FID = -1") #crea capa en blanco
    auxiliar4 = root + "\\AUXILIAR4"
    os.mkdir(auxiliar4)
    output = "AUXILIAR2\\" + str(vivienda) + "_9.dbf"
    row2s = arcpy.SearchCursor(output)
    for row2 in row2s:
        output = "AUXILIAR2\\" + str(vivienda) + "_9.shp"
        clause = '"FID" = ' + str(row2.FID)
        output2 = "AUXILIAR4\\" + str(row2.FID) + ".shp"
        arcpy.Select_analysis(output, output2, clause)
        output = "AUXILIAR3\\" + str(vivienda) + "_20.shp"
        output3 = "AUXILIAR4\\" + str(row2.FID) + "b.shp"
        arcpy.Merge_management([output2, output], output3)
        output = "AUXILIAR4\\" + str(row2.FID) + "c.shp"
        arcpy.PointsToLine_management(output3, output)
        output2 = "AUXILIAR3\\" + str(vivienda) + "_21.shp"
        output3 = "AUXILIAR4\\" + str(vivienda) + "_21.shp"
        if row2.FID == 0:
            arcpy.Copy_management(output, output2)
        else:
            arcpy.Merge_management([output2, output], output3)
            arcpy.Copy_management(output3, output2)
    shutil.rmtree(auxiliar4)

def grafo2(edificio):

    auxiliar4 = root + "\\AUXILIAR4"
    os.mkdir(auxiliar4)
    output = "AUXILIAR2\\" + str(edificio) + "_9.dbf"
    row2s = arcpy.SearchCursor(output)
    for row2 in row2s:
        output = "AUXILIAR2\\" + str(edificio) + "_9.shp"
        clause = '"FID" = ' + str(row2.FID)
        output2 = "AUXILIAR4\\" + str(row2.FID) + ".shp"
        arcpy.Select_analysis(output, output2, clause)
        if row2.VIVIENDA == 0:
            output = "AUXILIAR3\\" + str(edificio) + "_0_20.shp"
        else:
            output = "AUXILIAR3\\" + str(edificio) + "_1_20.shp"
        output3 = "AUXILIAR4\\" + str(row2.FID) + "b.shp"
        arcpy.Merge_management([output2, output], output3)
        output = "AUXILIAR4\\" + str(row2.FID) + "c.shp"
        arcpy.PointsToLine_management(output3, output)

        outputb = "AUXILIAR4\\" + str(row2.FID) + "c.dbf"
        arcpy.AddField_management(outputb, "VIVIENDA", "SHORT")
        arcpy.CalculateField_management(outputb, "VIVIENDA", row2.VIVIENDA, "PYTHON_9.3")

        output2 = "AUXILIAR3\\" + str(edificio) + "_21.shp"
        output3 = "AUXILIAR4\\" + str(edificio) + "_21.shp"
        if row2.FID == 0:
            arcpy.Copy_management(output, output2)
        else:
            arcpy.Merge_management([output2, output], output3)
            arcpy.Copy_management(output3, output2)
    shutil.rmtree(auxiliar4)

auxiliar2 = root + "\\AUXILIAR2"
os.mkdir(auxiliar2)
auxiliar3 = root + "\\AUXILIAR3"
os.mkdir(auxiliar3)

#SE RECALCULAN LAS CAPAS DE ADYACENCIA A PARTIR DE LAS MODIFICACIONES DEL USUARIO
arcpy.FeatureToLine_management("PARCELA.shp", "AUXILIAR2\\PARCELA_LINE.shp")
arcpy.Intersect_analysis(["MEDIANEIRAS_LINDEIROS.shp", "AUXILIAR2\\PARCELA_LINE.shp"], "LINDEIROS.shp")
arcpy.FeatureToLine_management("ALTAS.shp", "AUXILIAR2\\ALTAS_LINE.shp")
arcpy.Erase_analysis("AUXILIAR2\\ALTAS_LINE.shp", "MEDIANEIRAS_LINDEIROS.shp", "FACHADAS.shp")
arcpy.Erase_analysis("AUXILIAR2\\ALTAS_LINE.shp", "FACHADAS.shp", "MEDIANERAS.shp")


#Bucle FOR con el objetivo de exportar cada edificio a un archivo de capa separado
arcpy.AddField_management("ALTAS.dbf", "AREA", "FLOAT")
arcpy.CalculateField_management("ALTAS.dbf", "AREA", "!SHAPE.area@SQUAREMETERS!", "PYTHON_9.3")
rows = arcpy.SearchCursor("ALTAS.dbf")
for row in rows:
    clause = '"FID" = ' + str(row.FID)
    output = "AUXILIAR2\\" + str(row.FID) + ".shp"
    arcpy.Select_analysis("ALTAS.shp", output, clause)

#DESCRIPCION DE LAS CAPAS QUE SE VAN A CREAR POR CADA UNO DE LOS EDIFICIOS
#Carpeta AUXILIAR2
# _1: (Fachadas del edificio)
# _2: (buffer 2,5m desde fachada)
# _3: (superficie >2,5m desde fachada)
# _4: (linea 2,5m desde fachada)
# _5: (buffer 3,5m desde fachada)
# _6: Superficie >3,5m desde fachada
# _7: Corredor(es) de apartamentos
# _8: (Superficie <3,5m desde fachada)
# _9: Puntos cuartos equivalentes
# _10: Superficie de cuartos equivalentes
# _11: Fachadas de los cuartos
#Carpeta AUXILIAR3
# _20: Centroide de apartamento(s) (corredores)
# _21: Lineas de grafo de apartamento
# _22: Centroide de nucleo(s)
# _23: Superficie de nucleo(s)
# _24: Lineas de grafo de planta

#Esta capa sera usada para substraer y evitar que se formen estancias al final de las lineas de fachada
arcpy.Buffer_analysis("MEDIANERAS.shp", "AUXILIAR2\\MED_.shp", "1,45", "FULL", "ROUND", "ALL")

#Bucle para estimar las estancias que dan a fachada
registros = int(arcpy.GetCount_management("ALTAS.shp").getOutput(0))
oid = 0
while  oid < registros:
    #Fachada y primer buffer de fachada
    input = "AUXILIAR2\\" + str(oid) + ".shp"
    output = "AUXILIAR2\\" + str(oid) + "_1.shp"
    arcpy.Intersect_analysis ([input, "FACHADAS.shp"], output, "ALL", "", "")
    output2 = "AUXILIAR2\\" + str(oid) + "_2.shp"
    arcpy.Buffer_analysis(output, output2, "2,5", "FULL", "ROUND", "ALL")
    output = "AUXILIAR2\\" + str(oid) + "_3.shp"
    arcpy.Erase_analysis(input, output2, output)

    #Linea de puntos de estancias
    output2 = "AUXILIAR2\\" + str(oid) + "_4b.shp"
    try:
        arcpy.FeatureToLine_management(output, output2)
        output = "AUXILIAR2\\" + str(oid) + "_4.shp"
        arcpy.Erase_analysis(output2, "MEDIANEIRAS_LINDEIROS.shp", output)
    except Exception:
        output2 = "AUXILIAR2\\" + str(oid) + "_4.shp"
        arcpy.Select_analysis("AUXILIAR2\\0_1.shp", output2, "FID = -1") #crea capa en blanco

    #Segundo buffer de fachada: franja de estancias y zona de posible corredor
    output = "AUXILIAR2\\" + str(oid) + "_1.shp"
    output2 = "AUXILIAR2\\" + str(oid) + "_5.shp"
    arcpy.Buffer_analysis(output, output2, "3,5", "FULL", "ROUND", "ALL")
    output = "AUXILIAR2\\" + str(oid) + "_6.shp"
    arcpy.Erase_analysis(input, output2, output)

    output = "AUXILIAR2\\" + str(oid) + "_5.shp"
    output2 = "AUXILIAR2\\" + str(oid) + "_8.shp"
    arcpy.Intersect_analysis([input, output], output2, "ALL", "", "")

    #Se estiman los centros de las estancias poniendo una cadena de puntos de lado a lado de fachada
    output = "AUXILIAR2\\" + str(oid) + "_4.shp"
    output2 = "AUXILIAR2\\" + str(oid) + "_9b.shp"
    arcpy.GeneratePointsAlongLines_management(output, output2, 'DISTANCE', Distance='3')
    output3 = "AUXILIAR2\\" + str(oid) + "_9c.shp"
    arcpy.GeneratePointsAlongLines_management(output, output3, 'DISTANCE', Distance='1,5')
    output = "AUXILIAR2\\" + str(oid) + "_9d.shp"
    arcpy.Erase_analysis(output3, output2, output)
    output3 = "AUXILIAR2\\" + str(oid) + "_9.shp"
    arcpy.Erase_analysis(output, "AUXILIAR2\\MED_.shp", output3)
    arcpy.AddField_management(output3, "CUARTO", "SHORT")
    output = "FID_" + str(oid) + "_3"
    arcpy.DeleteField_management(output3, ["Id", "ORIG_FID", output, "SUM_AREA"])

    #Se crea una figura mayor que el edificio para teselar a partir de los puntos de las estacias,
    #se utiliza este teselado como divisiones
    input = "AUXILIAR2\\" + str(oid) + ".shp"
    output = "AUXILIAR2\\" + str(oid) + "_10c.shp"
    arcpy.Buffer_analysis(input, output, "9", "FULL", "ROUND", "ALL")
    output2 = "AUXILIAR2\\" + str(oid) + "_10b.shp"
    arcpy.MinimumBoundingGeometry_management(output, output2, "ENVELOPE")
    output = "AUXILIAR2\\" + str(oid) + "_10d.shp"
    arcpy.FeatureVerticesToPoints_management(output2, output, "ALL")
    output2 = "AUXILIAR2\\" + str(oid) + "_10e.shp"
    arcpy.Merge_management([output3, output], output2)
    output = "AUXILIAR2\\" + str(oid) + "_10f.shp"
    try:
        arcpy.CreateThiessenPolygons_analysis(output2, output, "ALL")
    except Exception:
        arcpy.Select_analysis("AUXILIAR2\\0_10.shp", output, "FID = -1") #crea capa en blanco
    output3 = "AUXILIAR2\\" + str(oid) + "_8.shp"
    output2 = "AUXILIAR2\\" + str(oid) + "_10.shp"
    arcpy.Intersect_analysis ([output, output3], output2, "ALL", "", "")

    #Seleccion de los cuartos con fachada menor de 1m, eliminacion y recalculo
    output = "AUXILIAR2\\" + str(oid) + "_11b.shp"
    try:
        arcpy.FeatureToLine_management(output2, output)
    except Exception:
        arcpy.Select_analysis("AUXILIAR2\\0_1.shp", output, "FID = -1") #crea capa en blanco
    output2 = "AUXILIAR2\\" + str(oid) + "_1.shp"
    output3 = "AUXILIAR2\\" + str(oid) + "_11.shp"
    arcpy.Intersect_analysis ([output, output2], output3, "ALL", "", "")
    output = "AUXILIAR2\\" + str(oid) + "_11.dbf"
    arcpy.AddField_management(output, "LENGTH", "FLOAT")
    arcpy.CalculateField_management(output, "LENGTH", "!SHAPE.length@METERS!", "PYTHON_9.3")
    output2 = "AUXILIAR2\\" + str(oid) + "_10g.shp"
    output = "AUXILIAR2\\" + str(oid) + "_10.shp"
    arcpy.SpatialJoin_analysis(output, output3, output2)
    output = "AUXILIAR2\\" + str(oid) + "_10h.shp"
    arcpy.Select_analysis(output2, output, "LENGTH < 1")
    output2 = "AUXILIAR2\\" + str(oid) + "_9.shp"
    output3 = "AUXILIAR2\\" + str(oid) + "_10j.shp"
    arcpy.Erase_analysis(output2, output, output3)
    arcpy.Copy_management(output3, output2)
    output = "AUXILIAR2\\" + str(oid) + "_9.dbf"
    arcpy.CalculateField_management(output, "CUARTO", "!FID!", "PYTHON_9.3")
    #Puntos de cuartos sin apenas fachada eliminados y renumerados

    #Se vuelven a generar las teselas (divisiones) a partir de los puntos limpios
    output = "AUXILIAR2\\" + str(oid) + "_10d.shp"
    output2 = "AUXILIAR2\\" + str(oid) + "_10e.shp"
    output3 = "AUXILIAR2\\" + str(oid) + "_10j.shp"
    arcpy.Merge_management([output3, output], output2)
    output = "AUXILIAR2\\" + str(oid) + "_10f.shp"
    try:
        arcpy.CreateThiessenPolygons_analysis(output2, output, "ALL")
    except Exception:
        arcpy.Select_analysis("AUXILIAR2\\0_10.shp", output, "FID = -1") #crea capa en blanco
    output3 = "AUXILIAR2\\" + str(oid) + "_8.shp"
    output2 = "AUXILIAR2\\" + str(oid) + "_10.shp"
    arcpy.Intersect_analysis ([output, output3], output2, "ALL", "", "")

    #Eliminacion de los campos innecesarios para operar mejor con la capa de los cuartos
    output = "FID_" + str(oid) + "_10f"
    outputb = "FID_" + str(oid) + "_8"
    outputc = "FID_" + str(oid)
    outputd = "FID_" + str(oid) + "_5"
    output3 = "AUXILIAR2\\" + str(oid) + "_10.dbf"
    arcpy.DeleteField_management(output3, [output, "Id", "Input_FID", "Id_1", "ORIG_FID", "SUM_AREA",
        outputb, outputc, outputd, "Id_12", "REFCAT_1"])

    #En esta parte se agrupan las capas de cada edificio en una sola capa de conjunto
    if oid == 0:
        arcpy.Copy_management("AUXILIAR2\\0_9.shp", "CUARTOS.shp")
        arcpy.Copy_management("AUXILIAR2\\0_10.shp", "SUP_CUARTOS.shp")

    else:
        output = "AUXILIAR2\\" + str(oid) + "_9.shp"
        arcpy.Merge_management(["CUARTOS.shp", output], "AUXILIAR2\\CUARTOS.shp")
        arcpy.Copy_management("AUXILIAR2\\CUARTOS.shp", "CUARTOS.shp")
        output = "AUXILIAR2\\" + str(oid) + "_10.shp"
        arcpy.Merge_management(["SUP_CUARTOS.shp", output], "AUXILIAR2\\SUP_CUARTOS.shp")
        arcpy.Copy_management("AUXILIAR2\\SUP_CUARTOS.shp", "SUP_CUARTOS.shp")

    print oid
    oid = oid + 1


#VIVIENDAS-NUCLEOS: para cada edificio se estiman sus viviendas y nucleo
rows = arcpy.SearchCursor("ALTAS.dbf")
for row in rows:
    #Se crean capas en blanco para que en todo caso la combinacion no falle al final del bucle
    output = "AUXILIAR2\\" + str(row.FID) + "_7.shp"
    arcpy.Select_analysis("AUXILIAR2\\0_6.shp", output, "FID = -1") #crea capa en blanco
    output = "AUXILIAR3\\" + str(row.FID) + "_21.shp"
    arcpy.Select_analysis("AUXILIAR2\\0_1.shp", output, "FID = -1") #crea capa en blanco
    output = "AUXILIAR3\\" + str(row.FID) + "_22.shp"
    arcpy.Select_analysis("AUXILIAR2\\0_9.shp", output, "FID = -1") #crea capa en blanco
    output = "AUXILIAR3\\" + str(row.FID) + "_23.shp"
    arcpy.Select_analysis("AUXILIAR2\\0_2.shp", output, "FID = -1") #crea capa en blanco
    output = "AUXILIAR3\\" + str(row.FID) + "_24.shp"
    arcpy.Select_analysis("AUXILIAR2\\0_1.shp", output, "FID = -1") #crea capa en blanco

    #La estimacion de la division interior depende del numero de viviendas
    if row.AREA < 90: #viviendas = 0, es un edificio (casa) unifamiliar
        grafo(row.FID) #Funcion que dibuja el grafo de la vivienda
        output = "AUXILIAR2\\" + str(row.FID) + "_6.shp"
        output2 = "AUXILIAR2\\" + str(row.FID) + "_7.shp"
        arcpy.Copy_management(output, output2)
        print row.FID
    else:
        if row.AREA < 200: #viviendas = 1, tiene 1 apartamento por planta y un nucleo vertical
            grafo(row.FID) #Funcion que dibuja el grafo de la vivienda

            #Se estima la posicion del nucleo en la parte donde el grafo deja mas espacio
            output = "AUXILIAR3\\" + str(row.FID) + "_21.shp"
            output2 = "AUXILIAR3\\" + str(row.FID) + "_22b.shp"
            arcpy.Buffer_analysis(output, output2, "0,5", "FULL", "ROUND", "ALL")
            output3 = "AUXILIAR3\\" + str(row.FID) + "_22c.shp"
            output = "AUXILIAR2\\" + str(row.FID) + "_6.shp"
            arcpy.Erase_analysis(output, output2, output3)
            output = "AUXILIAR3\\" + str(row.FID) + "_22d.shp"
            arcpy.Dissolve_management(output3, output, "AREA", [["AREA", "MAX"]], "SINGLE_PART")
            output = "AUXILIAR3\\" + str(row.FID) + "_22d.dbf"
            arcpy.AddField_management(output, "AREA", "FLOAT")
            arcpy.CalculateField_management(output, "AREA", "!SHAPE.area@SQUAREMETERS!", "PYTHON_9.3")
            output2 = "AUXILIAR3\\" + str(row.FID) + "_22e.shp"
            output3 = "AUXILIAR3\\" + str(row.FID) + "_22.shp"

            #Aqui se busca ese subespacio mayor entre los que deja el grafo
            try:
                arcpy.FeatureToPoint_management(output, output2)
                outputb = "AUXILIAR3\\" + str(row.FID) + "_22e.dbf"
                row3s = arcpy.SearchCursor(outputb)
                areamax = 0
                for row3 in row3s:
                    if row3.AREA > areamax:
                        areamax = row3.AREA
                        IDmax = row3.FID
                clause = '"FID" = ' + str(IDmax)
                arcpy.Select_analysis(output2, output3, clause)

                #Encontrado el subespacio se estima un area del nucleo vertical < 19,6m2
                #y se interseca con otros espacios
                output = "AUXILIAR3\\" + str(row.FID) + "_22.shp"
                output2 = "AUXILIAR3\\" + str(row.FID) + "_23b.shp"
                arcpy.Buffer_analysis(output, output2, "2,5", "FULL", "ROUND", "ALL")
                output3 = "AUXILIAR2\\" + str(row.FID) + "_6.shp"
                output = "AUXILIAR3\\" + str(row.FID) + "_23.shp"
                arcpy.Intersect_analysis([output3, output2], output)
                output = "AUXILIAR2\\" + str(row.FID) + "_6.shp"
                output3 = "AUXILIAR2\\" + str(row.FID) + "_6b.shp"
                arcpy.Erase_analysis(output, output2, output3)
                output = "AUXILIAR2\\" + str(row.FID) + "_7.shp"

                #Por ultimo se calcula el grafo de la planta (nucleo-apartamentos)
                arcpy.Copy_management(output3, output)
                output2 = "AUXILIAR3\\" + str(row.FID) + "_20.shp"
                try:
                    arcpy.FeatureToPoint_management(output3, output2)
                    grafo(row.FID)
                except Exception:
                    arcpy.FeatureToPoint_management(output, output2)
                output3 = "AUXILIAR3\\" + str(row.FID) + "_24b.shp"
                output = "AUXILIAR3\\" + str(row.FID) + "_22.shp"
                arcpy.Merge_management([output, output2], output3)
                output = "AUXILIAR3\\" + str(row.FID) + "_24.shp"
                arcpy.PointsToLine_management(output3, output)
            except Exception:
                output = "AUXILIAR2\\" + str(row.FID) + ".shp"
                arcpy.FeatureToPoint_management(output, output3)
            print row.FID
        else:
            if row.AREA < 300: #viviendas = 2, tiene 2 apartamentos por planta y un nucleo vertical

                #Se estima la division de apartamentos en funcion de la geometria del edificio,
                # asimilando la zona interior (corredor) a un rectangulo:
                #1) Si la zona corredor es mas ancho que profundo se estima que
                # habra una vivienda a cada lado.
                #2) Si la zona corredor es mas profundo que ancho se estima que
                # habra una vivienda delante y otra detras.

                #Se empieza calculando el rectangulo equivalente
                output = "AUXILIAR2\\" + str(row.FID) + "_6.shp"
                output2 = "AUXILIAR3\\" + str(row.FID) + "_20b.shp"
                arcpy.MinimumBoundingGeometry_management(output, output2, "RECTANGLE_BY_WIDTH")
                output = "AUXILIAR3\\" + str(row.FID) + "_20c.shp"
                arcpy.FeatureToLine_management(output2, output)
                output2 = "AUXILIAR3\\" + str(row.FID) + "_20d.shp"
                arcpy.SplitLine_management(output, output2)
                outputb = "AUXILIAR3\\" + str(row.FID) + "_20d.dbf"
                arcpy.AddField_management(outputb, "LARGO", "FLOAT")
                arcpy.CalculateField_management(outputb, "LARGO", "!SHAPE.length@METERS!", "PYTHON_9.3")
                output = "AUXILIAR3\\" + str(row.FID) + "_20db.shp"
                output3 = "AUXILIAR3\\" + str(row.FID) + "_20dc.shp"

                #Aqui se comprueba si la zona corredor es mas ancha que profunda
                row3s = arcpy.SearchCursor(outputb)
                largomax = 0
                for row3 in row3s:
                    if row3.LARGO > largomax:
                        largomax = row3.LARGO
                largomax = largomax - 0.1
                a = 0
                row4s = arcpy.SearchCursor(outputb)
                for row4 in row4s:
                    clause = '"FID" = ' + str(row4.FID)
                    if row4.LARGO < largomax:
                        if a == 0:
                            arcpy.Select_analysis(output2, output3, clause)
                            a = 1
                        else:
                            arcpy.Select_analysis(output2, output, clause)
                output2 = "AUXILIAR3\\" + str(row.FID) + "_20e.shp"
                arcpy.Merge_management([output, output3], output2)

                #Se calculan 2 puntos ficticios para dividir la panta en 2 apartamentos
                output3 = "AUXILIAR3\\" + str(row.FID) + "_20f.shp"
                arcpy.FeatureToPoint_management(output2, output3)
                outputb = "AUXILIAR3\\" + str(row.FID) + "_20f.dbf"
                arcpy.AddField_management(outputb, "VIVIENDA", "FLOAT")
                arcpy.CalculateField_management(outputb, "VIVIENDA", "!FID!", "PYTHON_9.3")
                output3 = "AUXILIAR3\\" + str(row.FID) + "_20f.shp"
                output2 = "AUXILIAR3\\" + str(row.FID) + "_20g.shp"
                arcpy.Buffer_analysis(output3, output2, "50", "FULL", "ROUND", "ALL")
                output = "AUXILIAR3\\" + str(row.FID) + "_20h.shp"
                arcpy.FeatureVerticesToPoints_management(output2, output, "ALL")
                output2 = "AUXILIAR3\\" + str(row.FID) + "_20i.shp"
                arcpy.Merge_management([output3, output], output2)
                output = "AUXILIAR3\\" + str(row.FID) + "_20j.shp"
                arcpy.CreateThiessenPolygons_analysis(output2, output, "ALL")
                output3 = "AUXILIAR2\\" + str(row.FID) + "_6.shp"
                output2 = "AUXILIAR2\\" + str(row.FID) + "_7.shp"
                arcpy.Intersect_analysis([output, output3], output2, "ALL", "", "")

                #calculadas las 2 zonas de corredor de cada vivienda, se pasan a puntos
                output3 = "AUXILIAR3\\" + str(row.FID) + "_20.shp"
                try:
                    arcpy.FeatureToPoint_management(output2, output3)
                except Exception:
                    output3 = "AUXILIAR3\\" + str(row.FID) + "_20.shp"
                    arcpy.Select_analysis("AUXILIAR2\\0_9.shp", output3, "FID = -1") #crea capa en blanco
                output = "AUXILIAR3\\" + str(row.FID) + "_0_20.shp"
                arcpy.Select_analysis(output3, output, "VIVIENDA = 0")
                output = "AUXILIAR3\\" + str(row.FID) + "_1_20.shp"
                arcpy.Select_analysis(output3, output, "VIVIENDA = 1")

                #Se intersecan los poligonos de las 2 viviendas con los cuartos
                #para incluir en la tabla de los cuartos a que vivienda pertenecen
                output3 = "AUXILIAR2\\" + str(row.FID) + "_9.shp"
                output2 = "AUXILIAR3\\" + str(row.FID) + "_21b.shp"
                output = "AUXILIAR3\\" + str(row.FID) + "_20j.shp"
                arcpy.Intersect_analysis([output, output3], output2, "ALL", "", "")
                arcpy.Copy_management(output2, output3)
                grafo2(row.FID) #y se calculan los grafos de cada vivienda

                #Para estimar la localizacion del nucleo vertical se calcula el grafo
                # y se utiliza para cortar el espacio de corredor en varios subespacios.
                #El nucleo vertical estara colocado en el subespacio que una
                # el centro de los dos apartamentos (el unico que no corta la comunicacion entre cuartos).
                output = "AUXILIAR3\\" + str(row.FID) + "_21.shp"
                output2 = "AUXILIAR3\\" + str(row.FID) + "_22b.shp"
                arcpy.Buffer_analysis(output, output2, "0,5", "FULL", "ROUND", "LIST", "VIVIENDA")
                outputb = "AUXILIAR3\\" + str(row.FID) + "_22b.dbf"
                output3 = "AUXILIAR3\\" + str(row.FID) + "_22c.shp"
                output = "AUXILIAR2\\" + str(row.FID) + "_6.shp"
                arcpy.Erase_analysis(output, output2, output3)
                output = "AUXILIAR3\\" + str(row.FID) + "_22d.shp"
                arcpy.Dissolve_management(output3, output, "REFCAT", "", "SINGLE_PART")

                #Aqui se elige entre los varios subespacios aquel que conecta los apartamentos
                outputb = "AUXILIAR3\\" + str(row.FID) + "_22d.dbf" #Espacios posibles nucleos
                arcpy.AddField_management(outputb, "VIVIENDA", "SHORT")
                row4s = arcpy.SearchCursor(outputb) #Espacios posibles nucleos
                row4s = arcpy.UpdateCursor(outputb)
                auxiliar4 = root + "\\AUXILIAR4"
                os.mkdir(auxiliar4)
                for row4 in row4s:
                    output = "AUXILIAR3\\" + str(row.FID) + "_22d.shp"
                    clause = '"FID" = ' + str(row4.FID)
                    output2 = "AUXILIAR4\\" + str(row4.FID) + ".shp"
                    arcpy.Select_analysis(output, output2, clause)
                    outputc = "AUXILIAR3\\" + str(row.FID) + "_22b.dbf" #Espacios grafos
                    row5s = arcpy.SearchCursor(outputb)
                    for row5 in row5s:
                        output = "AUXILIAR3\\" + str(row.FID) + "_22b.shp"
                        clause = '"FID" = ' + str(row5.FID)
                        output3 = "AUXILIAR4\\" + str(row5.FID) + "b.shp"
                        arcpy.Select_analysis(output, output3, clause)
                        output = "AUXILIAR4\\" + str(row5.FID) + "c.shp"
                        arcpy.Intersect_analysis([output2, output3], output, "ALL", "", "LINE")
                        result = arcpy.GetCount_management(output)
                        count = int(result.getOutput(0))
                        if count > 0:
                            #Se calcula que subespacio toca los grafos de los 2 apartamentos
                            row4.VIVIENDA = row4.VIVIENDA + 1
                            row4s.updateRow(row4)
                shutil.rmtree(auxiliar4)
                output = "AUXILIAR3\\" + str(row.FID) + "_22d.shp"
                output2 = "AUXILIAR3\\" + str(row.FID) + "_22f.shp"
                arcpy.Select_analysis(output, output2, "VIVIENDA = 2")
                #Seleccion del subespacio que toca el grafo de las 2 viviendas

                #Encontrado el subespacio se estima un area del nucleo vertical < 19,6m2
                # y se interseca con otros espacios
                output = "AUXILIAR3\\" + str(row.FID) + "_22.shp"
                arcpy.FeatureToPoint_management(output2, output)
                output = "AUXILIAR3\\" + str(row.FID) + "_22.shp"
                output2 = "AUXILIAR3\\" + str(row.FID) + "_23b.shp"
                arcpy.Buffer_analysis(output, output2, "2,5", "FULL", "ROUND", "ALL")
                output3 = "AUXILIAR2\\" + str(row.FID) + "_6.shp"
                output = "AUXILIAR3\\" + str(row.FID) + "_23.shp"
                arcpy.Intersect_analysis([output3, output2], output)
                output = "AUXILIAR2\\" + str(row.FID) + "_7.shp"
                output3 = "AUXILIAR2\\" + str(row.FID) + "_6b.shp"
                arcpy.Erase_analysis(output, output2, output3)
                output = "AUXILIAR2\\" + str(row.FID) + "_7.shp"
                arcpy.Copy_management(output3, output)

                #Por ultimo se calcula el grafo de la planta (nucleo-apartamentos)
                outputb = "AUXILIAR3\\" + str(row.FID) + "_20.dbf"
                row6s = arcpy.SearchCursor(outputb)
                for row6 in row6s:
                    output2 = "AUXILIAR3\\" + str(row.FID) + "_20.shp"
                    output = "AUXILIAR3\\" + str(row.FID) + "_20_" + str(row6.FID) + ".shp"
                    clause = '"FID" = ' + str(row6.FID)
                    arcpy.Select_analysis(output2, output, clause)
                    output3 = "AUXILIAR3\\" + str(row.FID) + "_20_" + str(row6.FID) + "b.shp"
                    output2 = "AUXILIAR3\\" + str(row.FID) + "_22.shp"
                    arcpy.Merge_management([output, output2], output3)
                    output = "AUXILIAR3\\" + str(row.FID) + "_20_" + str(row6.FID) + "c.shp"
                    arcpy.PointsToLine_management(output3, output)
                    output2 = "AUXILIAR3\\" + str(row.FID) + "_24.shp"
                    output3 = "AUXILIAR3\\" + str(row.FID) + "_24b.shp"
                    if row6.FID == 0:
                        arcpy.Copy_management(output, output2)
                    else:
                        arcpy.Merge_management([output2, output], output3)
                        arcpy.Copy_management(output3, output2)

            else:
                #Estos serian edificios > 2 apartamentos por planta
                #Podria programarse un procedimiento analogo
                output = "AUXILIAR3\\" + str(row.FID) + "_20.shp"
                arcpy.Select_analysis("AUXILIAR2\\0_9.shp", output, "FID = -1") #crea capa en blanco
                output = "AUXILIAR2\\" + str(row.FID) + "_6.shp"
                output2 = "AUXILIAR2\\" + str(row.FID) + "_7.shp"
                arcpy.Copy_management(output, output2)
                """if row.AREA < 400: #viviendas = 3
                        if row.AREA < 500: #viviendas = 4"""


    #En esta parte se agrupan las capas de cada edificio en una sola capa de conjunto
    if row.FID == 0:
        arcpy.Copy_management("AUXILIAR2\\0_7.shp", "CORREDOR.shp")
        arcpy.Copy_management("AUXILIAR3\\0_20.shp", "APARTAMENTOS.shp")
        arcpy.Copy_management("AUXILIAR3\\0_21.shp", "GRAFOS.shp")
        arcpy.Copy_management("AUXILIAR3\\0_22.shp", "NUCLEO.shp")
        arcpy.Copy_management("AUXILIAR3\\0_23.shp", "NUCLEO_S.shp")
        arcpy.Copy_management("AUXILIAR3\\0_24.shp", "GRAFOP.shp")

    else:
        output = "AUXILIAR2\\" + str(row.FID) + "_7.shp"
        arcpy.Merge_management(["CORREDOR.shp", output], "AUXILIAR2\\CORREDOR.shp")
        arcpy.Copy_management("AUXILIAR2\\CORREDOR.shp", "CORREDOR.shp")
        output = "AUXILIAR3\\" + str(row.FID) + "_20.shp"
        arcpy.Merge_management(["APARTAMENTOS.shp", output], "AUXILIAR3\\APARTAMENTOS.shp")
        arcpy.Copy_management("AUXILIAR3\\APARTAMENTOS.shp", "APARTAMENTOS.shp")
        output = "AUXILIAR3\\" + str(row.FID) + "_21.shp"
        arcpy.Merge_management(["GRAFOS.shp", output], "AUXILIAR3\\GRAFOS.shp")
        arcpy.Copy_management("AUXILIAR3\\GRAFOS.shp", "GRAFOS.shp")
        output = "AUXILIAR3\\" + str(row.FID) + "_22.shp"
        arcpy.Merge_management(["NUCLEO.shp", output], "AUXILIAR3\\NUCLEO.shp")
        arcpy.Copy_management("AUXILIAR3\\NUCLEO.shp", "NUCLEO.shp")
        output = "AUXILIAR3\\" + str(row.FID) + "_23.shp"
        arcpy.Merge_management(["NUCLEO_S.shp", output], "AUXILIAR3\\NUCLEO_S.shp")
        arcpy.Copy_management("AUXILIAR3\\NUCLEO_S.shp", "NUCLEO_S.shp")
        output = "AUXILIAR3\\" + str(row.FID) + "_24.shp"
        arcpy.Merge_management(["GRAFOP.shp", output], "AUXILIAR3\\GRAFOP.shp")
        arcpy.Copy_management("AUXILIAR3\\GRAFOP.shp", "GRAFOP.shp")


#Se borran las carpetas creadas
shutil.rmtree(auxiliar2)
shutil.rmtree(auxiliar3)






