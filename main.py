import streamlit as st
import pandas as pd
import requests as r
import datetime

full_date = datetime.datetime.now()
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
                "showOnlyFutureSub":True,
                "showBreakSupervisions":False,
                "showTeacher":True,
                "showClass":True,
                "showHour":True,
                "showInfo":False,
                "showRoom":True,
                "showSubject":True,
                "groupBy":1,
                "hideAbsent":False,
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
                "showAbsentTeacher":True,
                "strikethroughAbsentTeacher":True,
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
dataframe.to_csv("plan_2.csv", index=False)

groups_today = list(set(dataframe["group"].tolist()))
groups_today.sort()

st.write(display_date)

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
            if section.startswith("<span"):
                #<span class=""substMonitorSubstElem"">---</span> (<span class=""cancelStyle"">Ge</span>)
                #<span class=""substMonitorSubstElem"">F106</span> (D13)
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




