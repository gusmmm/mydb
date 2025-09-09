#!/usr/bin/env python3
"""
Database relationship testing script
Tests joins and foreign key relationships between tables
"""

from src.db import engine
from sqlalchemy import text
import sys

def print_separator(title):
    """Print a formatted separator with title"""
    print("\n" + "="*80)
    print(f"{title:^80}")
    print("="*80)

def print_query_results(title, query, conn):
    """Execute query and print results in a formatted table"""
    print_separator(title)
    print(f"Query: {query.strip()}")
    print("-"*80)
    
    try:
        result = conn.execute(text(query))
        rows = result.fetchall()
        columns = list(result.keys())
        
        if not rows:
            print("No results found.")
            return
        
        # Calculate column widths
        col_widths = []
        for i, col in enumerate(columns):
            max_width = max(len(str(col)), max(len(str(row[i])) for row in rows))
            col_widths.append(min(max_width, 25))  # Max width 25 chars
        
        # Print header
        header = " | ".join(str(col)[:col_widths[i]].ljust(col_widths[i]) 
                           for i, col in enumerate(columns))
        print(header)
        print("-" * len(header))
        
        # Print rows
        for row in rows:
            row_str = " | ".join(str(row[i])[:col_widths[i]].ljust(col_widths[i]) 
                                for i in range(len(row)))
            print(row_str)
        
        print(f"\nTotal rows: {len(rows)}")
        
    except Exception as e:
        print(f"Error executing query: {e}")

