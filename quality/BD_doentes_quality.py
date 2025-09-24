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
from datetime import datetime
from typing import Optional, Dict, Any, List
import os

# Initialize Rich console
console = Console()

# Optional: expected values for 'destino' column.
# You can override by setting env BD_DOENTES_DESTINO_EXPECTED to a pipe-separated list, e.g.:
#   export BD_DOENTES_DESTINO_EXPECTED="Domicílio|Outro hospital|SU|Óbito|Enfermaria|UCI"
def _expected_destino_values() -> Optional[set[str]]:
    env = os.getenv("BD_DOENTES_DESTINO_EXPECTED", "").strip()
    if not env:
        return None
    return {v.strip().casefold() for v in env.split("|") if v.strip()}

def load_data(file_path: str) -> Optional[pd.DataFrame]:
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
        # Use enumerate to avoid issues when index is not integer
        for pos, (_, row) in enumerate(df.iterrows(), start=2):
            id_value = row['ID_str']
            row_number = pos  # CSV header starts at row 1, so data starts at 2
            
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


# -------------------------------
# Processo column analysis
# -------------------------------

def analyze_processo_column(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze the 'processo' column with checks: empties, digit-only, length distribution, duplicates.

    Returns a dict with detailed findings and statistics.
    """
    results: Dict[str, Any] = {
        'total_rows': len(df),
        'empty_values': [],  # list of {row, value, ID, nome}
        'non_digit_values': [],  # list of {row, value, ID, nome}
        'length_distribution': Counter(),  # length -> count
        'usual_length': None,
        'deviant_lengths': [],  # list of {row, value, length, ID, nome}
        'duplicates': {},  # processo -> {count, rows: [...]}
        'statistics': {},
    }

    # Preprocess: ensure column exists
    if 'processo' not in df.columns:
        console.print("[red]Column 'processo' not found in CSV![/red]")
        return results

    # Work on a string version and strip whitespace
    processo_series = df['processo'].astype(str).str.strip()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing processo column...", total=len(df))

        for pos, (idx, value) in enumerate(processo_series.items(), start=2):
            raw_value = value
            row = df.loc[idx]

            # Treat empty and NaN
            if pd.isna(df.loc[idx, 'processo']) or raw_value in ['', 'nan', 'None']:
                results['empty_values'].append({
                    'row': pos,
                    'value': df.loc[idx, 'processo'],
                    'ID': row.get('ID', ''),
                    'nome': row.get('nome', '')
                })
                progress.update(task, advance=1)
                continue

            # Check digits
            if not raw_value.isdigit():
                results['non_digit_values'].append({
                    'row': pos,
                    'value': df.loc[idx, 'processo'],
                    'ID': row.get('ID', ''),
                    'nome': row.get('nome', '')
                })
            else:
                # Length distribution only for valid digits
                length = len(raw_value)
                results['length_distribution'][length] += 1

            progress.update(task, advance=1)

    # Determine usual length as the mode among digit-only entries
    if results['length_distribution']:
        usual_length = results['length_distribution'].most_common(1)[0][0]
        results['usual_length'] = usual_length

        # Find deviants: entries whose digit length differs from usual_length
        for pos, (idx, value) in enumerate(processo_series.items(), start=2):
            val = value
            if val.isdigit() and len(val) != usual_length:
                row = df.loc[idx]
                results['deviant_lengths'].append({
                    'row': pos,
                    'value': df.loc[idx, 'processo'],
                    'length': len(val),
                    'ID': row.get('ID', ''),
                    'nome': row.get('nome', '')
                })

    # Detect duplicates: they are allowed, but we report them alongside the rows
    counts = Counter(processo_series)
    for proc, cnt in counts.items():
        if proc in ['', 'nan', 'None']:
            continue
        if cnt > 1:
            # Collect rows where this processo appears
            rows: List[Dict[str, Any]] = []
            matching = df.index[processo_series == proc]
            for idx in matching:
                row = df.loc[idx]
                # Attempt to compute CSV row number (header=1)
                # We don't know original order vs index, so approximate via position
                pos = int(df.index.get_loc(idx)) + 2 if hasattr(df.index, 'get_loc') else 0
                rows.append({
                    'row': pos,
                    'ID': row.get('ID', ''),
                    'processo': row.get('processo', ''),
                    'nome': row.get('nome', ''),
                    'data_ent': row.get('data_ent', ''),
                    'data_alta': row.get('data_alta', ''),
                    'sexo': row.get('sexo', ''),
                    'origem': row.get('origem', ''),
                })
            results['duplicates'][proc] = {
                'count': cnt,
                'rows': sorted(rows, key=lambda r: r['row'])
            }

    # Statistics
    results['statistics'] = {
        'total_empty': len(results['empty_values']),
        'total_non_digit': len(results['non_digit_values']),
        'total_deviants': len(results['deviant_lengths']),
        'unique_processo': len(counts),
        'total_duplicates_groups': sum(1 for v in counts.values() if v > 1),
        'total_duplicated_rows': sum(cnt for cnt in counts.values() if cnt > 1),
    }

    return results


def display_processo_overview(results: Dict[str, Any]):
    """Display high-level statistics for processo column."""
    stats = results['statistics']
    table = Table(title="🧾 Processo - Overview", style="cyan")
    table.add_column("Metric", style="yellow", width=28)
    table.add_column("Count", justify="right", style="green", width=10)
    table.add_column("Notes", style="magenta")

    usual = results.get('usual_length')

    rows = [
        ("Total Rows", results['total_rows'], ""),
        ("Empty Values", stats['total_empty'], "Should be 0"),
        ("Non-Digit Values", stats['total_non_digit'], "Should be 0"),
        ("Usual Length", usual if usual is not None else "N/A", "Mode of digit-only lengths"),
        ("Deviant Length Rows", stats['total_deviants'], "Not matching usual length"),
        ("Unique 'processo' values", stats['unique_processo'], ""),
        ("Duplicate groups", stats['total_duplicates_groups'], "Allowed, listed below"),
        ("Rows in duplicates", stats['total_duplicated_rows'], "Total appearances"),
    ]

    for metric, count, note in rows:
        table.add_row(str(metric), str(count), str(note))

    console.print(table)


def display_processo_details(results: Dict[str, Any]):
    """Display detailed findings for processo: empties, non-digits, length distribution, deviants, duplicates."""

    # Empty values
    if results['empty_values']:
        console.print("\n[red]❌ Empty 'processo' values:[/red]")
        t = Table()
        t.add_column("Row", justify="right", width=6)
        t.add_column("processo", width=14)
        t.add_column("ID", width=8)
        t.add_column("Patient Name", width=40)
        for e in results['empty_values'][:20]:
            nome = e['nome'] or ''
            t.add_row(str(e['row']), str(e['value']), str(e['ID']), nome[:37] + "..." if len(nome) > 40 else nome)
        if len(results['empty_values']) > 20:
            t.add_row("...", "...", "...", f"... and {len(results['empty_values'])-20} more")
        console.print(t)
    else:
        console.print("\n[green]✅ No empty 'processo' values.[/green]")

    # Non-digit values
    if results['non_digit_values']:
        console.print("\n[red]❌ Non-digit 'processo' values:[/red]")
        t = Table()
        t.add_column("Row", justify="right", width=6)
        t.add_column("processo", width=14)
        t.add_column("ID", width=8)
        t.add_column("Patient Name", width=40)
        for e in results['non_digit_values'][:20]:
            nome = e['nome'] or ''
            t.add_row(str(e['row']), str(e['value']), str(e['ID']), nome[:37] + "..." if len(nome) > 40 else nome)
        if len(results['non_digit_values']) > 20:
            t.add_row("...", "...", "...", f"... and {len(results['non_digit_values'])-20} more")
        console.print(t)
    else:
        console.print("\n[green]✅ All 'processo' values are digit-only.[/green]")

    # Length distribution
    console.print("\n[cyan]📏 Length distribution (digit-only entries):[/cyan]")
    tlen = Table()
    tlen.add_column("Length", justify="right", width=8)
    tlen.add_column("Count", justify="right", width=8)
    tlen.add_column("Percent", justify="right", width=8)
    total_digits = sum(results['length_distribution'].values()) or 1
    usual = results.get('usual_length')
    for length, count in sorted(results['length_distribution'].items(), key=lambda kv: (-kv[1], kv[0])):
        pct = f"{count/total_digits*100:.1f}%"
        label = f"{length}"
        if usual is not None and length == usual:
            label = f"[green]{label}*[/green]"
        tlen.add_row(label, str(count), pct)
    console.print(tlen)

    # Deviants
    if results['deviant_lengths']:
        console.print("\n[yellow]⚠️ Entries with deviant length:[/yellow]")
        t = Table()
        t.add_column("Row", justify="right", width=6)
        t.add_column("processo", width=14)
        t.add_column("Length", justify="right", width=8)
        t.add_column("ID", width=8)
        t.add_column("Patient Name", width=40)
        for e in results['deviant_lengths'][:20]:
            nome = e['nome'] or ''
            t.add_row(str(e['row']), str(e['value']), str(e['length']), str(e['ID']), nome[:37] + "..." if len(nome) > 40 else nome)
        if len(results['deviant_lengths']) > 20:
            t.add_row("...", "...", "...", "...", f"... and {len(results['deviant_lengths'])-20} more")
        console.print(t)
    else:
        console.print("\n[green]✅ No deviant lengths detected.[/green]")

    # Duplicates
    if results['duplicates']:
        console.print("\n[cyan]🔁 Duplicated 'processo' values:[/cyan]")
        # Summary
        ts = Table(title="Duplicate groups summary")
        ts.add_column("processo", width=16)
        ts.add_column("Count", justify="right", width=8)
        for proc, info in sorted(results['duplicates'].items(), key=lambda kv: -kv[1]['count']):
            ts.add_row(str(proc), str(info['count']))
        console.print(ts)

        # Detailed per-processo rows (limit to first 10 groups)
        shown = 0
        for proc, info in sorted(results['duplicates'].items(), key=lambda kv: -kv[1]['count']):
            if shown >= 10:
                remaining = len(results['duplicates']) - shown
                if remaining > 0:
                    console.print(f"[dim]... and {remaining} more duplicate groups[/dim]")
                break
            console.print(f"\n[bold]processo {proc}[/bold] (x{info['count']})")
            t = Table()
            t.add_column("Row", justify="right", width=6)
            t.add_column("ID", width=8)
            t.add_column("Nome", width=34)
            t.add_column("data_ent", width=12)
            t.add_column("data_alta", width=12)
            t.add_column("Sexo", width=6)
            t.add_column("Origem", width=22)
            for r in info['rows'][:20]:
                nome = r['nome'] or ''
                t.add_row(str(r['row']), str(r['ID']), nome[:31] + "..." if len(nome) > 34 else nome,
                          str(r['data_ent']), str(r['data_alta']), str(r['sexo']), str(r['origem'])[:22])
            if len(info['rows']) > 20:
                t.add_row("...", "...", f"... and {len(info['rows'])-20} more", "...", "...", "...", "...")
            console.print(t)
            shown += 1
    else:
        console.print("\n[green]✅ No duplicates for 'processo'.[/green]\n")


def save_processo_report(results: Dict[str, Any], csv_file: Path) -> Path:
    """Save a detailed markdown report for 'processo' analysis into /files/reports/."""
    reports_dir = Path("/home/gusmmm/Desktop/mydb/files/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"BD_doentes_processo_analysis_{timestamp}.md"

    stats = results['statistics']
    lines: List[str] = []
    lines.append("# BD_doentes.csv - 'processo' Column Quality Control Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Source File:** {csv_file}\n")
    lines.append("\n## 📊 Summary\n")
    lines.append(f"- Total rows: {results['total_rows']}")
    lines.append(f"- Empty values: {stats['total_empty']}")
    lines.append(f"- Non-digit values: {stats['total_non_digit']}")
    usual = results.get('usual_length')
    lines.append(f"- Usual length: {usual if usual is not None else 'N/A'}")
    lines.append(f"- Deviant length rows: {stats['total_deviants']}")
    lines.append(f"- Unique 'processo' values: {stats['unique_processo']}")
    lines.append(f"- Duplicate groups: {stats['total_duplicates_groups']} (rows in duplicates: {stats['total_duplicated_rows']})\n")

    # Length distribution
    lines.append("### Length Distribution (digit-only)\n")
    lines.append("| Length | Count | Percent |")
    lines.append("|--------|-------|---------|")
    total_digits = sum(results['length_distribution'].values()) or 1
    for length, count in sorted(results['length_distribution'].items(), key=lambda kv: (-kv[1], kv[0])):
        pct = f"{count/total_digits*100:.1f}%"
        lines.append(f"| {length} | {count} | {pct} |")

    # Deviants (first 50)
    if results['deviant_lengths']:
        lines.append("\n### Deviant Length Rows (first 50)\n")
        lines.append("| Row | processo | Length | ID | Name |")
        lines.append("|-----|----------|--------|----|------|")
        for e in results['deviant_lengths'][:50]:
            lines.append(f"| {e['row']} | {e['value']} | {e['length']} | {e['ID']} | {e['nome']} |")

    # Non-digit values (first 50)
    if results['non_digit_values']:
        lines.append("\n### Non-digit Values (first 50)\n")
        lines.append("| Row | processo | ID | Name |")
        lines.append("|-----|----------|----|------|")
        for e in results['non_digit_values'][:50]:
            lines.append(f"| {e['row']} | {e['value']} | {e['ID']} | {e['nome']} |")

    # Duplicates - summary and detail (first 20 groups)
    if results['duplicates']:
        lines.append("\n### Duplicate 'processo' Values\n")
        lines.append("| processo | Count |")
        lines.append("|----------|-------|")
        for proc, info in sorted(results['duplicates'].items(), key=lambda kv: -kv[1]['count']):
            lines.append(f"| {proc} | {info['count']} |")

        # Detailed rows
        lines.append("\n#### Duplicate Details (first 20 groups, 50 rows each)\n")
        shown = 0
        for proc, info in sorted(results['duplicates'].items(), key=lambda kv: -kv[1]['count']):
            if shown >= 20:
                break
            lines.append(f"\n##### processo {proc} (x{info['count']})\n")
            lines.append("| Row | ID | Name | data_ent | data_alta | Sexo | Origem |")
            lines.append("|-----|----|------|----------|-----------|------|--------|")
            for r in info['rows'][:50]:
                lines.append(f"| {r['row']} | {r['ID']} | {r['nome']} | {r['data_ent']} | {r['data_alta']} | {r['sexo']} | {r['origem']} |")
            shown += 1

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")

    console.print(f"\n[green]📄 'processo' report saved to:[/green] {report_file}")
    return report_file


# -------------------------------
# Nome column analysis
# -------------------------------

def analyze_nome_column(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze the 'nome' column: empties, non-string values, duplicates with row details."""
    results: Dict[str, Any] = {
        'total_rows': len(df),
        'empty_values': [],  # {row, value, ID, processo}
        'non_string_values': [],  # {row, value, type, ID, processo}
        'duplicates': {},  # name_key -> {count, display: original, rows: [...]}
        'statistics': {},
    }

    if 'nome' not in df.columns:
        console.print("[red]Column 'nome' not found in CSV![/red]")
        return results

    series = df['nome']

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing nome column...", total=len(df))

        for pos, (idx, val) in enumerate(series.items(), start=2):
            raw = val
            # Empty check
            if pd.isna(raw) or (isinstance(raw, str) and raw.strip() == ""):
                results['empty_values'].append({
                    'row': pos,
                    'value': None if pd.isna(raw) else raw,
                    'ID': df.loc[idx].get('ID', ''),
                    'processo': df.loc[idx].get('processo', ''),
                })
                progress.update(task, advance=1)
                continue

            # String type check
            if not isinstance(raw, str):
                results['non_string_values'].append({
                    'row': pos,
                    'value': raw,
                    'type': type(raw).__name__,
                    'ID': df.loc[idx].get('ID', ''),
                    'processo': df.loc[idx].get('processo', ''),
                })
            progress.update(task, advance=1)

    # Duplicates (allow duplicates but report them). Normalize by trimming spaces.
    name_keys = series.apply(lambda x: x.strip() if isinstance(x, str) else x)
    counts = Counter(name_keys)
    for name_key, cnt in counts.items():
        if pd.isna(name_key) or name_key == "":
            continue
        if cnt > 1:
            rows: List[Dict[str, Any]] = []
            matching = df.index[name_keys == name_key]
            for idx in matching:
                row = df.loc[idx]
                pos = int(df.index.get_loc(idx)) + 2 if hasattr(df.index, 'get_loc') else 0
                rows.append({
                    'row': pos,
                    'ID': row.get('ID', ''),
                    'processo': row.get('processo', ''),
                    'nome': row.get('nome', ''),
                    'data_ent': row.get('data_ent', ''),
                    'data_alta': row.get('data_alta', ''),
                    'sexo': row.get('sexo', ''),
                    'origem': row.get('origem', ''),
                })
            # Pick a display version (first occurrence's original)
            display_value = df.loc[matching[0]].get('nome', str(name_key)) if len(matching) > 0 else str(name_key)
            results['duplicates'][str(name_key)] = {
                'display': display_value,
                'count': cnt,
                'rows': sorted(rows, key=lambda r: r['row'])
            }

    results['statistics'] = {
        'total_empty': len(results['empty_values']),
        'total_non_string': len(results['non_string_values']),
        'total_duplicates_groups': len(results['duplicates']),
        'total_duplicated_rows': sum(info['count'] for info in results['duplicates'].values()),
        'unique_names': len([k for k, v in counts.items() if not (pd.isna(k) or k == '')]),
    }

    return results


def display_nome_overview(results: Dict[str, Any]):
    table = Table(title="🧑‍⚕️ Nome - Overview", style="cyan")
    table.add_column("Metric", style="yellow", width=28)
    table.add_column("Count", justify="right", style="green", width=10)
    table.add_column("Notes", style="magenta")

    s = results['statistics']
    rows = [
        ("Total Rows", results['total_rows'], ""),
        ("Empty Values", s['total_empty'], "Should be 0"),
        ("Non-String Values", s['total_non_string'], "Should be 0"),
        ("Unique Names", s['unique_names'], ""),
        ("Duplicate groups", s['total_duplicates_groups'], "Allowed, listed below"),
        ("Rows in duplicates", s['total_duplicated_rows'], "Total appearances"),
    ]
    for metric, count, note in rows:
        table.add_row(str(metric), str(count), str(note))
    console.print(table)


def display_nome_details(results: Dict[str, Any]):
    # Empty
    if results['empty_values']:
        console.print("\n[red]❌ Empty 'nome' values:[/red]")
        t = Table()
        t.add_column("Row", justify="right", width=6)
        t.add_column("ID", width=8)
        t.add_column("processo", width=14)
        t.add_column("nome", width=40)
        for e in results['empty_values'][:20]:
            t.add_row(str(e['row']), str(e['ID']), str(e['processo']), str(e['value']))
        if len(results['empty_values']) > 20:
            t.add_row("...", "...", "...", f"... and {len(results['empty_values'])-20} more")
        console.print(t)
    else:
        console.print("\n[green]✅ No empty 'nome' values.[/green]")

    # Non-string
    if results['non_string_values']:
        console.print("\n[red]❌ Non-string 'nome' values:[/red]")
        t = Table()
        t.add_column("Row", justify="right", width=6)
        t.add_column("Type", width=10)
        t.add_column("Value", width=40)
        t.add_column("ID", width=8)
        t.add_column("processo", width=14)
        for e in results['non_string_values'][:20]:
            t.add_row(str(e['row']), str(e['type']), str(e['value']), str(e['ID']), str(e['processo']))
        if len(results['non_string_values']) > 20:
            t.add_row("...", "...", "...", "...", f"... and {len(results['non_string_values'])-20} more")
        console.print(t)
    else:
        console.print("\n[green]✅ All 'nome' values are strings.[/green]")

    # Duplicates
    if results['duplicates']:
        console.print("\n[cyan]🔁 Duplicated 'nome' values:[/cyan]")
        ts = Table(title="Duplicate name groups")
        ts.add_column("Name", width=34)
        ts.add_column("Count", justify="right", width=8)
        for name_key, info in sorted(results['duplicates'].items(), key=lambda kv: -kv[1]['count']):
            display = info.get('display', name_key)
            ts.add_row(str(display)[:34], str(info['count']))
        console.print(ts)

        shown = 0
        for name_key, info in sorted(results['duplicates'].items(), key=lambda kv: -kv[1]['count']):
            if shown >= 10:
                remaining = len(results['duplicates']) - shown
                if remaining > 0:
                    console.print(f"[dim]... and {remaining} more duplicate name groups[/dim]")
                break
            console.print(f"\n[bold]{info.get('display', name_key)}[/bold] (x{info['count']})")
            t = Table()
            t.add_column("Row", justify="right", width=6)
            t.add_column("ID", width=8)
            t.add_column("processo", width=14)
            t.add_column("data_ent", width=12)
            t.add_column("data_alta", width=12)
            t.add_column("Sexo", width=6)
            t.add_column("Origem", width=22)
            for r in info['rows'][:20]:
                t.add_row(str(r['row']), str(r['ID']), str(r['processo']), str(r['data_ent']), str(r['data_alta']), str(r['sexo']), str(r['origem'])[:22])
            if len(info['rows']) > 20:
                t.add_row("...", "...", "...", "...", "...", "...", f"... and {len(info['rows'])-20} more")
            console.print(t)
            shown += 1
    else:
        console.print("\n[green]✅ No duplicate names detected.[/green]\n")


def save_nome_report(results: Dict[str, Any], csv_file: Path) -> Path:
    reports_dir = Path("/home/gusmmm/Desktop/mydb/files/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"BD_doentes_nome_analysis_{timestamp}.md"

    s = results['statistics']
    lines: List[str] = []
    lines.append("# BD_doentes.csv - 'nome' Column Quality Control Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Source File:** {csv_file}\n")
    lines.append("\n## 📊 Summary\n")
    lines.append(f"- Total rows: {results['total_rows']}")
    lines.append(f"- Empty values: {s['total_empty']}")
    lines.append(f"- Non-string values: {s['total_non_string']}")
    lines.append(f"- Unique names: {s['unique_names']}")
    lines.append(f"- Duplicate groups: {s['total_duplicates_groups']} (rows in duplicates: {s['total_duplicated_rows']})\n")

    if results['duplicates']:
        lines.append("### Duplicate Names\n")
        lines.append("| Name | Count |")
        lines.append("|------|-------|")
        for name_key, info in sorted(results['duplicates'].items(), key=lambda kv: -kv[1]['count']):
            display = info.get('display', name_key)
            lines.append(f"| {display} | {info['count']} |")

        # Detail (first 20 groups)
        lines.append("\n#### Duplicate Details (first 20 groups, 50 rows each)\n")
        shown = 0
        for name_key, info in sorted(results['duplicates'].items(), key=lambda kv: -kv[1]['count']):
            if shown >= 20:
                break
            lines.append(f"\n##### {info.get('display', name_key)} (x{info['count']})\n")
            lines.append("| Row | ID | processo | data_ent | data_alta | Sexo | Origem |")
            lines.append("|-----|----|----------|----------|-----------|------|--------|")
            for r in info['rows'][:50]:
                lines.append(f"| {r['row']} | {r['ID']} | {r['processo']} | {r['data_ent']} | {r['data_alta']} | {r['sexo']} | {r['origem']} |")
            shown += 1

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")

    console.print(f"\n[green]📄 'nome' report saved to:[/green] {report_file}")
    return report_file


# -------------------------------
# data_ent (admission date) analysis
# -------------------------------

def _id_expected_year(id_str: str) -> Optional[int]:
    if not isinstance(id_str, str) or not id_str.isdigit():
        return None
    if len(id_str) == 3:
        return 2000 + int(id_str[0])
    if len(id_str) == 4:
        yy = int(id_str[:2])
        return 2000 + yy if 0 <= yy <= 30 else 1900 + yy
    return None


def _is_strict_dd_mm_yyyy(s: str) -> bool:
    return isinstance(s, str) and re.fullmatch(r"\d{2}-\d{2}-\d{4}", s) is not None


def _parse_date_loose(s: str) -> Optional[pd.Timestamp]:
    """Try to parse date allowing common dd-mm-yyyy variants while preserving correctness.
    Returns a pandas Timestamp or None.
    """
    if not isinstance(s, str) or s.strip() == "":
        return None
    st = s.strip()
    # First try strict dd-mm-yyyy
    if _is_strict_dd_mm_yyyy(st):
        try:
            return pd.to_datetime(st, format="%d-%m-%Y", errors="raise")
        except Exception:
            return None
    # Try yyyy-mm-dd (fallback strict)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", st):
        try:
            return pd.to_datetime(st, format="%Y-%m-%d", errors="raise")
        except Exception:
            return None
    # Try d-m-Y with 1-2 digits (fallback)
    m = re.fullmatch(r"(\d{1,2})-(\d{1,2})-(\d{4})", st)
    if m:
        d, mo, y = m.groups()
        try:
            return pd.to_datetime(f"{int(d):02d}-{int(mo):02d}-{y}", format="%d-%m-%Y", errors="raise")
        except Exception:
            return None
    return None


def analyze_data_ent_column(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data_ent column for format, year vs ID, and monotonicity by ID."""
    results: Dict[str, Any] = {
        'total_rows': len(df),
        'missing': [],  # {row, ID, data_ent}
        'invalid_format': [],  # {row, ID, data_ent}
        'invalid_date_value': [],  # reserved; currently handled by parser
        'year_mismatch': [],  # {row, ID, id_year, data_ent, date_year}
        'series_violations': [],  # {row, ID, data_ent, prev_row, prev_ID, prev_date}
        'strict_valid_count': 0,
        'parsed_loose_count': 0,
        'unparseable_count': 0,
        'excluded_from_series': 0,
        'statistics': {},
    }

    if 'data_ent' not in df.columns:
        console.print("[red]Column 'data_ent' not found in CSV![/red]")
        return results

    # Prepare fields
    id_str_series = df['ID'].astype(str)
    data_series = df['data_ent'].astype(object)

    parsed_dates: List[Optional[pd.Timestamp]] = [None] * len(df)
    strict_flags: List[bool] = [False] * len(df)
    id_years: List[Optional[int]] = [None] * len(df)
    row_positions: List[int] = list(range(2, len(df) + 2))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing data_ent column...", total=len(df))
        for i, (idx, val) in enumerate(data_series.items()):
            row = df.loc[idx]
            pos = row_positions[i]
            id_str = id_str_series.loc[idx]
            id_year = _id_expected_year(id_str)
            id_years[i] = id_year
            s = None if pd.isna(val) else str(val).strip()
            if s is None or s == "":
                results['missing'].append({'row': pos, 'ID': id_str, 'data_ent': val})
                parsed_dates[i] = None
                results['unparseable_count'] += 1
                progress.update(task, advance=1)
                continue
            is_strict = _is_strict_dd_mm_yyyy(s)
            if not is_strict:
                results['invalid_format'].append({'row': pos, 'ID': id_str, 'data_ent': s})
            # Try to parse
            dt = _parse_date_loose(s)
            if dt is None:
                results['unparseable_count'] += 1
            else:
                if is_strict:
                    results['strict_valid_count'] += 1
                else:
                    results['parsed_loose_count'] += 1
                # Year match check
                if id_year is not None and dt.year != id_year:
                    results['year_mismatch'].append({
                        'row': pos,
                        'ID': id_str,
                        'id_year': id_year,
                        'data_ent': s,
                        'date_year': int(dt.year),
                    })
            parsed_dates[i] = dt
            strict_flags[i] = is_strict
            progress.update(task, advance=1)

    # Series (higher ID -> equal or later date). Sort by numeric ID asc, then by serial pos to preserve stable ordering.
    # Build a list of tuples for rows with any parsed date; if a date is missing, they are excluded from check.
    try:
        ids_int = [int(s) if isinstance(s, str) and s.isdigit() else None for s in id_str_series]
    except Exception:
        ids_int = [None for _ in id_str_series]

    sortable = []
    for i in range(len(df)):
        if ids_int[i] is None:
            continue
        sortable.append((ids_int[i], i))
    sortable.sort(key=lambda t: t[0])

    last_date = None
    last_i = None
    for _, i in sortable:
        dt = parsed_dates[i]
        if dt is None:
            results['excluded_from_series'] += 1
            continue
        if last_date is not None and dt < last_date:
            # violation
            curr_pos = row_positions[i]
            prev_pos = row_positions[last_i] if last_i is not None else None
            results['series_violations'].append({
                'row': curr_pos,
                'ID': str(id_str_series.iloc[i]),
                'data_ent': str(df['data_ent'].iloc[i]),
                'prev_row': prev_pos,
                'prev_ID': str(id_str_series.iloc[last_i]) if last_i is not None else '',
                'prev_date': str(df['data_ent'].iloc[last_i]) if last_i is not None else '',
            })
        # Update last_date to max(last_date, dt) to allow equal or later rule
        if last_date is None or dt >= last_date:
            last_date = dt
            last_i = i

    results['statistics'] = {
        'total_missing': len(results['missing']),
        'total_invalid_format': len(results['invalid_format']),
        'strict_valid_count': results['strict_valid_count'],
        'parsed_loose_count': results['parsed_loose_count'],
        'unparseable_count': results['unparseable_count'],
        'year_mismatch': len(results['year_mismatch']),
        'series_violations': len(results['series_violations']),
        'excluded_from_series': results['excluded_from_series'],
    }

    return results


def display_data_ent_overview(results: Dict[str, Any]):
    t = Table(title="📅 data_ent - Overview", style="cyan")
    t.add_column("Metric", style="yellow", width=30)
    t.add_column("Count", justify="right", style="green", width=10)
    t.add_column("Notes", style="magenta")
    s = results['statistics']
    rows = [
        ("Total Rows", results['total_rows'], ""),
        ("Missing", s['total_missing'], "Should be 0"),
    ("Invalid Format (not DD-MM-YYYY)", s['total_invalid_format'], ""),
    ("Strict valid (DD-MM-YYYY)", s['strict_valid_count'], ""),
    ("Parsed via fallback", s['parsed_loose_count'], "yyyy-mm-dd and d-m-Y accepted"),
        ("Unparseable", s['unparseable_count'], ""),
        ("Year mismatch vs ID", s['year_mismatch'], ""),
        ("Series violations", s['series_violations'], "Higher ID earlier date"),
        ("Excluded from series", s['excluded_from_series'], "Missing/unparseable"),
    ]
    for metric, count, note in rows:
        t.add_row(str(metric), str(count), str(note))
    console.print(t)


def display_data_ent_details(results: Dict[str, Any]):
    # Missing
    if results['missing']:
        console.print("\n[red]❌ Missing data_ent values:[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("data_ent", width=14)
        for e in results['missing'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['data_ent']))
        if len(results['missing']) > 20:
            tt.add_row("...", "...", f"... and {len(results['missing'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ No missing data_ent values.[/green]")

    # Invalid format
    if results['invalid_format']:
        console.print("\n[yellow]⚠️ Invalid format (expected DD-MM-YYYY):[/yellow]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("data_ent", width=14)
        for e in results['invalid_format'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['data_ent']))
        if len(results['invalid_format']) > 20:
            tt.add_row("...", "...", f"... and {len(results['invalid_format'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ All data_ent values match DD-MM-YYYY format.[/green]")

    # Year mismatch
    if results['year_mismatch']:
        console.print("\n[red]❌ Year mismatches (ID vs data_ent):[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("ID year", justify="right", width=8)
        tt.add_column("data_ent", width=14)
        tt.add_column("Date year", justify="right", width=10)
        for e in results['year_mismatch'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['id_year']), str(e['data_ent']), str(e['date_year']))
        if len(results['year_mismatch']) > 20:
            tt.add_row("...", "...", "...", "...", f"... and {len(results['year_mismatch'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ All ID years match data_ent years (for parseable dates).[/green]")

    # Series violations
    if results['series_violations']:
        console.print("\n[red]❌ Series violations (higher ID earlier date):[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("data_ent", width=14)
        tt.add_column("Prev Row", justify="right", width=8)
        tt.add_column("Prev ID", width=8)
        tt.add_column("Prev date", width=14)
        for e in results['series_violations'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['data_ent']), str(e['prev_row']), str(e['prev_ID']), str(e['prev_date']))
        if len(results['series_violations']) > 20:
            tt.add_row("...", "...", "...", "...", "...", f"... and {len(results['series_violations'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ No series violations detected (for parseable dates).[/green]")


def save_data_ent_report(results: Dict[str, Any], csv_file: Path) -> Path:
    reports_dir = Path("/home/gusmmm/Desktop/mydb/files/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"BD_doentes_data_ent_analysis_{timestamp}.md"
    s = results['statistics']

    lines: List[str] = []
    lines.append("# BD_doentes.csv - data_ent Column Quality Control Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Source File:** {csv_file}\n")
    lines.append("\n## 📊 Summary\n")
    lines.append(f"- Total rows: {results['total_rows']}")
    lines.append(f"- Missing: {s['total_missing']}")
    lines.append(f"- Invalid format (not DD-MM-YYYY): {s['total_invalid_format']}")
    lines.append(f"- Strict valid (DD-MM-YYYY): {s['strict_valid_count']}")
    lines.append(f"- Parsed via fallback (yyyy-mm-dd or d-m-Y): {s['parsed_loose_count']}")
    lines.append(f"- Unparseable: {s['unparseable_count']}")
    lines.append(f"- Year mismatches (ID vs data): {s['year_mismatch']}")
    lines.append(f"- Series violations: {s['series_violations']} (excluded: {s['excluded_from_series']})\n")

    # Samples
    def tbl(rows: List[Dict[str, Any]], headers: List[str], keys: List[str], title: str, limit: int = 50):
        nonlocal lines
        if not rows:
            return
        lines.append(f"\n### {title}\n")
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(['-'*len(h) for h in headers]) + " |")
        for e in rows[:limit]:
            values = [str(e.get(k, '')) for k in keys]
            lines.append("| " + " | ".join(values) + " |")
        if len(rows) > limit:
            lines.append(f"| ... | ... | ... | ... | ... |")

    tbl(results['invalid_format'], ["Row", "ID", "data_ent"], ["row", "ID", "data_ent"], "Invalid format (first 50) - expected DD-MM-YYYY")
    tbl(results['year_mismatch'], ["Row", "ID", "ID year", "data_ent", "Date year"], ["row", "ID", "id_year", "data_ent", "date_year"], "Year mismatches (first 50)")
    tbl(results['series_violations'], ["Row", "ID", "data_ent", "Prev Row", "Prev ID", "Prev date"], ["row", "ID", "data_ent", "prev_row", "prev_ID", "prev_date"], "Series violations (first 50)")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    console.print(f"\n[green]📄 'data_ent' report saved to:[/green] {report_file}")
    return report_file


# -------------------------------
# data_alta (discharge date) analysis
# -------------------------------

def analyze_data_alta_column(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data_alta: missing, DD-MM-YYYY format, posterior to data_ent (when present)."""
    results: Dict[str, Any] = {
        'total_rows': len(df),
        'missing': [],  # {row, ID}
        'invalid_format': [],  # {row, ID, data_alta}
        'unparseable_count': 0,
        'strict_valid_count': 0,
        'parsed_loose_count': 0,
        'not_after_data_ent': [],  # {row, ID, data_ent, data_alta}
        'statistics': {},
    }

    if 'data_alta' not in df.columns:
        console.print("[red]Column 'data_alta' not found in CSV![/red]")
        return results

    series_alta = df['data_alta'].astype(object)
    series_ent = df['data_ent'].astype(object) if 'data_ent' in df.columns else None
    id_str_series = df['ID'].astype(str)

    parsed_alta: List[Optional[pd.Timestamp]] = [None] * len(df)
    parsed_ent: List[Optional[pd.Timestamp]] = [None] * len(df)
    row_positions: List[int] = list(range(2, len(df) + 2))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analyzing data_alta column...", total=len(df))

        for i, (idx, val) in enumerate(series_alta.items()):
            pos = row_positions[i]
            id_str = id_str_series.loc[idx]
            raw_alta = None if pd.isna(val) else str(val).strip()
            if raw_alta is None or raw_alta == "":
                results['missing'].append({'row': pos, 'ID': id_str})
                parsed_alta[i] = None
                progress.update(task, advance=1)
                continue

            is_strict = _is_strict_dd_mm_yyyy(raw_alta)
            if not is_strict:
                results['invalid_format'].append({'row': pos, 'ID': id_str, 'data_alta': raw_alta})
            dt_alta = _parse_date_loose(raw_alta)
            if dt_alta is None:
                results['unparseable_count'] += 1
            else:
                if is_strict:
                    results['strict_valid_count'] += 1
                else:
                    results['parsed_loose_count'] += 1
            parsed_alta[i] = dt_alta

            # Parse data_ent if available for comparison
            if series_ent is not None:
                raw_ent = None if pd.isna(series_ent.loc[idx]) else str(series_ent.loc[idx]).strip()
                dt_ent = _parse_date_loose(raw_ent) if raw_ent else None
                parsed_ent[i] = dt_ent

            progress.update(task, advance=1)

    # Compare alta > ent when both parseable
    for i in range(len(df)):
        dt_alta = parsed_alta[i]
        dt_ent = parsed_ent[i] if series_ent is not None else None
        if dt_alta is not None and dt_ent is not None:
            if not (dt_alta >= dt_ent):  # posterior or same day acceptable? Requirement says posterior; use >
                # If strictly posterior required, change to dt_alta > dt_ent
                if not (dt_alta > dt_ent):
                    results['not_after_data_ent'].append({
                        'row': row_positions[i],
                        'ID': str(id_str_series.iloc[i]),
                        'data_ent': str(series_ent.iloc[i]) if series_ent is not None else '',
                        'data_alta': str(series_alta.iloc[i]),
                    })

    results['statistics'] = {
        'total_missing': len(results['missing']),
        'total_invalid_format': len(results['invalid_format']),
        'strict_valid_count': results['strict_valid_count'],
        'parsed_loose_count': results['parsed_loose_count'],
        'unparseable_count': results['unparseable_count'],
        'not_after_data_ent': len(results['not_after_data_ent']),
    }

    return results


def display_data_alta_overview(results: Dict[str, Any]):
    t = Table(title="📆 data_alta - Overview", style="cyan")
    t.add_column("Metric", style="yellow", width=30)
    t.add_column("Count", justify="right", style="green", width=10)
    t.add_column("Notes", style="magenta")
    s = results['statistics']
    rows = [
        ("Total Rows", results['total_rows'], ""),
        ("Missing", s['total_missing'], ""),
        ("Invalid Format (not DD-MM-YYYY)", s['total_invalid_format'], ""),
        ("Strict valid (DD-MM-YYYY)", s['strict_valid_count'], ""),
        ("Parsed via fallback", s['parsed_loose_count'], "yyyy-mm-dd and d-m-Y accepted"),
        ("Unparseable", s['unparseable_count'], ""),
        ("Not after data_ent", s['not_after_data_ent'], "Should be strictly later than data_ent"),
    ]
    for metric, count, note in rows:
        t.add_row(str(metric), str(count), str(note))
    console.print(t)


def display_data_alta_details(results: Dict[str, Any]):
    # Missing
    if results['missing']:
        console.print("\n[red]❌ Missing data_alta values:[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        for e in results['missing'][:20]:
            tt.add_row(str(e['row']), str(e['ID']))
        if len(results['missing']) > 20:
            tt.add_row("...", f"... and {len(results['missing'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ No missing data_alta values.[/green]")

    # Invalid format
    if results['invalid_format']:
        console.print("\n[yellow]⚠️ Invalid format (expected DD-MM-YYYY):[/yellow]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("data_alta", width=14)
        for e in results['invalid_format'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['data_alta']))
        if len(results['invalid_format']) > 20:
            tt.add_row("...", "...", f"... and {len(results['invalid_format'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ All data_alta values match DD-MM-YYYY format.[/green]")

    # Not after data_ent
    if results['not_after_data_ent']:
        console.print("\n[red]❌ Discharge before or same as admission (requires posterior):[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("data_ent", width=14)
        tt.add_column("data_alta", width=14)
        for e in results['not_after_data_ent'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['data_ent']), str(e['data_alta']))
        if len(results['not_after_data_ent']) > 20:
            tt.add_row("...", "...", "...", f"... and {len(results['not_after_data_ent'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ All discharges are strictly after admissions (for parseable dates).[/green]")


def save_data_alta_report(results: Dict[str, Any], csv_file: Path) -> Path:
    reports_dir = Path("/home/gusmmm/Desktop/mydb/files/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"BD_doentes_data_alta_analysis_{timestamp}.md"
    s = results['statistics']

    lines: List[str] = []
    lines.append("# BD_doentes.csv - data_alta Column Quality Control Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Source File:** {csv_file}\n")
    lines.append("\n## 📊 Summary\n")
    lines.append(f"- Total rows: {results['total_rows']}")
    lines.append(f"- Missing: {s['total_missing']}")
    lines.append(f"- Invalid format (not DD-MM-YYYY): {s['total_invalid_format']}")
    lines.append(f"- Strict valid (DD-MM-YYYY): {s['strict_valid_count']}")
    lines.append(f"- Parsed via fallback (yyyy-mm-dd or d-m-Y): {s['parsed_loose_count']}")
    lines.append(f"- Unparseable: {s['unparseable_count']}")
    lines.append(f"- Not after data_ent: {s['not_after_data_ent']}\n")

    def tbl(rows: List[Dict[str, Any]], headers: List[str], keys: List[str], title: str, limit: int = 50):
        nonlocal lines
        if not rows:
            return
        lines.append(f"\n### {title}\n")
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(['-'*len(h) for h in headers]) + " |")
        for e in rows[:limit]:
            values = [str(e.get(k, '')) for k in keys]
            lines.append("| " + " | ".join(values) + " |")
        if len(rows) > limit:
            lines.append("| ... | ... | ... | ... |")

    tbl(results['invalid_format'], ["Row", "ID", "data_alta"], ["row", "ID", "data_alta"], "Invalid format (first 50) - expected DD-MM-YYYY")
    tbl(results['not_after_data_ent'], ["Row", "ID", "data_ent", "data_alta"], ["row", "ID", "data_ent", "data_alta"], "Not after data_ent (first 50)")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    console.print(f"\n[green]📄 'data_alta' report saved to:[/green] {report_file}")
    return report_file

# -------------------------------
# destino (discharge destination) analysis
# -------------------------------

def analyze_destino_column(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze 'destino':
    - check missing/empty
    - value frequencies (string values)
    - mark values deviating from expected list (if provided via env)
    """
    results: Dict[str, Any] = {
        'total_rows': len(df),
        'missing': [],  # {row, ID}
        'frequencies': Counter(),
        'distinct_values': [],
        'deviant_values': [],  # rows with value not in expected set
        'statistics': {},
        'expected_set': None,
    }

    if 'destino' not in df.columns:
        console.print("[red]Column 'destino' not found in CSV![/red]")
        return results

    expected = _expected_destino_values()
    results['expected_set'] = sorted(list(expected)) if expected else None

    series = df['destino'].astype(object)
    id_series = df['ID'].astype(str)
    row_positions: List[int] = list(range(2, len(df) + 2))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analyzing destino column...", total=len(df))
        for i, (idx, val) in enumerate(series.items()):
            pos = row_positions[i]
            id_str = id_series.iloc[i]
            if pd.isna(val) or (isinstance(val, str) and val.strip() == ""):
                results['missing'].append({'row': pos, 'ID': id_str})
                progress.update(task, advance=1)
                continue
            # normalize to string
            s = str(val).strip()
            results['frequencies'][s] += 1
            if expected is not None:
                if s.casefold() not in expected:
                    results['deviant_values'].append({'row': pos, 'ID': id_str, 'destino': s})
            progress.update(task, advance=1)

    results['distinct_values'] = sorted(results['frequencies'].items(), key=lambda kv: (-kv[1], kv[0]))
    results['statistics'] = {
        'total_missing': len(results['missing']),
        'distinct_count': len(results['frequencies']),
        'total_deviants': len(results['deviant_values']),
    }
    return results


def display_destino_overview(results: Dict[str, Any]):
    t = Table(title="📦 destino - Overview", style="cyan")
    t.add_column("Metric", style="yellow", width=30)
    t.add_column("Count", justify="right", style="green", width=10)
    t.add_column("Notes", style="magenta")
    s = results['statistics']
    rows = [
        ("Total Rows", results['total_rows'], ""),
        ("Missing", s['total_missing'], "Should be 0"),
        ("Distinct values", s['distinct_count'], ""),
        ("Deviant values", s['total_deviants'], "Not in expected set" if results.get('expected_set') else "No expected set provided"),
    ]
    for metric, count, note in rows:
        t.add_row(str(metric), str(count), str(note))
    console.print(t)

    # Frequencies table (top 20)
    if results['distinct_values']:
        tf = Table(title="destino value frequencies (top 20)")
        tf.add_column("destino", width=30)
        tf.add_column("Count", justify="right", width=8)
        for value, cnt in results['distinct_values'][:20]:
            tf.add_row(str(value), str(cnt))
        if len(results['distinct_values']) > 20:
            tf.add_row("...", f"... and {len(results['distinct_values'])-20} more")
        console.print(tf)

    if results.get('expected_set'):
        exp = ", ".join(results['expected_set'])
        console.print(f"[dim]Expected categories: {exp}[/dim]")


def display_destino_details(results: Dict[str, Any]):
    # Missing rows
    if results['missing']:
        console.print("\n[red]❌ Missing destino values:[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        for e in results['missing'][:20]:
            tt.add_row(str(e['row']), str(e['ID']))
        if len(results['missing']) > 20:
            tt.add_row("...", f"... and {len(results['missing'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ No missing destino values.[/green]")

    # Deviant rows (if expected set provided)
    if results.get('expected_set') and results['deviant_values']:
        console.print("\n[yellow]⚠️ Values not in expected categories:[/yellow]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("destino", width=40)
        for e in results['deviant_values'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['destino']))
        if len(results['deviant_values']) > 20:
            tt.add_row("...", "...", f"... and {len(results['deviant_values'])-20} more")
        console.print(tt)
    elif results.get('expected_set'):
        console.print("\n[green]✅ All destino values are in expected categories.[/green]")


def save_destino_report(results: Dict[str, Any], csv_file: Path) -> Path:
    reports_dir = Path("/home/gusmmm/Desktop/mydb/files/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"BD_doentes_destino_analysis_{timestamp}.md"

    s = results['statistics']
    lines: List[str] = []
    lines.append("# BD_doentes.csv - destino Column Quality Control Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Source File:** {csv_file}\n")
    lines.append("\n## 📊 Summary\n")
    lines.append(f"- Total rows: {results['total_rows']}")
    lines.append(f"- Missing: {s['total_missing']}")
    lines.append(f"- Distinct values: {s['distinct_count']}")
    if results.get('expected_set'):
        lines.append(f"- Deviant values (not in expected): {s['total_deviants']}")
        lines.append("\n### Expected categories\n")
        lines.append(", ".join(results['expected_set']) + "\n")

    # Frequencies (top 100 to keep report usable)
    if results['distinct_values']:
        lines.append("\n### Value Frequencies (top 100)\n")
        lines.append("| destino | Count |")
        lines.append("|---------|-------|")
        for value, cnt in results['distinct_values'][:100]:
            lines.append(f"| {value} | {cnt} |")

    # Deviant rows
    if results.get('expected_set') and results['deviant_values']:
        lines.append("\n### Deviant Rows (first 100)\n")
        lines.append("| Row | ID | destino |")
        lines.append("|-----|----|---------|")
        for e in results['deviant_values'][:100]:
            lines.append(f"| {e['row']} | {e['ID']} | {e['destino']} |")

    # Missing rows
    if results['missing']:
        lines.append("\n### Missing Rows (first 100)\n")
        lines.append("| Row | ID |")
        lines.append("|-----|----|")
        for e in results['missing'][:100]:
            lines.append(f"| {e['row']} | {e['ID']} |")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    console.print(f"\n[green]📄 'destino' report saved to:[/green] {report_file}")
    return report_file

# -------------------------------
# sexo (gender) analysis
# -------------------------------

def _expected_sexo_values() -> set[str]:
    """Return expected 'sexo' categories. Allow override via env var BD_DOENTES_SEXO_EXPECTED (pipe-separated)."""
    env = os.getenv("BD_DOENTES_SEXO_EXPECTED", "").strip()
    if env:
        raw = [v.strip() for v in env.split("|") if v.strip()]
        return set(raw)
    # Default from codebook
    return {"M", "F", "other"}


def analyze_sexo_column(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze 'sexo': check missing and values against expected set (M, F, other)."""
    results: Dict[str, Any] = {
        'total_rows': len(df),
        'missing': [],  # {row, ID}
        'frequencies': Counter(),
        'distinct_values': [],
        'deviant_values': [],  # {row, ID, sexo}
        'statistics': {},
        'expected_set': sorted(list(_expected_sexo_values())),
    }

    if 'sexo' not in df.columns:
        console.print("[red]Column 'sexo' not found in CSV![/red]")
        return results

    expected = _expected_sexo_values()
    expected_cf = {v.casefold() for v in expected}

    series = df['sexo'].astype(object)
    id_series = df['ID'].astype(str)
    row_positions: List[int] = list(range(2, len(df) + 2))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analyzing sexo column...", total=len(df))
        for i, (idx, val) in enumerate(series.items()):
            pos = row_positions[i]
            id_str = id_series.iloc[i]
            if pd.isna(val) or (isinstance(val, str) and val.strip() == ""):
                results['missing'].append({'row': pos, 'ID': id_str})
                progress.update(task, advance=1)
                continue
            s = str(val).strip()
            results['frequencies'][s] += 1
            if s.casefold() not in expected_cf:
                results['deviant_values'].append({'row': pos, 'ID': id_str, 'sexo': s})
            progress.update(task, advance=1)

    results['distinct_values'] = sorted(results['frequencies'].items(), key=lambda kv: (-kv[1], kv[0]))
    results['statistics'] = {
        'total_missing': len(results['missing']),
        'distinct_count': len(results['frequencies']),
        'total_deviants': len(results['deviant_values']),
    }
    return results


def display_sexo_overview(results: Dict[str, Any]):
    t = Table(title="🚻 sexo - Overview", style="cyan")
    t.add_column("Metric", style="yellow", width=28)
    t.add_column("Count", justify="right", style="green", width=10)
    t.add_column("Notes", style="magenta")
    s = results['statistics']
    rows = [
        ("Total Rows", results['total_rows'], ""),
        ("Missing", s['total_missing'], "Should be 0"),
        ("Distinct values", s['distinct_count'], ""),
        ("Deviant values", s['total_deviants'], f"Not in expected: {', '.join(results['expected_set'])}"),
    ]
    for metric, count, note in rows:
        t.add_row(str(metric), str(count), str(note))
    console.print(t)

    # Frequencies (top 20)
    if results['distinct_values']:
        tf = Table(title="sexo value frequencies (top 20)")
        tf.add_column("sexo", width=10)
        tf.add_column("Count", justify="right", width=8)
        for value, cnt in results['distinct_values'][:20]:
            tf.add_row(str(value), str(cnt))
        if len(results['distinct_values']) > 20:
            tf.add_row("...", f"... and {len(results['distinct_values'])-20} more")
        console.print(tf)


def display_sexo_details(results: Dict[str, Any]):
    # Missing
    if results['missing']:
        console.print("\n[red]❌ Missing sexo values:[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        for e in results['missing'][:20]:
            tt.add_row(str(e['row']), str(e['ID']))
        if len(results['missing']) > 20:
            tt.add_row("...", f"... and {len(results['missing'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ No missing sexo values.[/green]")

    # Deviants
    if results['deviant_values']:
        console.print("\n[yellow]⚠️ Values not in expected categories (M, F, other):[/yellow]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("sexo", width=12)
        for e in results['deviant_values'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['sexo']))
        if len(results['deviant_values']) > 20:
            tt.add_row("...", "...", f"... and {len(results['deviant_values'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ All sexo values are within expected categories.[/green]")


def save_sexo_report(results: Dict[str, Any], csv_file: Path) -> Path:
    reports_dir = Path("/home/gusmmm/Desktop/mydb/files/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"BD_doentes_sexo_analysis_{timestamp}.md"

    s = results['statistics']
    lines: List[str] = []
    lines.append("# BD_doentes.csv - sexo Column Quality Control Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Source File:** {csv_file}\n")
    lines.append("\n## 📊 Summary\n")
    lines.append(f"- Total rows: {results['total_rows']}")
    lines.append(f"- Missing: {s['total_missing']}")
    lines.append(f"- Distinct values: {s['distinct_count']}")
    lines.append(f"- Deviant values (not in expected {{ {', '.join(results['expected_set'])} }}): {s['total_deviants']}\n")

    # Frequencies
    if results['distinct_values']:
        lines.append("### Value Frequencies (top 100)\n")
        lines.append("| sexo | Count |")
        lines.append("|------|-------|")
        for value, cnt in results['distinct_values'][:100]:
            lines.append(f"| {value} | {cnt} |")

    if results['deviant_values']:
        lines.append("\n### Deviant Rows (first 100)\n")
        lines.append("| Row | ID | sexo |")
        lines.append("|-----|----|------|")
        for e in results['deviant_values'][:100]:
            lines.append(f"| {e['row']} | {e['ID']} | {e['sexo']} |")

    if results['missing']:
        lines.append("\n### Missing Rows (first 100)\n")
        lines.append("| Row | ID |")
        lines.append("|-----|----|")
        for e in results['missing'][:100]:
            lines.append(f"| {e['row']} | {e['ID']} |")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    console.print(f"\n[green]📄 'sexo' report saved to:[/green] {report_file}")
    return report_file

# -------------------------------
# data_nasc (birth date) analysis
# -------------------------------

def analyze_data_nasc_column(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data_nasc (birthdate):
    - missing
    - strict DD-MM-YYYY format (with fallback parsing for calculations)
    - birth year bounds: >1900 and < current year
    - compute age at admission using data_ent (assumption: 'data_int' in request refers to 'data_ent')
    - flag deviants and outliers: invalid year, negative age, age > 120
    """
    now_year = datetime.now().year
    results: Dict[str, Any] = {
        'total_rows': len(df),
        'missing': [],  # {row, ID}
        'invalid_format': [],  # {row, ID, data_nasc}
        'unparseable_count': 0,
        'strict_valid_count': 0,
        'parsed_loose_count': 0,
        'year_out_of_bounds': [],  # {row, ID, data_nasc, year}
        'age_records': [],  # {row, ID, data_ent, data_nasc, age}
        'age_negative': [],  # {row, ID, data_ent, data_nasc, age}
        'age_over_max': [],  # {row, ID, data_ent, data_nasc, age}
        'age_uncomputed': [],  # {row, ID, reason}
        'statistics': {},
    }

    if 'data_nasc' not in df.columns:
        console.print("[red]Column 'data_nasc' not found in CSV![/red]")
        return results

    series_nasc = df['data_nasc'].astype(object)
    series_ent = df['data_ent'].astype(object) if 'data_ent' in df.columns else None
    id_series = df['ID'].astype(str)

    row_positions: List[int] = list(range(2, len(df) + 2))

    parsed_nasc: List[Optional[pd.Timestamp]] = [None] * len(df)
    parsed_ent: List[Optional[pd.Timestamp]] = [None] * len(df)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analyzing data_nasc column...", total=len(df))
        for i, (idx, val) in enumerate(series_nasc.items()):
            pos = row_positions[i]
            id_str = id_series.iloc[i]
            raw_nasc = None if pd.isna(val) else str(val).strip()
            if raw_nasc is None or raw_nasc == "":
                results['missing'].append({'row': pos, 'ID': id_str})
                parsed_nasc[i] = None
                results['unparseable_count'] += 1
                progress.update(task, advance=1)
                continue

            is_strict = _is_strict_dd_mm_yyyy(raw_nasc)
            if not is_strict:
                results['invalid_format'].append({'row': pos, 'ID': id_str, 'data_nasc': raw_nasc})
            dt_nasc = _parse_date_loose(raw_nasc)
            if dt_nasc is None:
                results['unparseable_count'] += 1
                parsed_nasc[i] = None
            else:
                parsed_nasc[i] = dt_nasc
                if is_strict:
                    results['strict_valid_count'] += 1
                else:
                    results['parsed_loose_count'] += 1
                # check year bounds
                if not (1900 < int(dt_nasc.year) < now_year):
                    results['year_out_of_bounds'].append({'row': pos, 'ID': id_str, 'data_nasc': raw_nasc, 'year': int(dt_nasc.year)})

            # parse data_ent to compute age
            if series_ent is not None:
                raw_ent = None if pd.isna(series_ent.iloc[i]) else str(series_ent.iloc[i]).strip()
                dt_ent = _parse_date_loose(raw_ent) if raw_ent else None
                parsed_ent[i] = dt_ent

            progress.update(task, advance=1)

    # Compute ages
    for i in range(len(df)):
        pos = row_positions[i]
        id_str = id_series.iloc[i]
        bn = parsed_nasc[i]
        ad = parsed_ent[i] if series_ent is not None else None
        if bn is None or ad is None:
            reason = "birthdate missing/unparseable" if bn is None else "admission date missing/unparseable"
            results['age_uncomputed'].append({'row': pos, 'ID': id_str, 'reason': reason})
            continue
        # Age computation: whole years at admission
        age = int(ad.year - bn.year - ((ad.month, ad.day) < (bn.month, bn.day)))
        rec = {'row': pos, 'ID': id_str, 'data_ent': str(df['data_ent'].iloc[i]), 'data_nasc': str(df['data_nasc'].iloc[i]), 'age': age}
        results['age_records'].append(rec)
        if age < 0:
            results['age_negative'].append(rec)
        if age > 120:
            results['age_over_max'].append(rec)

    # Stats for ages
    ages = [r['age'] for r in results['age_records']]
    if ages:
        ages_series = pd.Series(ages)
        stats = {
            'age_count': int(len(ages)),
            'age_min': int(ages_series.min()),
            'age_max': int(ages_series.max()),
            'age_mean': float(round(ages_series.mean(), 2)),
            'age_median': float(ages_series.median()),
        }
    else:
        stats = {
            'age_count': 0,
            'age_min': None,
            'age_max': None,
            'age_mean': None,
            'age_median': None,
        }

    results['statistics'] = {
        'total_missing': len(results['missing']),
        'total_invalid_format': len(results['invalid_format']),
        'strict_valid_count': results['strict_valid_count'],
        'parsed_loose_count': results['parsed_loose_count'],
        'unparseable_count': results['unparseable_count'],
        'year_out_of_bounds': len(results['year_out_of_bounds']),
        'age_computed': stats['age_count'],
        'age_uncomputed': len(results['age_uncomputed']),
        'age_negative': len(results['age_negative']),
        'age_over_max': len(results['age_over_max']),
        'age_min': stats['age_min'],
        'age_max': stats['age_max'],
        'age_mean': stats['age_mean'],
        'age_median': stats['age_median'],
    }
    return results


def display_data_nasc_overview(results: Dict[str, Any]):
    t = Table(title="👶 data_nasc - Overview", style="cyan")
    t.add_column("Metric", style="yellow", width=34)
    t.add_column("Count/Value", justify="right", style="green", width=14)
    t.add_column("Notes", style="magenta")
    s = results['statistics']
    rows = [
        ("Total Rows", results['total_rows'], ""),
        ("Missing", s['total_missing'], "Should be 0"),
        ("Invalid Format (not DD-MM-YYYY)", s['total_invalid_format'], ""),
        ("Strict valid (DD-MM-YYYY)", s['strict_valid_count'], ""),
        ("Parsed via fallback", s['parsed_loose_count'], "Accepted for calculations"),
        ("Unparseable", s['unparseable_count'], ""),
        ("Year out of bounds", s['year_out_of_bounds'], ">1900 and < current year"),
        ("Ages computed", s['age_computed'], "Using data_ent"),
        ("Ages uncomputed", s['age_uncomputed'], "Missing/unparseable dates"),
        ("Age negative (<0)", s['age_negative'], "Birth after admission"),
        ("Age > 120", s['age_over_max'], "Outlier upper bound"),
        ("Age min", s['age_min'], ""),
        ("Age max", s['age_max'], ""),
        ("Age mean", s['age_mean'], ""),
        ("Age median", s['age_median'], ""),
    ]
    for metric, count, note in rows:
        t.add_row(str(metric), str(count), str(note))
    console.print(t)


def display_data_nasc_details(results: Dict[str, Any]):
    # Missing
    if results['missing']:
        console.print("\n[red]❌ Missing data_nasc values:[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        for e in results['missing'][:20]:
            tt.add_row(str(e['row']), str(e['ID']))
        if len(results['missing']) > 20:
            tt.add_row("...", f"... and {len(results['missing'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ No missing data_nasc values.[/green]")

    # Invalid format
    if results['invalid_format']:
        console.print("\n[yellow]⚠️ Invalid format (expected DD-MM-YYYY):[/yellow]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("data_nasc", width=14)
        for e in results['invalid_format'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['data_nasc']))
        if len(results['invalid_format']) > 20:
            tt.add_row("...", "...", f"... and {len(results['invalid_format'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ All data_nasc values match DD-MM-YYYY format.[/green]")

    # Year out of bounds
    if results['year_out_of_bounds']:
        console.print("\n[red]❌ Birth year out of bounds (>1900 and < current year):[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("data_nasc", width=14)
        tt.add_column("Year", justify="right", width=6)
        for e in results['year_out_of_bounds'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['data_nasc']), str(e['year']))
        if len(results['year_out_of_bounds']) > 20:
            tt.add_row("...", "...", "...", f"... and {len(results['year_out_of_bounds'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ All birth years within bounds.[/green]")

    # Negative ages
    if results['age_negative']:
        console.print("\n[red]❌ Negative ages (birth after admission):[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("data_ent", width=14)
        tt.add_column("data_nasc", width=14)
        tt.add_column("Age", justify="right", width=6)
        for e in results['age_negative'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['data_ent']), str(e['data_nasc']), str(e['age']))
        if len(results['age_negative']) > 20:
            tt.add_row("...", "...", "...", "...", f"... and {len(results['age_negative'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ No negative ages detected.[/green]")

    # Over max ages
    if results['age_over_max']:
        console.print("\n[red]❌ Ages over 120 (outliers):[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("data_ent", width=14)
        tt.add_column("data_nasc", width=14)
        tt.add_column("Age", justify="right", width=6)
        for e in results['age_over_max'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['data_ent']), str(e['data_nasc']), str(e['age']))
        if len(results['age_over_max']) > 20:
            tt.add_row("...", "...", "...", "...", f"... and {len(results['age_over_max'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ No ages over 120 detected.[/green]")


def save_data_nasc_report(results: Dict[str, Any], csv_file: Path) -> Path:
    reports_dir = Path("/home/gusmmm/Desktop/mydb/files/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"BD_doentes_data_nasc_analysis_{timestamp}.md"
    s = results['statistics']

    lines: List[str] = []
    lines.append("# BD_doentes.csv - data_nasc Column Quality Control Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Source File:** {csv_file}\n")
    lines.append("\n## 📊 Summary\n")
    lines.append(f"- Total rows: {results['total_rows']}")
    lines.append(f"- Missing: {s['total_missing']}")
    lines.append(f"- Invalid format (not DD-MM-YYYY): {s['total_invalid_format']}")
    lines.append(f"- Strict valid (DD-MM-YYYY): {s['strict_valid_count']}")
    lines.append(f"- Parsed via fallback: {s['parsed_loose_count']}")
    lines.append(f"- Unparseable: {s['unparseable_count']}")
    lines.append(f"- Birth year out of bounds: {s['year_out_of_bounds']} (expected >1900 and < current year)\n")

    # Age stats
    lines.append("## 🧮 Age Statistics (at admission)\n")
    lines.append(f"- Ages computed: {s['age_computed']} (uncomputed: {s['age_uncomputed']})")
    lines.append(f"- Min / Max: {s['age_min']} / {s['age_max']}")
    lines.append(f"- Mean / Median: {s['age_mean']} / {s['age_median']}\n")

    # Deviations/outliers tables
    def tbl(rows: List[Dict[str, Any]], headers: List[str], keys: List[str], title: str, limit: int = 50):
        nonlocal lines
        if not rows:
            return
        lines.append(f"\n### {title}\n")
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(['-'*len(h) for h in headers]) + " |")
        for e in rows[:limit]:
            values = [str(e.get(k, '')) for k in keys]
            lines.append("| " + " | ".join(values) + " |")
        if len(rows) > limit:
            lines.append("| ... | ... | ... | ... | ... | ... |")

    tbl(results['invalid_format'], ["Row", "ID", "data_nasc"], ["row", "ID", "data_nasc"], "Invalid format (first 50)")
    tbl(results['year_out_of_bounds'], ["Row", "ID", "data_nasc", "Year"], ["row", "ID", "data_nasc", "year"], "Birth year out of bounds (first 50)")
    tbl(results['age_negative'], ["Row", "ID", "data_ent", "data_nasc", "Age"], ["row", "ID", "data_ent", "data_nasc", "age"], "Negative ages (first 50)")
    tbl(results['age_over_max'], ["Row", "ID", "data_ent", "data_nasc", "Age"], ["row", "ID", "data_ent", "data_nasc", "age"], "Ages over 120 (first 50)")

    # Missing / uncomputed
    if results['missing']:
        lines.append("\n### Missing data_nasc Rows (first 100)\n")
        lines.append("| Row | ID |")
        lines.append("|-----|----|")
        for e in results['missing'][:100]:
            lines.append(f"| {e['row']} | {e['ID']} |")
    if results['age_uncomputed']:
        lines.append("\n### Age Uncomputed (first 100)\n")
        lines.append("| Row | ID | Reason |")
        lines.append("|-----|----|--------|")
        for e in results['age_uncomputed'][:100]:
            lines.append(f"| {e['row']} | {e['ID']} | {e['reason']} |")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    console.print(f"\n[green]📄 'data_nasc' report saved to:[/green] {report_file}")
    return report_file

# -------------------------------
# origem (admission source) analysis
# -------------------------------

def analyze_origem_column(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze 'origem':
    - check missing/empty
    - compute full value frequencies (string values)
    """
    results: Dict[str, Any] = {
        'total_rows': len(df),
        'missing': [],  # {row, ID}
        'frequencies': Counter(),
        'distinct_values': [],
        'statistics': {},
    }

    if 'origem' not in df.columns:
        console.print("[red]Column 'origem' not found in CSV![/red]")
        return results

    series = df['origem'].astype(object)
    id_series = df['ID'].astype(str)
    row_positions: List[int] = list(range(2, len(df) + 2))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analyzing origem column...", total=len(df))
        for i, (idx, val) in enumerate(series.items()):
            pos = row_positions[i]
            id_str = id_series.iloc[i]
            if pd.isna(val) or (isinstance(val, str) and val.strip() == ""):
                results['missing'].append({'row': pos, 'ID': id_str})
                progress.update(task, advance=1)
                continue
            s = str(val).strip()
            results['frequencies'][s] += 1
            progress.update(task, advance=1)

    results['distinct_values'] = sorted(results['frequencies'].items(), key=lambda kv: (-kv[1], kv[0]))
    results['statistics'] = {
        'total_missing': len(results['missing']),
        'distinct_count': len(results['frequencies']),
    }
    return results


def display_origem_overview(results: Dict[str, Any]):
    t = Table(title="📥 origem - Overview", style="cyan")
    t.add_column("Metric", style="yellow", width=28)
    t.add_column("Count", justify="right", style="green", width=10)
    t.add_column("Notes", style="magenta")
    s = results['statistics']
    rows = [
        ("Total Rows", results['total_rows'], ""),
        ("Missing", s['total_missing'], "Should be 0"),
        ("Distinct values", s['distinct_count'], ""),
    ]
    for metric, count, note in rows:
        t.add_row(str(metric), str(count), str(note))
    console.print(t)

    # Show all value frequencies
    if results['distinct_values']:
        tf = Table(title="origem value frequencies (all)")
        tf.add_column("origem", width=34)
        tf.add_column("Count", justify="right", width=8)
        for value, cnt in results['distinct_values']:
            tf.add_row(str(value), str(cnt))
        console.print(tf)


def display_origem_details(results: Dict[str, Any]):
    # Missing rows (show all)
    if results['missing']:
        console.print("\n[red]❌ Missing origem values:[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        for e in results['missing']:
            tt.add_row(str(e['row']), str(e['ID']))
        console.print(tt)
    else:
        console.print("\n[green]✅ No missing origem values.[/green]")


def save_origem_report(results: Dict[str, Any], csv_file: Path) -> Path:
    reports_dir = Path("/home/gusmmm/Desktop/mydb/files/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"BD_doentes_origem_analysis_{timestamp}.md"

    s = results['statistics']
    lines: List[str] = []
    lines.append("# BD_doentes.csv - origem Column Quality Control Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Source File:** {csv_file}\n")
    lines.append("\n## 📊 Summary\n")
    lines.append(f"- Total rows: {results['total_rows']}")
    lines.append(f"- Missing: {s['total_missing']}")
    lines.append(f"- Distinct values: {s['distinct_count']}\n")

    # All frequencies
    if results['distinct_values']:
        lines.append("### Value Frequencies (all)\n")
        lines.append("| origem | Count |")
        lines.append("|--------|-------|")
        for value, cnt in results['distinct_values']:
            lines.append(f"| {value} | {cnt} |")

    # Missing rows
    if results['missing']:
        lines.append("\n### Missing Rows\n")
        lines.append("| Row | ID |")
        lines.append("|-----|----|")
        for e in results['missing']:
            lines.append(f"| {e['row']} | {e['ID']} |")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    console.print(f"\n[green]📄 'origem' report saved to:[/green] {report_file}")
    return report_file

# -------------------------------
# ASCQ (burn surface area) analysis
# -------------------------------

def analyze_ASCQ_column(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze 'ASCQ':
    - check missing/empty
    - validate range: digit between 1 and 100
    """
    results: Dict[str, Any] = {
        'total_rows': len(df),
        'missing': [],  # {row, ID}
        'non_digit': [],  # {row, ID, ASCQ}
        'out_of_range': [],  # {row, ID, ASCQ, value}
        'valid_values': [],  # {row, ID, ASCQ, value}
        'statistics': {},
    }

    if 'ASCQ' not in df.columns:
        console.print("[red]Column 'ASCQ' not found in CSV![/red]")
        return results

    series = df['ASCQ'].astype(object)
    id_series = df['ID'].astype(str)
    row_positions: List[int] = list(range(2, len(df) + 2))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analyzing ASCQ column...", total=len(df))
        for i, (idx, val) in enumerate(series.items()):
            pos = row_positions[i]
            id_str = id_series.iloc[i]
            if pd.isna(val) or (isinstance(val, str) and val.strip() == ""):
                results['missing'].append({'row': pos, 'ID': id_str})
                progress.update(task, advance=1)
                continue
            
            s = str(val).strip()
            if not s.isdigit():
                results['non_digit'].append({'row': pos, 'ID': id_str, 'ASCQ': s})
            else:
                num_val = int(s)
                if not (1 <= num_val <= 100):
                    results['out_of_range'].append({'row': pos, 'ID': id_str, 'ASCQ': s, 'value': num_val})
                else:
                    results['valid_values'].append({'row': pos, 'ID': id_str, 'ASCQ': s, 'value': num_val})
            progress.update(task, advance=1)

    results['statistics'] = {
        'total_missing': len(results['missing']),
        'total_non_digit': len(results['non_digit']),
        'total_out_of_range': len(results['out_of_range']),
        'total_valid': len(results['valid_values']),
    }
    
    # Add value statistics for valid values
    if results['valid_values']:
        values = [v['value'] for v in results['valid_values']]
        values_series = pd.Series(values)
        results['statistics'].update({
            'min_value': int(values_series.min()),
            'max_value': int(values_series.max()),
            'mean_value': float(round(values_series.mean(), 2)),
            'median_value': float(values_series.median()),
        })
    else:
        results['statistics'].update({
            'min_value': None,
            'max_value': None,
            'mean_value': None,
            'median_value': None,
        })
    
    return results


def display_ASCQ_overview(results: Dict[str, Any]):
    t = Table(title="🔥 ASCQ - Overview", style="cyan")
    t.add_column("Metric", style="yellow", width=28)
    t.add_column("Count/Value", justify="right", style="green", width=12)
    t.add_column("Notes", style="magenta")
    s = results['statistics']
    rows = [
        ("Total Rows", results['total_rows'], ""),
        ("Missing", s['total_missing'], "Should be 0"),
        ("Non-digit", s['total_non_digit'], "Should be digits only"),
        ("Out of range (not 1-100)", s['total_out_of_range'], "Must be 1-100"),
        ("Valid values", s['total_valid'], "Within range 1-100"),
        ("Min value", s['min_value'], ""),
        ("Max value", s['max_value'], ""),
        ("Mean value", s['mean_value'], ""),
        ("Median value", s['median_value'], ""),
    ]
    for metric, count, note in rows:
        t.add_row(str(metric), str(count), str(note))
    console.print(t)


def display_ASCQ_details(results: Dict[str, Any]):
    # Missing values
    if results['missing']:
        console.print("\n[red]❌ Missing ASCQ values:[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        for e in results['missing'][:20]:
            tt.add_row(str(e['row']), str(e['ID']))
        if len(results['missing']) > 20:
            tt.add_row("...", f"... and {len(results['missing'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ No missing ASCQ values.[/green]")

    # Non-digit values
    if results['non_digit']:
        console.print("\n[red]❌ Non-digit ASCQ values:[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("ASCQ", width=12)
        for e in results['non_digit'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['ASCQ']))
        if len(results['non_digit']) > 20:
            tt.add_row("...", "...", f"... and {len(results['non_digit'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ All ASCQ values are digits.[/green]")

    # Out of range values
    if results['out_of_range']:
        console.print("\n[red]❌ ASCQ values out of range (not 1-100):[/red]")
        tt = Table()
        tt.add_column("Row", justify="right", width=6)
        tt.add_column("ID", width=8)
        tt.add_column("ASCQ", width=12)
        tt.add_column("Value", justify="right", width=8)
        for e in results['out_of_range'][:20]:
            tt.add_row(str(e['row']), str(e['ID']), str(e['ASCQ']), str(e['value']))
        if len(results['out_of_range']) > 20:
            tt.add_row("...", "...", "...", f"... and {len(results['out_of_range'])-20} more")
        console.print(tt)
    else:
        console.print("\n[green]✅ All ASCQ values are within range (1-100).[/green]")


def save_ASCQ_report(results: Dict[str, Any], csv_file: Path) -> Path:
    reports_dir = Path("/home/gusmmm/Desktop/mydb/files/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"BD_doentes_ASCQ_analysis_{timestamp}.md"

    s = results['statistics']
    lines: List[str] = []
    lines.append("# BD_doentes.csv - ASCQ Column Quality Control Report\n")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**Source File:** {csv_file}\n")
    lines.append("\n## 📊 Summary\n")
    lines.append(f"- Total rows: {results['total_rows']}")
    lines.append(f"- Missing: {s['total_missing']}")
    lines.append(f"- Non-digit: {s['total_non_digit']}")
    lines.append(f"- Out of range (not 1-100): {s['total_out_of_range']}")
    lines.append(f"- Valid values: {s['total_valid']}")
    
    if s['total_valid'] > 0:
        lines.append(f"\n## 📈 Value Statistics (valid values only)\n")
        lines.append(f"- Min: {s['min_value']}")
        lines.append(f"- Max: {s['max_value']}")
        lines.append(f"- Mean: {s['mean_value']}")
        lines.append(f"- Median: {s['median_value']}")

    # Tables for issues
    def tbl(rows: List[Dict[str, Any]], headers: List[str], keys: List[str], title: str, limit: int = 100):
        nonlocal lines
        if not rows:
            return
        lines.append(f"\n### {title}\n")
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["-"*len(h) for h in headers]) + " |")
        for e in rows[:limit]:
            values = [str(e.get(k, '')) for k in keys]
            lines.append("| " + " | ".join(values) + " |")
        if len(rows) > limit:
            lines.append("| ... | ... | ... | ... |")

    tbl(results['missing'], ["Row", "ID"], ["row", "ID"], "Missing ASCQ Values (first 100)")
    tbl(results['non_digit'], ["Row", "ID", "ASCQ"], ["row", "ID", "ASCQ"], "Non-digit ASCQ Values (first 100)")
    tbl(results['out_of_range'], ["Row", "ID", "ASCQ", "Value"], ["row", "ID", "ASCQ", "value"], "Out-of-range ASCQ Values (first 100)")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    console.print(f"\n[green]📄 'ASCQ' report saved to:[/green] {report_file}")
    return report_file

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

def save_detailed_report(results: dict, csv_file: Path):
    """Save a detailed markdown report to the reports directory"""
    
    # Create reports directory if it doesn't exist
    reports_dir = Path("/home/gusmmm/Desktop/mydb/files/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for the report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"BD_doentes_ID_analysis_{timestamp}.md"
    
    stats = results['statistics']
    
    report_content = f"""# BD_doentes.csv - ID Column Quality Control Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Source File:** {csv_file}
**Analysis Script:** BD_doentes_quality.py

## 📊 Executive Summary

The quality control analysis of the ID column in BD_doentes.csv reveals the following:

### ✅ **Excellent Data Quality Overall**
- **{results['total_rows']} total rows** analyzed
- **{stats['total_empty']} empty values** ({100 - (stats['total_empty']/results['total_rows']*100):.1f}% completeness)
- **{stats['total_invalid_format']} invalid formats** (all IDs are proper 3 or 4 digit numbers)
- **{stats['total_duplicates']} duplicate IDs** (perfect uniqueness)
- **{stats['total_valid']} valid IDs** ({stats['total_valid']/results['total_rows']*100:.1f}% validity rate)

### 📅 **Coverage Analysis**
- **{stats['years_covered']} years covered**: {', '.join(map(str, sorted(results['year_series'].keys())))}
- **{stats['total_missing_serials']} missing serial numbers** across all years
"""

    if stats['total_missing_serials'] > 0:
        report_content += f"""
### ⚠️ **Data Issues Found**

#### **Missing Serials by Year**
"""
        for year in sorted(results['missing_serials'].keys()):
            missing = results['missing_serials'][year]
            if missing:
                report_content += f"- **Year {year}**: {len(missing)} missing serials ({', '.join(map(str, missing[:10]))}{'...' if len(missing) > 10 else ''})\n"

    report_content += f"""
### 🔍 **ID Format Distribution**
- **{stats['total_valid_3_digit']}** ({stats['total_valid_3_digit']/results['total_rows']*100:.1f}%) use 3-digit format (years 2006-2014)
- **{stats['total_valid_4_digit']}** ({stats['total_valid_4_digit']/results['total_rows']*100:.1f}%) use 4-digit format (years 2021-2025)

### 📋 **Year-by-Year Breakdown**

| Year | Count | Serial Range | Status | Missing Serials |
|------|-------|--------------|--------|-----------------|
"""

    for year in sorted(results['year_series'].keys()):
        entries = results['year_series'][year]
        count = len(entries)
        serials = [entry['serial'] for entry in entries]
        min_serial = min(serials)
        max_serial = max(serials)
        missing = results['missing_serials'][year]
        
        status = "✅ Complete" if not missing else f"❌ {len(missing)} gaps"
        missing_str = "0" if not missing else str(len(missing))
        
        report_content += f"| {year} | {count} | {min_serial:02d}-{max_serial:02d} | {status} | {missing_str} |\n"

    if results['empty_values']:
        report_content += f"""
### 🚫 **Empty Values Found** ({len(results['empty_values'])})

| Row | Patient Name |
|-----|-------------|
"""
        for entry in results['empty_values'][:20]:  # Show first 20
            report_content += f"| {entry['row']} | {entry['nome']} |\n"
        
        if len(results['empty_values']) > 20:
            report_content += f"| ... | *{len(results['empty_values']) - 20} more entries* |\n"

    if results['invalid_format']:
        report_content += f"""
### ❌ **Invalid Format Found** ({len(results['invalid_format'])})

| Row | Invalid ID | Patient Name |
|-----|-----------|-------------|
"""
        for entry in results['invalid_format'][:20]:  # Show first 20
            report_content += f"| {entry['row']} | {entry['value']} | {entry['nome']} |\n"
        
        if len(results['invalid_format']) > 20:
            report_content += f"| ... | ... | *{len(results['invalid_format']) - 20} more entries* |\n"

    if results['duplicate_ids']:
        report_content += f"""
### 🔄 **Duplicate IDs Found** ({len(results['duplicate_ids'])})

| ID | Count |
|----|-------|
"""
        for entry in results['duplicate_ids']:
            report_content += f"| {entry['id']} | {entry['count']} |\n"

    report_content += f"""
### 🎯 **Recommendations**

"""
    
    if stats['total_empty'] > 0:
        report_content += f"1. **Fix {stats['total_empty']} empty ID values** - These records cannot be properly identified\n"
    
    if stats['total_invalid_format'] > 0:
        report_content += f"2. **Fix {stats['total_invalid_format']} invalid ID formats** - Ensure all IDs follow 3 or 4 digit format\n"
    
    if stats['total_duplicates'] > 0:
        report_content += f"3. **Resolve {stats['total_duplicates']} duplicate IDs** - Each patient should have unique identifier\n"
    
    if stats['total_missing_serials'] > 0:
        report_content += f"4. **Investigate {stats['total_missing_serials']} missing serial numbers** - Check source systems for missing records\n"
    
    if (stats['total_empty'] == 0 and 
        stats['total_invalid_format'] == 0 and 
        stats['total_duplicates'] == 0 and 
        stats['total_missing_serials'] == 0):
        report_content += "✅ **All ID values are valid and complete!** No action required.\n"

    report_content += f"""
### 🏥 **Clinical Impact Assessment**

- **Data Quality Score**: {((stats['total_valid'] - stats['total_missing_serials']) / results['total_rows'] * 100):.1f}%
- **Reliability for Studies**: {"High" if stats['total_missing_serials'] < 50 else "Medium" if stats['total_missing_serials'] < 100 else "Low"}
- **Trend Analysis Suitability**: {"Excellent" if stats['years_covered'] >= 10 else "Good" if stats['years_covered'] >= 5 else "Limited"}

---

*Report generated by BD_doentes_quality.py v1.0*
*Analysis completed in {results.get('analysis_time', 'N/A')} seconds*
"""

    # Save the report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    console.print(f"\n[green]📄 Detailed report saved to:[/green] {report_file}")
    return report_file

def main():
    """Main function to run the quality control analysis"""
    
    start_time = datetime.now()
    
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
    
    # Calculate analysis time
    end_time = datetime.now()
    analysis_time = (end_time - start_time).total_seconds()
    results['analysis_time'] = f"{analysis_time:.2f}"
    
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
    
    # Save detailed report for ID
    report_file = save_detailed_report(results, csv_file)
    
    # -------------------------------------------------------
    # Processo analysis
    # -------------------------------------------------------
    console.print("\n" + "="*80)
    console.print("[bold]🧾 Analyzing column: processo[/bold]")
    proc_results = analyze_processo_column(df)
    display_processo_overview(proc_results)
    display_processo_details(proc_results)
    proc_report = save_processo_report(proc_results, csv_file)

    # -------------------------------------------------------
    # Nome analysis
    # -------------------------------------------------------
    console.print("\n" + "="*80)
    console.print("[bold]🧑‍⚕️ Analyzing column: nome[/bold]")
    nome_results = analyze_nome_column(df)
    display_nome_overview(nome_results)
    display_nome_details(nome_results)
    nome_report = save_nome_report(nome_results, csv_file)

    # -------------------------------------------------------
    # data_ent analysis
    # -------------------------------------------------------
    console.print("\n" + "="*80)
    console.print("[bold]📅 Analyzing column: data_ent[/bold]")
    data_ent_results = analyze_data_ent_column(df)
    display_data_ent_overview(data_ent_results)
    display_data_ent_details(data_ent_results)
    data_ent_report = save_data_ent_report(data_ent_results, csv_file)

    # -------------------------------------------------------
    # data_alta analysis
    # -------------------------------------------------------
    console.print("\n" + "="*80)
    console.print("[bold]📆 Analyzing column: data_alta[/bold]")
    data_alta_results = analyze_data_alta_column(df)
    display_data_alta_overview(data_alta_results)
    display_data_alta_details(data_alta_results)
    data_alta_report = save_data_alta_report(data_alta_results, csv_file)

    console.print(f"\n[bold green]✅ Analysis complete![/bold green]")
    console.print(f"[cyan]📊 Analysis time:[/cyan] {analysis_time:.2f} seconds")
    console.print(f"[cyan]📄 ID report:[/cyan] {report_file}")
    console.print(f"[cyan]📄 processo report:[/cyan] {proc_report}")
    console.print(f"[cyan]📄 nome report:[/cyan] {nome_report}")
    console.print(f"[cyan]📄 data_ent report:[/cyan] {data_ent_report}")
    console.print(f"[cyan]📄 data_alta report:[/cyan] {data_alta_report}")
    
    # -------------------------------------------------------
    # destino analysis
    # -------------------------------------------------------
    console.print("\n" + "="*80)
    console.print("[bold]📦 Analyzing column: destino[/bold]")
    destino_results = analyze_destino_column(df)
    display_destino_overview(destino_results)
    display_destino_details(destino_results)
    destino_report = save_destino_report(destino_results, csv_file)

    # Final summary
    console.print(f"[cyan]📄 destino report:[/cyan] {destino_report}")

    # -------------------------------------------------------
    # sexo analysis
    # -------------------------------------------------------
    console.print("\n" + "="*80)
    console.print("[bold]🚻 Analyzing column: sexo[/bold]")
    sexo_results = analyze_sexo_column(df)
    display_sexo_overview(sexo_results)
    display_sexo_details(sexo_results)
    sexo_report = save_sexo_report(sexo_results, csv_file)
    console.print(f"[cyan]📄 sexo report:[/cyan] {sexo_report}")

    # -------------------------------------------------------
    # data_nasc analysis
    # -------------------------------------------------------
    console.print("\n" + "="*80)
    console.print("[bold]👶 Analyzing column: data_nasc[/bold]")
    data_nasc_results = analyze_data_nasc_column(df)
    display_data_nasc_overview(data_nasc_results)
    display_data_nasc_details(data_nasc_results)
    data_nasc_report = save_data_nasc_report(data_nasc_results, csv_file)
    console.print(f"[cyan]📄 data_nasc report:[/cyan] {data_nasc_report}")

    # -------------------------------------------------------
    # origem analysis
    # -------------------------------------------------------
    console.print("\n" + "="*80)
    console.print("[bold]📥 Analyzing column: origem[/bold]")
    origem_results = analyze_origem_column(df)
    display_origem_overview(origem_results)
    display_origem_details(origem_results)
    origem_report = save_origem_report(origem_results, csv_file)
    console.print(f"[cyan]📄 origem report:[/cyan] {origem_report}")

    # -------------------------------------------------------
    # ASCQ analysis
    # -------------------------------------------------------
    console.print("\n" + "="*80)
    console.print("[bold]🔥 Analyzing column: ASCQ[/bold]")
    ASCQ_results = analyze_ASCQ_column(df)
    display_ASCQ_overview(ASCQ_results)
    display_ASCQ_details(ASCQ_results)
    ASCQ_report = save_ASCQ_report(ASCQ_results, csv_file)
    console.print(f"[cyan]📄 ASCQ report:[/cyan] {ASCQ_report}")

if __name__ == "__main__":
    main()
