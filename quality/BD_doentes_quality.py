#!/usr/bin/env python3
"""
Quality Control Script for BD_doentes.csv
Analyzes the ID column with beautiful colored terminal output
"""

import pandas as pd
import re
from collections import defaultdict, Counter
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.align import Align
from pathlib import Path

# Initialize Rich console
console = Console()

def load_data(file_path: str) -> pd.DataFrame:
    """Load the CSV file and return a pandas DataFrame"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading CSV data...", total=None)
            df = pd.read_csv(file_path)
            progress.update(task, completed=True)
        return df
    except Exception as e:
        console.print(f"[red]Error loading file: {e}[/red]")
        return None

def analyze_id_column(df: pd.DataFrame) -> dict:
    """Comprehensive analysis of the ID column"""
    
    # Initialize results dictionary
    results = {
        'total_rows': len(df),
        'empty_values': [],
        'invalid_format': [],
        'valid_3_digit': [],
        'valid_4_digit': [],
        'year_series': defaultdict(list),
        'missing_serials': defaultdict(list),
        'duplicate_ids': [],
        'statistics': {}
    }
    
    # Convert ID column to string to handle mixed types
    df['ID_str'] = df['ID'].astype(str)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing ID column...", total=len(df))
        
        for idx, row in df.iterrows():
            id_value = row['ID_str']
            row_number = idx + 2  # +2 because pandas is 0-indexed and CSV has header
            
            # Check for empty values
            if pd.isna(row['ID']) or id_value in ['', 'nan', 'None']:
                results['empty_values'].append({
                    'row': row_number,
                    'value': id_value,
                    'nome': row.get('nome', 'N/A')
                })
                progress.update(task, advance=1)
                continue
            
            # Check if it's a valid 3 or 4 digit number
            if not re.match(r'^\d{3,4}$', id_value):
                results['invalid_format'].append({
                    'row': row_number,
                    'value': id_value,
                    'nome': row.get('nome', 'N/A')
                })
                progress.update(task, advance=1)
                continue
            
            # Parse year and serial based on digits
            if len(id_value) == 3:
                year_digit = int(id_value[0])
                # Convert single digit to full year (0-9 -> 2000-2009)
                if year_digit == 0:
                    year = 2000 + year_digit
                else:
                    year = 2000 + year_digit
                serial = int(id_value[1:])
                results['valid_3_digit'].append({
                    'row': row_number,
                    'id': id_value,
                    'year': year,
                    'serial': serial,
                    'nome': row.get('nome', 'N/A')
                })
            elif len(id_value) == 4:
                year_digits = int(id_value[:2])
                # Convert 2-digit year to full year
                if year_digits >= 0 and year_digits <= 30:  # Assume 00-30 are 2000-2030
                    year = 2000 + year_digits
                else:  # 31-99 are 1931-1999
                    year = 1900 + year_digits
                serial = int(id_value[2:])
                results['valid_4_digit'].append({
                    'row': row_number,
                    'id': id_value,
                    'year': year,
                    'serial': serial,
                    'nome': row.get('nome', 'N/A')
                })
            
            progress.update(task, advance=1)
    
    # Analyze year series and find missing serials
    all_valid_entries = results['valid_3_digit'] + results['valid_4_digit']
    
    for entry in all_valid_entries:
        year = entry['year']
        serial = entry['serial']
        results['year_series'][year].append({
            'serial': serial,
            'row': entry['row'],
            'id': entry['id'],
            'nome': entry['nome']
        })
    
    # Check for missing serials in each year and duplicates
    id_counter = Counter([entry['id'] for entry in all_valid_entries])
    results['duplicate_ids'] = [{'id': id_val, 'count': count} 
                               for id_val, count in id_counter.items() if count > 1]
    
    for year, entries in results['year_series'].items():
        serials = sorted([entry['serial'] for entry in entries])
        results['year_series'][year] = sorted(entries, key=lambda x: x['serial'])
        
        # Find missing serials
        if serials:
            expected_range = range(1, max(serials) + 1)
            missing = [i for i in expected_range if i not in serials]
            results['missing_serials'][year] = missing
    
    # Generate statistics
    results['statistics'] = {
        'total_empty': len(results['empty_values']),
        'total_invalid_format': len(results['invalid_format']),
        'total_valid_3_digit': len(results['valid_3_digit']),
        'total_valid_4_digit': len(results['valid_4_digit']),
        'total_valid': len(all_valid_entries),
        'years_covered': len(results['year_series']),
        'total_duplicates': len(results['duplicate_ids']),
        'total_missing_serials': sum(len(missing) for missing in results['missing_serials'].values())
    }
    
    return results

def create_header():
    """Create a beautiful header for the quality control report"""
    title = Text("🏥 BD_doentes.csv Quality Control Report", style="bold white")
    subtitle = Text("ID Column Analysis", style="italic cyan")
    
    header_content = Align.center(
        Text.assemble(title, "\n", subtitle)
    )
    
    header_panel = Panel(
        header_content,
        style="blue",
        padding=(1, 2)
    )
    
    return header_panel

def display_overview(results: dict):
    """Display overview statistics"""
    stats = results['statistics']
    
    # Create overview table
    table = Table(title="📊 Overview Statistics", style="cyan")
    table.add_column("Metric", style="yellow", width=25)
    table.add_column("Count", justify="right", style="green", width=10)
    table.add_column("Percentage", justify="right", style="magenta", width=12)
    
    total_rows = results['total_rows']
    
    metrics = [
        ("Total Rows", total_rows, "100.00%"),
        ("Empty Values", stats['total_empty'], f"{stats['total_empty']/total_rows*100:.2f}%"),
        ("Invalid Format", stats['total_invalid_format'], f"{stats['total_invalid_format']/total_rows*100:.2f}%"),
        ("Valid 3-Digit IDs", stats['total_valid_3_digit'], f"{stats['total_valid_3_digit']/total_rows*100:.2f}%"),
        ("Valid 4-Digit IDs", stats['total_valid_4_digit'], f"{stats['total_valid_4_digit']/total_rows*100:.2f}%"),
        ("Total Valid IDs", stats['total_valid'], f"{stats['total_valid']/total_rows*100:.2f}%"),
        ("Years Covered", stats['years_covered'], "N/A"),
        ("Duplicate IDs", stats['total_duplicates'], f"{stats['total_duplicates']/total_rows*100:.2f}%"),
        ("Missing Serials", stats['total_missing_serials'], "N/A")
    ]
    
    for metric, count, percentage in metrics:
        if count == 0:
            style = "green"
        elif metric in ["Empty Values", "Invalid Format", "Duplicate IDs", "Missing Serials"] and count > 0:
            style = "red"
        else:
            style = "white"
        
        table.add_row(
            metric,
            f"[{style}]{count}[/{style}]",
            f"[{style}]{percentage}[/{style}]"
        )
    
    console.print(table)

def display_issues(results: dict):
    """Display detailed issues found"""
    
    # Empty Values
    if results['empty_values']:
        console.print("\n[red]❌ Empty ID Values Found:[/red]")
        empty_table = Table(style="red")
        empty_table.add_column("Row", justify="right", width=8)
        empty_table.add_column("Value", width=10)
        empty_table.add_column("Patient Name", width=40)
        
        for entry in results['empty_values'][:10]:  # Show first 10
            empty_table.add_row(
                str(entry['row']),
                entry['value'],
                entry['nome'][:37] + "..." if len(entry['nome']) > 40 else entry['nome']
            )
        
        if len(results['empty_values']) > 10:
            empty_table.add_row("...", "...", f"... and {len(results['empty_values']) - 10} more")
        
        console.print(empty_table)
    else:
        console.print("\n[green]✅ No empty ID values found![/green]")
    
    # Invalid Format
    if results['invalid_format']:
        console.print("\n[red]❌ Invalid ID Format Found:[/red]")
        invalid_table = Table(style="red")
        invalid_table.add_column("Row", justify="right", width=8)
        invalid_table.add_column("Invalid ID", width=12)
        invalid_table.add_column("Patient Name", width=40)
        
        for entry in results['invalid_format'][:10]:  # Show first 10
            invalid_table.add_row(
                str(entry['row']),
                entry['value'],
                entry['nome'][:37] + "..." if len(entry['nome']) > 40 else entry['nome']
            )
        
        if len(results['invalid_format']) > 10:
            invalid_table.add_row("...", "...", f"... and {len(results['invalid_format']) - 10} more")
        
        console.print(invalid_table)
    else:
        console.print("\n[green]✅ All IDs have valid 3 or 4 digit format![/green]")
    
    # Duplicate IDs
    if results['duplicate_ids']:
        console.print("\n[red]❌ Duplicate IDs Found:[/red]")
        dup_table = Table(style="red")
        dup_table.add_column("ID", width=10)
        dup_table.add_column("Count", justify="right", width=8)
        
        for entry in results['duplicate_ids']:
            dup_table.add_row(entry['id'], str(entry['count']))
        
        console.print(dup_table)
    else:
        console.print("\n[green]✅ No duplicate IDs found![/green]")

def display_year_analysis(results: dict):
    """Display year-by-year series analysis"""
    console.print("\n[cyan]📅 Year-by-Year Series Analysis:[/cyan]")
    
    year_table = Table(title="Year Series Statistics")
    year_table.add_column("Year", justify="center", style="yellow", width=8)
    year_table.add_column("Count", justify="right", style="green", width=8)
    year_table.add_column("Serial Range", justify="center", style="cyan", width=15)
    year_table.add_column("Missing Serials", justify="center", style="red", width=20)
    year_table.add_column("Status", justify="center", width=15)
    
    for year in sorted(results['year_series'].keys()):
        entries = results['year_series'][year]
        count = len(entries)
        serials = [entry['serial'] for entry in entries]
        min_serial = min(serials)
        max_serial = max(serials)
        
        missing = results['missing_serials'][year]
        missing_str = ", ".join(map(str, missing[:5]))  # Show first 5 missing
        if len(missing) > 5:
            missing_str += f" ... (+{len(missing) - 5})"
        if not missing:
            missing_str = "None"
        
        # Determine status
        if not missing:
            status = "[green]Complete[/green]"
        elif len(missing) <= 3:
            status = "[yellow]Minor gaps[/yellow]"
        else:
            status = "[red]Major gaps[/red]"
        
        year_table.add_row(
            str(year),
            str(count),
            f"{min_serial:02d}-{max_serial:02d}",
            missing_str,
            status
        )
    
    console.print(year_table)

def display_detailed_missing(results: dict):
    """Display detailed missing serial information for years with issues"""
    years_with_missing = {year: missing for year, missing in results['missing_serials'].items() if missing}
    
    if years_with_missing:
        console.print(f"\n[red]🔍 Detailed Missing Serials Analysis:[/red]")
        
        for year in sorted(years_with_missing.keys()):
            missing = years_with_missing[year]
            entries = results['year_series'][year]
            
            console.print(f"\n[yellow]Year {year}:[/yellow] Missing serials: {', '.join(map(str, missing))}")
            
            # Show existing entries around missing ones
            detail_table = Table(title=f"Year {year} - Existing Entries")
            detail_table.add_column("Serial", justify="right", width=8)
            detail_table.add_column("ID", width=8)
            detail_table.add_column("Row", justify="right", width=8)
            detail_table.add_column("Patient Name", width=30)
            
            # Sort entries by serial
            sorted_entries = sorted(entries, key=lambda x: x['serial'])
            
            for entry in sorted_entries[:15]:  # Show first 15 entries
                detail_table.add_row(
                    f"{entry['serial']:02d}",
                    entry['id'],
                    str(entry['row']),
                    entry['nome'][:27] + "..." if len(entry['nome']) > 30 else entry['nome']
                )
            
            if len(sorted_entries) > 15:
                detail_table.add_row("...", "...", "...", f"... and {len(sorted_entries) - 15} more entries")
            
            console.print(detail_table)
    else:
        console.print("\n[green]✅ No missing serials found in any year![/green]")

def main():
    """Main function to run the quality control analysis"""
    
    # Display header
    console.print(create_header())
    
    # File path
    csv_file = Path("/home/gusmmm/Desktop/mydb/files/csv/BD_doentes.csv")
    
    if not csv_file.exists():
        console.print(f"[red]Error: File {csv_file} not found![/red]")
        return
    
    console.print(f"[cyan]Analyzing file:[/cyan] {csv_file}")
    console.print()
    
    # Load data
    df = load_data(str(csv_file))
    if df is None:
        return
    
    console.print(f"[green]✅ Successfully loaded {len(df)} rows[/green]")
    console.print()
    
    # Analyze ID column
    results = analyze_id_column(df)
    
    # Display results
    display_overview(results)
    display_issues(results)
    display_year_analysis(results)
    display_detailed_missing(results)
    
    # Summary recommendations
    console.print("\n" + "="*80)
    console.print("[bold yellow]🎯 RECOMMENDATIONS:[/bold yellow]")
    
    if results['statistics']['total_empty'] > 0:
        console.print(f"[red]• Fix {results['statistics']['total_empty']} empty ID values[/red]")
    
    if results['statistics']['total_invalid_format'] > 0:
        console.print(f"[red]• Fix {results['statistics']['total_invalid_format']} invalid ID formats[/red]")
    
    if results['statistics']['total_duplicates'] > 0:
        console.print(f"[red]• Resolve {results['statistics']['total_duplicates']} duplicate IDs[/red]")
    
    if results['statistics']['total_missing_serials'] > 0:
        console.print(f"[yellow]• Investigate {results['statistics']['total_missing_serials']} missing serial numbers[/yellow]")
    
    if (results['statistics']['total_empty'] == 0 and 
        results['statistics']['total_invalid_format'] == 0 and 
        results['statistics']['total_duplicates'] == 0 and 
        results['statistics']['total_missing_serials'] == 0):
        console.print("[green]🎉 All ID values are valid and complete![/green]")
    
    console.print("="*80)

if __name__ == "__main__":
    main()
