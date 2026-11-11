import pandas as pd

excel_file = 'lame_duck_congress_tracker.xlsx'
df = pd.read_excel(excel_file, sheet_name='Tracker')

def update_priority(row):
    if row['Category'] in ['Defeated in November', 'Lost primary']:
        return 1
    elif row['Category'] == 'Retiring':
        return 2
    else:
        return 3

df['Priority'] = df.apply(update_priority, axis=1)
df = df.sort_values(by=['Priority', 'State', 'Member']).reset_index(drop=True)

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Tracker', index=False)

print("Tracker updated successfully!")