import pandas as pd
import json
import re
import csv

questions = pd.read_csv('ctf_questions.csv')
answers = pd.read_csv('ctf_answers.csv')
hints = pd.read_csv('ctf_hints.csv')

def create_hint_json(group):
    hint_list = []
    for _, row in group.iterrows():
        hint_list.append({
            "content": str(row['Hint']).strip(),
            "cost": int(row['HintCost']) if pd.notnull(row['HintCost']) else 0
        })
    return json.dumps(hint_list)

hints_grouped = hints.groupby('Number').apply(create_hint_json).reset_index(name='HintsJSON')

def format_flag(answer):
    if pd.isnull(answer):
        return ""
    ans_str = str(answer).strip()
    ans_str = ans_str.replace(',', r'\,')
    escaped_ans = re.escape(ans_str).replace(r'\\,', r'\,')
    return f"(?i)^{escaped_ans}$"

answers['FormattedAnswer'] = answers['Answer'].apply(format_flag)
answers_grouped = answers.groupby('Number')['FormattedAnswer'].apply(lambda x: x.iloc[0]).reset_index()

merged = questions.merge(answers_grouped, on='Number', how='left')
merged = merged.merge(hints_grouped, on='Number', how='left')

ctfd_final = pd.DataFrame()
ctfd_final['name'] = "Challenge " + merged['Number'].astype(str)
ctfd_final['description'] = merged['Question']
ctfd_final['value'] = merged['BasePoints'].fillna(0).astype(int)
ctfd_final['type'] = "standard"
ctfd_final['state'] = "visible"
ctfd_final['flags'] = merged['FormattedAnswer']
ctfd_final['hints'] = merged['HintsJSON'].fillna('[]')

ctfd_final.to_csv('bots_for_ctfd.csv', index=False, quoting=csv.QUOTE_ALL)

print("Conversion complete: bots_for_ctfd.csv created.")
print("Reminder: Ensure Flag Type is set to 'regex' in CTFd for these challenges.")
