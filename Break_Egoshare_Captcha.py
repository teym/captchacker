#!coding: utf-8
from svm import *
import os, sys
from PIL import Image
import time
import wx

#import psyco
#psyco.full()

from Preprocess import preprocess_captcha
from Preprocess import load_image
from svm import *
from svmutil import *

TEST = 0
VERBOSE = 0


def load_model(chemin, parent=None, fichier = ""):
    if not os.path.isfile(chemin):
        print 'The specified model file: \"'+chemin +'\" was not found. Aborting.'
        sys.exit(1)
    else:
        print "####################################################################################"
        print "\tLoading model ", chemin
        print "####################################################################################"
        if parent:
            parent.SetPathLabel("Loading model...")
        #model = svm_model(chemin)
        model = svm_load_model(chemin)
        print "Model successfully loaded."
        if parent:
            parent.SetPathLabel(fichier)
            parent.model = model
            parent.model_selected = True
    return model


def preprocess_captcha_part(file, folder=".", parent = None, remove=True):
    #Fait l'extraction �� partir de la starting position, sur une largeur length, et fait �ventuellement du preprocessing.

    if parent:
        beau_captcha = Image.open(file)
        w,h = beau_captcha.size
        beau_captcha = beau_captcha.convert('RGB').resize((parent.zoom*w, parent.zoom*h))

    if os.name == "nt":
        command = '""'+os.path.join(os.getcwd(), "Egoshare", 'Egoshare.exe" "'+file+'""')
    elif os.name == 'posix':
        command = os.path.join("\ ".join(os.getcwd().split(" ")) ,"Egoshare", "\ ".join('Egoshare Preprocessing'.split(' '))+" "+"\ ".join(file.split(" ")))
    else:
        print "OS type non supported"
        exit(2)
    os.system(command)


    letter1 = Image.open(os.path.join(os.getcwd(), "letter1.bmp")).copy()
    letter1_algo = letter1.point(lambda i: (i/255.))

    letter2 = Image.open(os.path.join(os.getcwd(), "letter2.bmp")).copy()
    letter2_algo = letter2.point(lambda i: (i/255.))

    letter3 = Image.open(os.path.join(os.getcwd(), "letter3.bmp")).copy()
    letter3_algo = letter3.point(lambda i: (i/255.))

    if remove:
        os.remove("letter1.bmp")
        os.remove("letter2.bmp")
        os.remove("letter3.bmp")

    if parent:
        w, h = letter1.size
        letter1 = letter1.convert('RGB').resize((parent.zoom*w, parent.zoom*h))
        letter2 = letter2.convert('RGB').resize((parent.zoom*w, parent.zoom*h))
        letter3 = letter3.convert('RGB').resize((parent.zoom*w, parent.zoom*h))
        return beau_captcha, letter1, letter2, letter3, letter1_algo, letter2_algo, letter3_algo
    else:
        return letter1_algo, letter2_algo, letter3_algo


def predict(model, im):
    data = list(im.getdata())
    prediction = model.predict(data)
    probability = model.predict_probability(data)

    if VERBOSE:
        print chr(65+int(prediction)), max(probability[1].values())
        #print probability

    return chr(65+int(prediction)), str(max(probability[1].values())), probability[1]



def break_captcha(model, letter1_algo, letter2_algo, letter3_algo, parent=None):
    liste_probas = []

    if not TEST:
        prediction1, max_score1, dico1 = predict(model, letter1_algo)
        prediction2, max_score2, dico2 = predict(model, letter2_algo)
        prediction3, max_score3, dico3 = predict(model, letter3_algo)
    else:
        prediction1, max_score1 = "M", "0.21313"
        prediction2, max_score2 = "M", "0.21313"
        prediction3, max_score3 = "M", "0.21313"

    if parent:
        parent.setResults(prediction1, max_score1, prediction2, max_score2, prediction3, max_score3, dico1, dico2, dico3)

    return prediction1+prediction2+prediction3





#TRACEBACK
import traceback
import sys
def Myexcepthook(type, value, tb):
        lines=traceback.format_exception(type, value, tb)
##        f=open('log.txt', 'a')
##        f.write("\n".join(lines))
##        f.close()
        print "\n".join(lines)
        raw_input()
        sys.exit(0)
sys.excepthook=Myexcepthook


def write(s):
    f=open("Egoshare/Models/Stats.txt", "a")
    f.write(s+"\n")
    f.close()
