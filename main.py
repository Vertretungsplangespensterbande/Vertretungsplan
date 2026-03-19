import streamlit as st
import pandas as pd
import requests as r
import datetime

st.set_page_config(layout="wide")

tag = st.selectbox("Tag", ["Heute", "Morgen"])

if tag == "Heute":
    full_date = datetime.datetime.today()
if tag == "Morgen":
    full_date = datetime.date.today() + datetime.timedelta(days=1)

# %d = day; %m = month; %Y = full year
date = full_date.strftime("%Y%m%d")
display_date = full_date.strftime("%d.%B %Y")

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

response = r.post(url, json = request_body)

json_response = response.json()
print(json_response)

dataframe = pd.DataFrame(data=json_response["payload"]["rows"]) 
dataframe = dataframe.drop(["cellClasses", "cssClasses"], axis=1)
dataframe.to_csv("plan_today.csv", index=False)

absent_elements = json_response["payload"]["absentElements"]
absent_classes = [klasse["elementName"] for klasse in absent_elements] 
    
absent_class_names = ", ".join(absent_classes)

groups_today = list(set(dataframe["group"].tolist()))
groups_today.sort()

st.write(display_date)

st.header("Vertretungsplan " + tag + ":")


st.write("Abwesend: " + str(absent_class_names)) 

st.write("In der Auswahlbox werden die Klassen angezeigt, die heute auf dem Plan stehen. Wenn deine nicht dabei ist, brauchst du gar nicht erst gucken... Der Inhalt ist derselbe wie auf der Website in Iserv.")
group = st.selectbox("Klasse", groups_today)

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
    st.table(table_frame)




