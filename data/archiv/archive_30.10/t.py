import pandas as pd

# Create data with room classifications
data = {
    'Room Number': [
        # A Section
        '1A01', '1A02', '1A03', '1A04', '1A05', '1A06', '1A07', '1A08', '1A09', '1A10',
        '1A11', '1A12', '1A13', '1A14', '1A15', '1A16',
        # B Section
        '1B01', '1B02', '1B03', '1B04', '1B05', '1B06', '1B07', '1B08', '1B09', '1B10',
        '1B11', '1B12', '1B13', '1B14', '1B15', '1B16', '1B17', '1B19', '1B21', '1B23',
        # C Section
        '1C01', '1C02', '1C03', '1C04', '1C05', '1C06', '1C07', '1C08', '1C09', '1C10',
        '1C11', '1C12', '1C13', '1C14', '1C15', '1C16', '1C17', '1C18', '1C19',
        # D Section
        '1D01', '1D02', '1D03', '1D04', '1D05', '1D06', '1D07', '1D08', '1D09', '1D10',
        '1D11', '1D13', '1D14', '1D15', '1D16', '1D17', '1D18', '1D19', '1D20', '1D21',
        '1D22', '1D23', '1D24', '1D25', '1D27', '1D28', '1D30', '1D31', '1D32', '1D33',
        '1D34', '1D35', '1D36', '1D37', '1D38', '1D39', '1D40',
        # E Section
        '1E01', '1E02', '1E03', '1E04', '1E05', '1E06', '1E07', '1E08', '1E09', '1E10',
        '1E11', '1E12', '1E14', '1E15', '1E15-A', '1E16', '1E17', '1E18', '1E19', '1E20',
        '1E21', '1E22', '1E23', '1E24', '1E25', '1E26', '1E27', '1E28', '1E29', '1E30',
        '1E33'
    ],
    'Room Name': [
        # A Section
        'PATIENT ADMIN. RECEPT.', 'RMO ANALYST', 'TRICARE OFFICE', 'TRICARE OFFICE',
        'TRICARE OFFICE', 'TRICARE OFFICE', 'TRICARE OFFICE', 'PHARM. OFFICE',
        'W. TOILET', 'LOUNGE', 'JAN.', 'M. TOILET', 'STAFF TOILET', 'SUPER/NCOIC',
        'COUNSELING', 'PHARM. DISP.',
        # B Section
        'RECEPTION', 'SPECIMEN TOILET', 'BLOOD DRAW', 'LAB', 'PAT./STAFF TOILET',
        'LAB OFFICE', 'DRESS', 'CENT. STO.', 'DRESS', 'STAFF LOUNGE', 'STAFF TOILET',
        'CLEAN SUP. & EQUIP.', 'RECEPTION', 'SOIL. UTL.', 'FILM VIEW', 'JAN. CL.',
        'RADIOGRAPHIC ROOM', 'TECH. WORK ROOM', 'COMM. ROOM', 'ELEC. ROOM',
        # C Section
        'WAITING', 'RECEPTION', 'JAN. CL.', 'FITTING/DISP.', 'VISUAL FIELD',
        'SOIL. UTL./TRASH', 'OPT. EXAM/OFF.', 'SCREEN EYE TEST', 'FUNDUS CAMERA ROOM',
        'OPT. EXAM/OFF.', 'ELEC. CL.', 'TOILET', 'COMM. ROOM', 'HIST./INTV.',
        'PES ADMIN. OFFICE', 'ECG TEST', 'CHIEF AERO MED.', 'PHYSICAL EXAM', 'AUDIO',
        # D Section
        'SL. LIN./TRASH', 'INTERACTION STATION', 'CLEAN U.', 'TOILET',
        'TRMT RM. DIRTY PROC.', 'SCOPE WASH/DECON.', 'INTERACTION STATION',
        'INTERACTION STATION', 'INTERACTION STATION', 'INTERACTION STATION',
        'INTERACTION STATION', 'INTERACTION STATION', 'SPECIMEN TOILET',
        'WTS & MEAS. ROOM', 'PROVIDER CUBICLES', 'JAN. CL.', 'TOILET', 'MDIS VIEW',
        'APPMTS', 'GROUP IS', 'TEAM INTERACTION', 'GROUP IS', 'RECORDS',
        'PROVIDER CUBICLES', 'ADMIN WORK STATN.', 'INTERACTION STATION',
        'PEDIATRIC WTS & MSRS', 'INTERACTION STATION', 'PEDIATRIC WAITING',
        'INTERACTION STATION', 'INTERACTION STATION', 'INTERACTION STATION', 'CLEAN U.',
        'TRMT ROOM', 'JAN. CL.', 'IMMUNIZ\'N ROOM', 'IMMUNIZ\'N ROOM',
        # E Section
        'HK EQUIP. STORAGE', 'ELEV. EQUIP.', 'JAN. CL.', 'HK BREAK ROOM',
        'CHIEF LOG OFFICE', 'TECH. WORK STATION', 'CONF. LIBRARY', 'SUPER', 'M. TOILET',
        'W. TOILET', 'STAFF LOUNGE', 'ISOLATION TOILET', 'DISASTER STOR.',
        'CENTRAL MECH. RM.', 'GAS STORAGE', 'BMET WORK STATION', 'HAZ. STOR.',
        'BIOMED MAINT. ADMIN.', 'ELEC. ROOM', 'TRASH', 'FLAMABLE STORAGE',
        'SEC. STORAGE', 'BEE EQUIP. STORAGE', 'RECEIVING/STORAGE', 'ADP EQUIP SPACE',
        'WORK ROOM', 'BENCHSTOCK STORAGE', 'FAC. MGR. OFFICE', 'HK. SUPV. OFFICE',
        'SOIL. LIN.', 'ISOLATION INTERACTION STATION'
    ],
    'Zone Classification': [
        # A Section
        'Administrative', 'Administrative', 'Administrative', 'Administrative',
        'Administrative', 'Administrative', 'Administrative', 'Administrative',
        'Support Facilities', 'Support Facilities', 'Support Facilities',
        'Support Facilities', 'Support Facilities', 'Administrative', 'Clinical',
        'Clinical Support',
        # B Section
        'Administrative', 'Clinical Support', 'Clinical/Diagnostic', 'Clinical/Diagnostic',
        'Support Facilities', 'Administrative', 'Support Facilities', 'Support Facilities',
        'Support Facilities', 'Support Facilities', 'Support Facilities',
        'Clinical Support', 'Administrative', 'Support Facilities', 'Clinical/Diagnostic',
        'Support Facilities', 'Clinical/Diagnostic', 'Clinical Support', 'Support Facilities',
        'Support Facilities',
        # C Section
        'Support Facilities', 'Administrative', 'Support Facilities', 'Clinical',
        'Clinical/Diagnostic', 'Support Facilities', 'Clinical', 'Clinical/Diagnostic',
        'Clinical/Diagnostic', 'Clinical', 'Support Facilities', 'Support Facilities',
        'Support Facilities', 'Clinical', 'Administrative', 'Clinical/Diagnostic',
        'Administrative', 'Clinical', 'Clinical/Diagnostic',
        # D Section
        'Support Facilities', 'Clinical', 'Clinical Support', 'Support Facilities',
        'Clinical', 'Clinical Support', 'Clinical', 'Clinical', 'Clinical', 'Clinical',
        'Clinical', 'Clinical', 'Clinical Support', 'Clinical Support',
        'Administrative', 'Support Facilities', 'Support Facilities', 'Clinical Support',
        'Administrative', 'Clinical', 'Administrative', 'Clinical', 'Administrative',
        'Administrative', 'Administrative', 'Clinical', 'Clinical Support', 'Clinical',
        'Support Facilities', 'Clinical', 'Clinical', 'Clinical', 'Clinical Support',
        'Clinical', 'Support Facilities', 'Clinical', 'Clinical',
        # E Section
        'Support Facilities', 'Support Facilities', 'Support Facilities',
        'Support Facilities', 'Administrative', 'Administrative', 'Administrative',
        'Administrative', 'Support Facilities', 'Support Facilities', 'Support Facilities',
        'Support Facilities', 'Support Facilities', 'Support Facilities',
        'Support Facilities', 'Administrative', 'Support Facilities', 'Administrative',
        'Support Facilities', 'Support Facilities', 'Support Facilities',
        'Support Facilities', 'Support Facilities', 'Support Facilities',
        'Administrative', 'Administrative', 'Support Facilities', 'Administrative',
        'Administrative', 'Support Facilities', 'Clinical'
    ],
    'Section': [
        # A Section
        'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A',
        # B Section
        'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B',
        'B', 'B', 'B', 'B',
        # C Section
        'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C',
        'C', 'C', 'C',
        # D Section
        'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D',
        'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D',
        'D', 'D', 'D', 'D', 'D',
        # E Section
        'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E',
        'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E', 'E'
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Sort by Room Number
df = df.sort_values('Room Number')

# Save to Excel with formatting
with pd.ExcelWriter('medical_facility_rooms.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Room Classification', index=False)

    # Get workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Room Classification']

    # Add some formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D3D3D3',
        'border': 1
    })

    cell_format = workbook.add_format({
        'border': 1
    })

    # Format the header
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    # Format all cells
    for row in range(1, len(df) + 1):
        for col in range(len(df.columns)):
            worksheet.write(row, col, df.iloc[row - 1, col], cell_format)

    # Set column widths
    worksheet.set_column('A:A', 12)  # Room Number
    worksheet.set_column('B:B', 30)  # Room Name
    worksheet.set_column('C:C', 20)  # Zone Classification
    worksheet.set_column('D:D', 10)  # Section