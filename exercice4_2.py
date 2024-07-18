# *******************************************************
# Nom ......... : Mon application Streamlit - Exif
# Role ........ : Application streamlit qui permet de modifier les données EXIF d'une image (déterminée), sur l'appareil, la date et le lieu de la prise de vue. S'y trouve aussi une carte avec les lieux, reliés entre eux, que j'ai parcouru.
# Auteur ...... : Damien Lebrun
# Version ..... : V0.1 du 18/07/2024
# Licence ..... : realisation dans le cadre du cours de OC
# (../..)
# Compilation : -
# Usage : execution : ./streamlit run exercice4_2.py
#********************************************************/

import streamlit as st
from exif import Image
from datetime import datetime
from streamlit_folium import st_folium
import folium

##FONCTIONS UTILES
#Fonction qui convertit une chaîne en un tuple de trois nombres, utile pour les chaînes de coordonnées GPS à reformater.
def string_to_tupleInt(liste_string):
    nombres = liste_string.strip('()')
    tuple_nombres = tuple(float(elt) for elt in nombres.split(', '))
    return tuple_nombres

#Fonction de conversion des données de GPS au format sexagésimal (fourni par exif) vers la forme décimale (necessitée par folium)
def sexa_to_decimal(nombres):
    multiplicateur = 1
    decimal = 0
    for nombre in nombres:
        nombre = nombre / multiplicateur
        decimal += nombre
        multiplicateur *= 60
    return decimal

##L'APPLICATION
#Les deux colonnes principales de la structure de l'application
col_image, col_input = st.columns(2)

#récupération de la photo
with open('shika.jpg', 'rb') as image_file:
    mon_image = Image(image_file)

#Création d'un dictionnaire avec chaque type d'information exif et sa valeur pour simplifier leur manipulation.
informations = {}
for element in mon_image.list_all():
    informations[element] = mon_image.get(element)

print(informations) #Un print qui m'a été bien utile pour observer les modifications depuis le terminal, mais qui peut être supprimé.

#Insertion des différents composants graphique de l'application
with col_image:
    st.image('shika.jpg', width=250)



st.header("Généralités")

with col_input:
    description = st.text_input("Description de l'image", informations['image_description'])
    marque = st.text_input("Marque du téléphone", value = informations['make'])
    modele = st.text_input("Modèle du téléphone", value = informations['model'])



st.header("Coordonnées GPS")

image_latitude = st.text_input("Latitude", value = mon_image.gps_latitude)
image_latitude_ref = st.text_input("Référence de la latitude", value = mon_image.gps_latitude_ref)
image_longitude = st.text_input("Longitude", value = mon_image.gps_longitude)
image_longitude_ref = st.text_input("Référence de la longitude", value = mon_image.gps_longitude_ref)
image_altitude = st.text_input("Altitude", value = mon_image.gps_altitude)

st.header("Heure de prise de vue, et modifications")
#Format standard pour la conversion des chaînes en datetime, ou le formatage des combinaisons par datetime.combine
date_format = "%Y:%m:%d %H:%M:%S"

#Formatage en datetime pour afficher la valeur dans les composants st.date et st.time
date_prise_complet = datetime.strptime(informations['datetime_original'], date_format)
date_prise = st.date_input("Date de prise", value = date_prise_complet.date() )
heure_prise = st.time_input("Heure de prise", value = date_prise_complet.time())



st.header("Dernières retouches")

logiciel = st.text_input("Logiciel de création, de retouche", value= informations['software'])

derniere_date = datetime.strptime(informations['datetime'], date_format)
date_modif = st.date_input("Date de modification", value=derniere_date.date())
heure_modif = st.time_input("Heure de modification", value=derniere_date.time())