def main():
    """Main function to run all database tests"""
    conn = engine.connect()
    
    try:
        # Query 1: Table overview
        print_query_results(
            "DATABASE OVERVIEW - TABLE RECORD COUNTS",
            """SELECT 
                'doente' as table_name, COUNT(*) as record_count FROM doente
                UNION ALL
                SELECT 'internamento', COUNT(*) FROM internamento
                UNION ALL
                SELECT 'tipoacidente', COUNT(*) FROM tipoacidente
                UNION ALL
                SELECT 'agentequeimadura', COUNT(*) FROM agentequeimadura""",
            conn
        )

        # Query 2: Patients with internamentos
        print_query_results(
            "PATIENTS WITH THEIR INTERNAMENTOS",
            """SELECT 
                d.id as patient_id,
                d.nome as patient_name,
                d.numero_processo,
                d.sexo,
                d.data_nascimento,
                i.numero_internamento,
                i.data_entrada,
                i.ASCQ_total,
                i.lesao_inalatoria,
                DATE(d.created_at) as patient_created
            FROM doente d
            LEFT JOIN internamento i ON d.id = i.doente_id
            ORDER BY d.id, i.data_entrada""",
            conn
        )

        # Query 3: Internamentos with lookup data
        print_query_results(
            "INTERNAMENTOS WITH ACCIDENT TYPE AND BURN AGENT",
            """SELECT 
                i.numero_internamento,
                d.nome as patient_name,
                i.data_entrada,
                i.ASCQ_total,
                i.lesao_inalatoria,
                ta.acidente as accident_type,
                ta.tipo_acidente as accident_category,
                aq.agente_queimadura as burn_agent,
                aq.nota as agent_note
            FROM internamento i
            LEFT JOIN doente d ON i.doente_id = d.id
            LEFT JOIN tipoacidente ta ON i.tipo_acidente = ta.id
            LEFT JOIN agentequeimadura aq ON i.agente_queimadura = aq.id
            ORDER BY i.data_entrada DESC""",
            conn
        )

        # Query 4: Statistics by accident type
        print_query_results(
            "STATISTICS BY ACCIDENT TYPE",
            """SELECT 
                COALESCE(ta.acidente, 'Unknown/Null') as accident_type,
                COALESCE(ta.tipo_acidente, 'Unknown/Null') as accident_category,
                COUNT(i.id) as total_internamentos,
                ROUND(AVG(i.ASCQ_total), 2) as avg_ascq,
                MIN(i.ASCQ_total) as min_ascq,
                MAX(i.ASCQ_total) as max_ascq,
                SUM(CASE WHEN i.lesao_inalatoria = 'SIM' THEN 1 ELSE 0 END) as inhalation_injuries
            FROM internamento i
            LEFT JOIN tipoacidente ta ON i.tipo_acidente = ta.id
            GROUP BY ta.id, ta.acidente, ta.tipo_acidente
            ORDER BY total_internamentos DESC""",
            conn
        )

        # Query 5: Statistics by burn agent
        print_query_results(
            "STATISTICS BY BURN AGENT",
            """SELECT 
                COALESCE(aq.agente_queimadura, 'Unknown/Null') as burn_agent,
                COUNT(i.id) as total_internamentos,
                ROUND(AVG(i.ASCQ_total), 2) as avg_ascq,
                SUM(CASE WHEN i.lesao_inalatoria = 'SIM' THEN 1 ELSE 0 END) as inhalation_injuries,
                MIN(i.data_entrada) as earliest_admission,
                MAX(i.data_entrada) as latest_admission
            FROM internamento i
            LEFT JOIN agentequeimadura aq ON i.agente_queimadura = aq.id
            GROUP BY aq.id, aq.agente_queimadura
            ORDER BY total_internamentos DESC""",
            conn
        )

        # Query 6: Lookup table contents
        print_query_results(
            "LOOKUP TABLE: TIPO ACIDENTE",
            """SELECT id, acidente, tipo_acidente 
            FROM tipoacidente 
            ORDER BY id""",
            conn
        )

        print_query_results(
            "LOOKUP TABLE: AGENTE QUEIMADURA",
            """SELECT id, agente_queimadura, nota 
            FROM agentequeimadura 
            ORDER BY id""",
            conn
        )

        # Query 7: Foreign key integrity check
        print_query_results(
            "DATA INTEGRITY CHECK - FOREIGN KEY RELATIONSHIPS",
            """SELECT 
                'Valid TipoAcidente FKs' as check_type,
                COUNT(*) as count
            FROM internamento i
            INNER JOIN tipoacidente ta ON i.tipo_acidente = ta.id
            WHERE i.tipo_acidente IS NOT NULL
            UNION ALL
            SELECT 
                'Invalid TipoAcidente FKs',
                COUNT(*)
            FROM internamento i
            WHERE i.tipo_acidente IS NOT NULL 
            AND i.tipo_acidente NOT IN (SELECT id FROM tipoacidente)
            UNION ALL
            SELECT 
                'Valid AgenteQueimadura FKs',
                COUNT(*)
            FROM internamento i
            INNER JOIN agentequeimadura aq ON i.agente_queimadura = aq.id
            WHERE i.agente_queimadura IS NOT NULL
            UNION ALL
            SELECT 
                'Invalid AgenteQueimadura FKs',
                COUNT(*)
            FROM internamento i
            WHERE i.agente_queimadura IS NOT NULL 
            AND i.agente_queimadura NOT IN (SELECT id FROM agentequeimadura)""",
            conn
        )

        # Query 8: Patient summary with all related data
        print_query_results(
            "COMPREHENSIVE PATIENT SUMMARY",
            """SELECT 
                d.nome as patient_name,
                d.numero_processo,
                d.sexo,
                COUNT(i.id) as total_internamentos,
                MIN(i.data_entrada) as first_admission,
                MAX(i.data_entrada) as last_admission,
                ROUND(AVG(i.ASCQ_total), 2) as avg_ascq_score,
                SUM(CASE WHEN i.lesao_inalatoria = 'SIM' THEN 1 ELSE 0 END) as inhalation_cases
            FROM doente d
            LEFT JOIN internamento i ON d.id = i.doente_id
            GROUP BY d.id, d.nome, d.numero_processo, d.sexo
            ORDER BY total_internamentos DESC""",
            conn
        )

    finally:
        conn.close()
        print_separator("DATABASE RELATIONSHIP TESTING COMPLETE")

if __name__ == "__main__":
    main()
