import json
import os
import shutil
import sys

#################################Configuration###################################

entree = 'Coco.json'
sortie = 'sortie'
tailleimage = [640, 480]

correspondancesObjets = {
    "4": "0",
    "5": "1"
    # boite est notre seul élément dans l'exemple, il correspond donc à l'indice 0. Le choix de l'ordre importe peu,
    # mais il faut que les items soient notés de 0 à Nombre-1
}
correspondancesNoms = {
    "0": "boite",
    "1": "actionneur"
}


#################################Definitions#####################################

def chargement_source(coco):
    with open(coco, 'r') as coco:
        content = json.load(coco)
        coco.close()
        return content


def make_txt_yolo_from_coco_bbox(dictionnaire, sortie, correspondance_images):
    # Crée la correspondance entre les id et les images, nettoie aussi les fichiers.
    tableau_images = {}
    for q in dictionnaire["images"]:
        tableau_images[q["id"]] = sortie + '/' + q["file_name"][:7] + 'txt'
        file = open('sortie/' + q["file_name"][:7] + 'txt', "w")
        file.close()

    for p in dictionnaire['annotations']:
        name = tableau_images[p["image_id"]]
        numcoco = p["category_id"]
        numyolo = correspondance_images[str(numcoco)]
        x_coco = p["bbox"][0]
        y_coco = p["bbox"][1]
        width = p["bbox"][2]
        height = p["bbox"][3]
        x_yolo = (x_coco + (width / 2)) / tailleimage[0]
        y_yolo = (y_coco + (height / 2)) / tailleimage[1]
        alpha = width / tailleimage[0]
        beta = height / tailleimage[1]

        yolo = open(str(name), "a")
        yolo.write(
            numyolo + " " +
            "{:0.10f}".format(x_yolo) + ' ' +
            "{:0.10f}".format(y_yolo) + ' ' +
            "{:0.10f}".format(alpha) + ' ' +
            "{:0.10f}".format(beta))
        yolo.close()


def part_train(nbimages):
    partTrain = 0
    nbTest = 0
    if nbimages < 500:
        partTrain = 15

    seuil = partTrain * nbimages * 0.01
    return seuil


def dispatch(pathtest, pathtrain, images, data):
    length = len(data["images"])
    for q in data["images"]:
        length = len(data['images'])
        seuil = part_train(length)
        i = 0
        txttrain = pathtrain + 'train.txt'
        txttest = pathtest + 'test.txt'
        if i < seuil:
            os.replace(images + '/' + q["file_name"], pathtrain + '/' + q["file_name"])
            file = open(str(txttrain), "a")
            file.write(pathtrain + '/' + q["file_name"])
            file.close()
            i = +1
        else:
            os.rename(images + q["file_name"], pathtest + '/' + q["file_name"])
            os.rename(pathtrain + '/' + q["file_name"][:-3] + 'txt', pathtest + '/' + q["file_name"][:-3] + 'txt')
            file = open(str(txttest), "a")
            file.write(pathtest + '/' + q["file_name"])
            file.close()


def create_data_txt(pathtest, pathtrain, pathbackup, nbclasses, pathconfig):
    txtdata = pathconfig + "/data.txt"
    file = open(str(txtdata), "a")
    file.write(
        "classes = " + str(nbclasses) + "\n" +
        "train = " + pathtrain + 'train.txt\n' +
        "valid = " + pathtest + 'test.txt\n' +
        "names = " + pathconfig + 'classes.names\n' +
        "backup = " + pathbackup
    )
    file.close()


def create_names(dictImages, filePath):
    length = len(dictImages)
    for i in range(0, length - 1):
        file = open(str(filePath), 'a')
        file.write(dictImages[str(i)])
        file.close()


def create_script(dataFilePath, configFilePath, originalWheightPath, filePath):
    file = open(str(filePath), 'a')
    file.write(
        './darknet detector train ' +
        dataFilePath + ' ' +
        configFilePath + ' ' +
        originalWheightPath +
        ' -dont_show -map'
    )
    file.close()

    os.chmod(filePath, 0o001)


##################################Execution#####################################

# # #Arguments# # #

if len(sys.argv) > 1:
    dossierproduit = sys.argv[1]
else:
    print("No path given")
    quit()
if len(sys.argv) > 2:
    entree = sys.argv[2]
if len(sys.argv) > 3:
    images = sys.argv[3]

# # #Créations des dossiers# # #

pathimages = dossierproduit + "/images"
pathbackup = dossierproduit + "/images/backup"
pathtest = dossierproduit + "/images/test"
pathtrain = dossierproduit + "/images/train"
pathconfig = dossierproduit + "/config"
if not os.path.exists(dossierproduit):
    os.mkdir(dossierproduit)
    if not os.path.exists(pathimages):
        os.mkdir(pathimages)
        if not os.path.exists(pathbackup):
            os.mkdir(pathbackup)
            if not os.path.exists(pathtest):
                os.mkdir(pathtest)
                if not os.path.exists(pathtrain):
                    os.mkdir(pathtrain)
                    if not os.path.exists(pathconfig):
                        os.mkdir(pathconfig)
                    else:
                        print("Erreur interne 1.4")
                        quit()
                else:
                    print("Erreur interne 1.3")
                    quit()
            else:
                print("Erreur interne 1.2")
                quit()
        else:
            print("Erreur interne 1.1")
            quit()
    else:
        print("Erreur interne 1")
        quit()
    if not os.path.exists(dossierproduit + "/configuration"):
        os.mkdir(dossierproduit + "/configuration")

else:
    print('A directory is already named as the directory aimed. Please delete it or change your destination path')
    quit()

if not os.path.isfile(entree):
    print("The file defined as input do not exist")
    quit()

data = chargement_source(entree)
make_txt_yolo_from_coco_bbox(data, pathtrain, correspondancesObjets)
dispatch(pathtest, pathtrain, images, data)
create_names(correspondancesNoms, pathconfig + 'classes.names\n')
create_data_txt(
    pathtest, pathtrain, pathbackup, len(correspondancesObjets), pathconfig
)
create_script()