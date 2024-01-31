# Description: Script to calculate GPA from PDF file with grades
# Author: Victor Colella
# Email: victorcgcpereira@gmail.com
# Date: 2021-01-01

import eel
import pdfplumber
import re
import pandas as pd
import numpy as np
import io

eel.init("static")


@eel.expose
def calculate_gpa(document_content):
    table_data = extract_table_from_pdf(bytes(document_content))
    df = pd.DataFrame(
        columns=["code", "name", "grade", "credits_hour", "credits", "other"]
    )
    pattern = r"(?P<code>[A-Z]{1,2}\s{0,1}\d{1,3})\s+(?P<name>.+?)\s+(?P<grade>\d+,\d+)\s+(?P<ch>\d+)\s+(?P<crd>\d+)\s+(?P<other_info>.+)"

    for i in table_data:
        for j in i:
            for k in j:
                # Access the captured groups
                if k is not None:
                    match = re.match(pattern, "".join([item for item in k if item]))
                    # print(''.join([item for item in k if item]))
                    if match and "Aprovado" in match.group("other_info"):
                        course_code = match.group("code")
                        course_name = match.group("name")
                        grade = match.group("grade")
                        ch = match.group("ch")
                        crd = match.group("crd")
                        other_info = match.group("other_info").strip()
                        df.loc[len(df)] = [
                            course_code,
                            course_name,
                            float(grade.replace(",", ".")),
                            int(ch),
                            int(crd),
                            other_info,
                        ]
    df["grade_US"] = df["grade"].apply(lambda x: 4 if x >= 9 else 3 if x >= 7 else 2 if x >= 5 else 1 if x >= 3 else 0)
    df.to_csv("grades.csv")
    return np.sum(df["credits"] * df["grade"]) / df["credits"].sum(), np.sum(df["credits"] * df["grade_US"]) / df["credits"].sum()


def extract_table_from_pdf(content, page_number=0):
    tables = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            tables.append(page.extract_tables())
        return tables


eel.start("main_page.html")