#Fonction de transmission des nouvelles données dans l'image
def modifier_exif():
    date_creation_formatee = datetime.combine(date_prise, heure_prise)
    date_creation_formatee = date_creation_formatee.strftime(date_format)
    date_modif_formatee = datetime.combine(date_modif, heure_modif)
    date_modif_formatee = date_modif_formatee.strftime(date_format)

    mon_image.set('image_description', description)
    mon_image.set('make', marque)
    mon_image.set('model', modele)
    mon_image.set('software', logiciel)
    mon_image.set('datetime_original', date_creation_formatee)
    #Modification des dates 'digitized' et du tampon GPS pour ne pas laisser de traces
    mon_image.set('datetime_digitized', date_creation_formatee)
    mon_image.set('gps_datestamp', date_creation_formatee)
    mon_image.set('datetime', date_modif_formatee)
    latitude_convertie = string_to_tupleInt(image_latitude)
    mon_image.gps_latitude = latitude_convertie
    mon_image.gps_latitude_ref = image_latitude_ref
    longitude_convertie = string_to_tupleInt(image_longitude)
    mon_image.gps_longitude = longitude_convertie
    mon_image.gps_longitude_ref = image_longitude_ref
    mon_image.gps_altitude = float(image_altitude)

    with open('shika.jpg', 'wb') as saved_file:
        saved_file.write(mon_image.get_file())


st.button("Appliquer les modifications", on_click=modifier_exif())


#Carte avec l'emplacement modifié de la photographie pour correspondre à mon emplacement actuel
st.header("Emplacement sur la carte")

#Conversion des données sexagésimale d'exif vers les données décimales pour folium
map_latitude = mon_image.gps_latitude
map_latitude = sexa_to_decimal(map_latitude)
map_longitude = mon_image.gps_longitude
map_longitude = sexa_to_decimal(map_longitude)

m = folium.Map(location=[map_latitude, map_longitude], zoom_start = 15)
folium.Marker(
    [map_latitude, map_longitude]).add_to(m)

st_data = st_folium(m, width=500, height=200)


#Carte de présentation des différents voyages que j'ai effectué.

voyage = folium.Map(location=[48.5400, 2.6550], zoom_start=4)

#Liste excessivement exhaustive
lieux = [
    ("Melun", [48.5400, 2.6550]),
    ("Lyon", [45.7640, 4.8357]),
    ("Paris", [48.8566, 2.3522]),
    ("Marseille", [43.2965, 5.3698]),
    ("Nice", [43.7102, 7.2620]),
    ("Tokyo", [35.6895, 139.6917]),
    ("Kyoto", [35.0116, 135.7681]),
    ("Kobe", [34.6901, 135.1955]),
    ("Nara", [34.6851, 135.8048]),
    ("Kagoshima", [31.5966, 130.5571]),
    ("Rabat", [34.0209, -6.8417]),
    ("Casablanca", [33.5731, -7.5898]),
    ("Agadir", [30.4278, -9.5981]),
    ("Marrakech", [31.6295, -7.9811]),
    ("Sofia", [42.6977, 23.3219]),
    ("Bucarest", [44.4268, 26.1025]),
    ("Osaka", [34.6937, 135.5023]),
    ("Stratford-upon-Avon", [52.1917, -1.7073]),
    ("Warwick", [52.2819, -1.5845]),
    ("Saint-Brieuc", [48.5146, -2.7656]),
    ("Plouha", [48.6839, -2.9442]),
    ("Tours", [47.3941, 0.6848]),
    ("Dijon", [47.3220, 5.0415]),
    ("Budapest", [47.4979, 19.0402])
]

#PolyLine, dont j'ai eu besoin pour relier les points, nécessite une liste avec seulement les lieux
coordonnees = [
    (48.5400, 2.6550),
    (45.7640, 4.8357),
    (48.8566, 2.3522),
    (43.2965, 5.3698),
    (43.7102, 7.2620),
    (35.6895, 139.6917),
    (35.0116, 135.7681),
    (34.6901, 135.1955),
    (34.6851, 135.8048),
    (31.5966, 130.5571),
    (34.0209, -6.8417),
    (33.5731, -7.5898),
    (30.4278, -9.5981),
    (31.6295, -7.9811),
    (42.6977, 23.3219),
    (44.4268, 26.1025),
    (34.6937, 135.5023),
    (52.1917, -1.7073),
    (52.2819, -1.5845),
    (48.5146, -2.7656),
    (48.6839, -2.9442),
    (47.3941, 0.6848),
    (47.3220, 5.0415),
    (47.4979, 19.0402)
]

#Insertion de chaque lieu visité dans un marqueur
for lieu, coordo in lieux:
    folium.Marker(
        location=coordo,
        popup=folium.Popup(lieu, parse_html=False)
    ).add_to(voyage)

#Traçage des lignes
folium.PolyLine(coordonnees, color="blue", weight=2.5).add_to(voyage)

out = st_folium(voyage, height=600)

st.write("Lieu :", out["last_object_clicked_popup"])
