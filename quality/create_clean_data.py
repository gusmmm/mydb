#!/usr/bin/env python3
"""
BD_doentes Clean Data Generator

This script creates BD_doentes_clean.csv from BD_doentes.csv according to the specifications
in BD_doentes.md. It performs data transformations, calculations, and generates a clean
dataset for analysis.

Created: September 2025
Author: Data Quality Control System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import shutil
from typing import Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID

console = Console()

def _parse_date_loose(date_str: str) -> Optional[datetime]:
    """Parse date with multiple format fallbacks."""
    if pd.isna(date_str) or str(date_str).strip() == '':
        return None
    
    date_str = str(date_str).strip()
    
    # Try strict DD-MM-YYYY first
    if _is_strict_dd_mm_yyyy(date_str):
        try:
            return datetime.strptime(date_str, '%d-%m-%Y')
        except ValueError:
            pass
    
    # Fallback formats
    formats = [
        '%d-%m-%Y',      # DD-MM-YYYY
        '%Y-%m-%d',      # YYYY-MM-DD  
        '%d/%m/%Y',      # DD/MM/YYYY
        '%d.%m.%Y',      # DD.MM.YYYY
        '%d-%m-%y',      # DD-MM-YY
        '%d/%m/%y',      # DD/MM/YY
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            # Handle 2-digit years
            if parsed.year < 1950:
                parsed = parsed.replace(year=parsed.year + 100)
            return parsed
        except ValueError:
            continue
    
    return None

def _is_strict_dd_mm_yyyy(date_str: str) -> bool:
    """Check if date matches strict DD-MM-YYYY format."""
    if not isinstance(date_str, str):
        return False
    
    parts = date_str.split('-')
    if len(parts) != 3:
        return False
    
    day, month, year = parts
    
    # Check format: DD-MM-YYYY
    return (len(day) == 2 and day.isdigit() and
            len(month) == 2 and month.isdigit() and
            len(year) == 4 and year.isdigit())

def extract_year_and_serial(id_value: int) -> Tuple[int, int]:
    """
    Extract year and serial_id from ID according to specification:
    - 3 digits: first digit = year (8 -> 2008), last 2 = serial
    - 4 digits: first 2 = year (11 -> 2011), last 2 = serial
    """
    id_str = str(id_value)
    
    if len(id_str) == 3:
        # 3 digits: first digit is year, last 2 are serial
        year_digit = int(id_str[0])
        year = 2000 + year_digit  # 8 -> 2008, 9 -> 2009
        serial_id = int(id_str[1:])  # Last 2 digits
    elif len(id_str) == 4:
        # 4 digits: first 2 are year, last 2 are serial
        year_digits = int(id_str[:2])
        year = 2000 + year_digits  # 11 -> 2011, 24 -> 2024
        serial_id = int(id_str[2:])  # Last 2 digits
    else:
        # Unexpected format, default to ID as year and 0 as serial
        console.print(f"⚠️ Unexpected ID format: {id_value}")
        year = 2000 + (id_value // 100)  # Estimate
        serial_id = id_value % 100
    
    return year, serial_id

def calculate_age_years(birth_date: Optional[datetime], admission_date: Optional[datetime]) -> Optional[int]:
    """Calculate age in years from birth date to admission date."""
    if birth_date is None or admission_date is None:
        return None
    
    age = admission_date.year - birth_date.year
    
    # Adjust if birthday hasn't occurred yet this year
    if (admission_date.month, admission_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return max(0, age)  # Ensure non-negative

def calculate_days_difference(later_date: Optional[datetime], earlier_date: Optional[datetime]) -> Optional[int]:
    """Calculate difference in days between two dates."""
    if later_date is None or earlier_date is None:
        return None
    
    return (later_date - earlier_date).days

def backup_existing_file(file_path: Path) -> bool:
    """Backup existing file with timestamp if it exists."""
    if not file_path.exists():
        return False
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
    
    try:
        shutil.move(str(file_path), str(backup_path))
        console.print(f"📋 Backed up existing file to: {backup_path.name}")
        return True
    except Exception as e:
        console.print(f"❌ Error backing up file: {e}")
        return False

def create_clean_dataset():
    """Create BD_doentes_clean.csv from BD_doentes.csv."""
    
    console.print(Panel.fit(
        "🏥 BD_doentes Clean Data Generator\n"
        "Creating clean dataset from BD_doentes.csv",
        style="bold green"
    ))
    
    # File paths
    source_file = Path("/home/gusmmm/Desktop/mydb/files/csv/BD_doentes.csv")
    target_file = Path("/home/gusmmm/Desktop/mydb/files/csv/BD_doentes_clean.csv")
    
    # Check source file exists
    if not source_file.exists():
        console.print(f"❌ Source file not found: {source_file}")
        return False
    
    # Backup existing clean file if present
    if target_file.exists():
        backup_existing_file(target_file)
    
    # Load source data
    console.print(f"📂 Loading source data from: {source_file.name}")
    try:
        df = pd.read_csv(source_file)
        console.print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        console.print(f"❌ Error loading CSV: {e}")
        return False
    
    with Progress() as progress:
        task = progress.add_task("Processing data transformations...", total=100)
        
        # Create clean dataframe with specified columns
        clean_df = pd.DataFrame()
        
        # Copy ID column
        progress.update(task, advance=5, description="Processing ID column...")
        clean_df['ID'] = df['ID']
        
        # Extract year and serial_id from ID
        progress.update(task, advance=10, description="Extracting year and serial_id...")
        year_serial = df['ID'].apply(lambda x: extract_year_and_serial(x) if pd.notna(x) else (None, None))
        clean_df['year'] = [item[0] for item in year_serial]
        clean_df['serial_id'] = [item[1] for item in year_serial]
        
        # Copy direct columns
        progress.update(task, advance=15, description="Copying direct columns...")
        direct_columns = ['processo', 'nome', 'data_ent', 'data_alta', 'destino', 'sexo', 'data_nasc', 'data_queim', 'origem', 'ASCQ', 'etiologia']
        for col in direct_columns:
            if col in df.columns:
                clean_df[col] = df[col]
            else:
                console.print(f"⚠️ Column {col} not found in source data")
                clean_df[col] = None
        
        # Copy and rename ent_VMI to env_VMI  
        progress.update(task, advance=20, description="Processing VMI column...")
        if 'ent_VMI' in df.columns:
            clean_df['env_VMI'] = df['ent_VMI']
        else:
            console.print("⚠️ Column ent_VMI not found in source data")
            clean_df['env_VMI'] = None
        
        # Copy lesao_inal
        progress.update(task, advance=25, description="Processing lesao_inal...")
        if 'lesao_inal' in df.columns:
            clean_df['lesao_inal'] = df['lesao_inal']
        else:
            console.print("⚠️ Column lesao_inal not found in source data")
            clean_df['lesao_inal'] = None
        
        # Calculate idade (age in years)
        progress.update(task, advance=40, description="Calculating idade (age)...")
        clean_df['idade'] = None
        
        for idx, row in df.iterrows():
            birth_date = _parse_date_loose(row.get('data_nasc'))
            admission_date = _parse_date_loose(row.get('data_ent'))
            age = calculate_age_years(birth_date, admission_date)
            clean_df.loc[idx, 'idade'] = age
        
        # Calculate dias_queim (days from burn to admission)
        progress.update(task, advance=60, description="Calculating dias_queim...")
        clean_df['dias_queim'] = None
        
        for idx, row in df.iterrows():
            burn_date = _parse_date_loose(row.get('data_queim'))
            admission_date = _parse_date_loose(row.get('data_ent'))
            days_diff = calculate_days_difference(admission_date, burn_date)
            clean_df.loc[idx, 'dias_queim'] = days_diff
        
        # Calculate BAUX score (ASCQ + idade)
        progress.update(task, advance=80, description="Calculating BAUX score...")
        clean_df['BAUX'] = None
        
        for idx, row in clean_df.iterrows():
            ascq = row.get('ASCQ')
            idade = row.get('idade')
            
            # Parse ASCQ if it's a string (handle decimal values)
            if pd.notna(ascq):
                try:
                    if isinstance(ascq, str):
                        # Handle decimal comma/point variations
                        ascq_cleaned = str(ascq).replace(',', '.')
                        ascq_float = float(ascq_cleaned)
                    else:
                        ascq_float = float(ascq)
                    
                    # Calculate BAUX if both values are available
                    if pd.notna(idade) and 1 <= ascq_float <= 100:
                        baux_score = ascq_float + idade
                        clean_df.loc[idx, 'BAUX'] = round(baux_score, 1)
                except (ValueError, TypeError):
                    pass  # Keep as None if parsing fails
        
        progress.update(task, advance=100, description="Finalizing dataset...")
    
    # Display summary statistics
    console.print("\n" + "="*60)
    console.print("📊 Clean Dataset Summary")
    console.print("="*60)
    
    summary_table = Table(title="Column Summary", show_header=True, header_style="bold magenta")
    summary_table.add_column("Column", style="cyan")
    summary_table.add_column("Non-null Count", justify="right")
    summary_table.add_column("Missing Count", justify="right") 
    summary_table.add_column("Missing %", justify="right")
    
    total_rows = len(clean_df)
    
    for col in clean_df.columns:
        non_null = clean_df[col].notna().sum()
        missing = total_rows - non_null
        missing_pct = (missing / total_rows) * 100 if total_rows > 0 else 0
        
        summary_table.add_row(
            col,
            str(non_null),
            str(missing),
            f"{missing_pct:.1f}%"
        )
    
    console.print(summary_table)
    
    # Sample of calculated values
    console.print(f"\n📋 Sample of calculated values (first 5 rows):")
    sample_cols = ['ID', 'year', 'serial_id', 'idade', 'dias_queim', 'BAUX']
    sample_table = Table(show_header=True, header_style="bold blue")
    
    for col in sample_cols:
        sample_table.add_column(col, style="white")
    
    for idx in range(min(5, len(clean_df))):
        row_data = []
        for col in sample_cols:
            value = clean_df.iloc[idx][col]
            if pd.isna(value):
                row_data.append("—")
            else:
                row_data.append(str(value))
        sample_table.add_row(*row_data)
    
    console.print(sample_table)
    
    # Save clean dataset
    try:
        clean_df.to_csv(target_file, index=False)
        console.print(f"\n✅ Clean dataset saved successfully!")
        console.print(f"📄 File: {target_file}")
        console.print(f"📊 Rows: {len(clean_df)}")
        console.print(f"📋 Columns: {len(clean_df.columns)}")
        
        # Validation checks
        console.print(f"\n🔍 Validation Summary:")
        console.print(f"• Year range: {clean_df['year'].min()}-{clean_df['year'].max()}")
        console.print(f"• Serial ID range: {clean_df['serial_id'].min()}-{clean_df['serial_id'].max()}")
        console.print(f"• Age range: {clean_df['idade'].min()}-{clean_df['idade'].max()}")
        console.print(f"• BAUX scores calculated: {clean_df['BAUX'].notna().sum()}/{len(clean_df)}")
        console.print(f"• Days from burn calculated: {clean_df['dias_queim'].notna().sum()}/{len(clean_df)}")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Error saving clean dataset: {e}")
        return False

if __name__ == "__main__":
    success = create_clean_dataset()
    if success:
        console.print(f"\n🎉 BD_doentes_clean.csv created successfully!")
    else:
        console.print(f"\n💥 Failed to create clean dataset")