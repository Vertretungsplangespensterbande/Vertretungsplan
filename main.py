import streamlit as st
import pandas as pd
import requests as r
import datetime

st.set_page_config(layout="wide")

#Datum je nach gewünschtem Tag setzen 
tag = st.selectbox("Tag", ["Heute", "Morgen"])
if tag == "Heute":
    full_date = datetime.datetime.today()
if tag == "Morgen":
    full_date = datetime.date.today() + datetime.timedelta(days=1)
# %d = day; %m = month; %Y = full year
date = full_date.strftime("%Y%m%d")
display_date = full_date.strftime("%d.%B %Y")

#Anfrage mit richtigem Datum etc. schicken
url = "https://hh5655.webuntis.com/WebUntis/monitor/substitution/data?school=hh5655"
request_body = {"formatName":"schueler",
                "schoolName":"hh5655",
                "date": date,
                "dateOffset":0,
                "strikethrough":True,
                "mergeBlocks":True,
                "showOnlyFutureSub":False,
                "showBreakSupervisions":False,
                "showTeacher":True,
                "showClass":True,
                "showHour":True,
                "showInfo":True,
                "showRoom":True,
                "showSubject":True,
                "groupBy":1,
                "hideAbsent":True,
                "departmentIds":[],
                "departmentElementType":1,
                "hideCancelWithSubstitution":False,
                "hideCancelCausedByEvent":False,
                "showTime":True,
                "showSubstText":True,
                "showAbsentElements":[1],
                "showAffectedElements":[1],
                "showUnitTime":False,
                "showMessages":False,
                "showStudentgroup":False,
                "enableSubstitutionFrom":False,
                "showSubstitutionFrom":1200,
                "showTeacherOnEvent":False,
                "showAbsentTeacher":False,
                "strikethroughAbsentTeacher":False,
                "activityTypeIds":[4],
                "showEvent":True,
                "showCancel":True,
                "showOnlyCancel":False,
                "showSubstTypeColor":False,
                "showExamSupervision":False,
                "showUnheraldedExams":False}

#Antwort zu json 
response = r.post(url, json = request_body)
json_response = response.json()

#Überprüfen im developer-Umfeld 
#print(json_response)

#Datum anzeigen
st.write(display_date)
#Tabelle (Dataframe) aus json
dataframe = pd.DataFrame(data=json_response["payload"]["rows"]) 
#Überprüfen, ob es heute vertretungen gibt (ob df empty ist)
if dataframe.empty: 
    #anzeigen, dass er leer ist
    if tag == "Heute":
        st.header("Heute keine Vertretungen")
    elif tag == "Morgen":
        st.header("Morgen keine Vertretungen")
    else:
        st.header("Für das eingebene Datum liegt keine Information vor.")
else:
    #Überschrift anzeigen 
    st.header("Vertretungsplan " + tag + ":")

    #Dataframe vorbereiten 
    dataframe = dataframe.drop(["cellClasses", "cssClasses"], axis=1)
    dataframe.to_csv("plan_today.csv", index=False)

    #Abwesende Klassen
    absent_elements = json_response["payload"]["absentElements"]
    absent_classes = [klasse["elementName"] for klasse in absent_elements]   
    absent_class_names = ", ".join(absent_classes)
    st.write("Abwesend: " + str(absent_class_names)) 

    #Kontext zur Auswahlbox + Auswahlbox
    st.write("In der Auswahlbox werden die Klassen angezeigt, die heute auf dem Plan stehen. Wenn deine nicht dabei ist, brauchst du gar nicht erst gucken... Der Inhalt ist derselbe wie auf der Website in Iserv.")
    groups_today = list(set(dataframe["group"].tolist()))
    groups_today.sort()
    group = st.selectbox("Klasse", groups_today)

    #Vorbereitung Plan mit Auswahlbox
    filtered_frame = dataframe[dataframe["group"] == group]
    filtered_frame = filtered_frame["data"]

    if filtered_frame.empty == True:
        st.write("Deine Klasse steht nicht auf dem Vertretungsplan!")
    else: 
        number_rows = filtered_frame.shape[0]
        table_columns = ["Stunde", "Zeit", "Klassen", "Fach", "Raum", "Lehrkraft", "Kommentar"]
        table_dict = {x: [] for x in table_columns}
        for i in range(0, number_rows):
            data = filtered_frame.iloc[i]
            
            #"Cancelstyle" usw ersetzen
            for (column,section) in zip(table_columns,data):
                if "<span" in section:
                    #<span class=""substMonitorSubstElem"">---</span> (<span class=""cancelStyle"">Ge</span>)
                    #<span class=""substMonitorSubstElem"">F106</span> (D13)
                    #<span class=""substMonitorSubstElem"">Kor</span> (<span class=""cancelStyle"">Aga</span>)
                    section = section.replace('"',"")
                    section = section.replace("<span class=substMonitorSubstElem>", "")    
                    section = section.replace("</span>", "")
                    if column == "Lehrkraft":
                        section = section.replace(" (<span class=cancelStyle>", " / ~")
                        section = section.replace(")", "~")
                    if column == "Raum":
                        section = section.replace("(", "~")
                        section = section.replace(")", "~")
                table_dict[column] += [section]
        table_frame = pd.DataFrame.from_dict(table_dict, "columns")

        #Plan anzeigen
        st.table(table_frame)




