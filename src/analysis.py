"""
BD_doentes Statistical Analysis Service

This module provides statistical analysis and visualization data
for the BD_doentes_clean.csv dataset.

Created: September 2025
Author: Data Analysis System
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
from collections import Counter


class BDDoentesAnalyzer:
    """Statistical analyzer for BD_doentes clean dataset."""
    
    def __init__(self, csv_path: str = "/home/gusmmm/Desktop/mydb/files/csv/BD_doentes_clean.csv"):
        """Initialize analyzer with CSV file path."""
        self.csv_path = Path(csv_path)
        self.df: Optional[pd.DataFrame] = None
        self._load_data()
    
    def _load_data(self) -> None:
        """Load and prepare the dataset."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        try:
            self.df = pd.read_csv(self.csv_path)
            self._prepare_dates()
        except Exception as e:
            raise RuntimeError(f"Error loading CSV: {e}")
    
    def _prepare_dates(self) -> None:
        """Parse and prepare date columns."""
        if self.df is None:
            return
        
        date_columns = ['data_ent', 'data_alta', 'data_nasc', 'data_queim']
        
        for col in date_columns:
            if col in self.df.columns:
                self.df[f'{col}_parsed'] = pd.to_datetime(self.df[col], format='%d-%m-%Y', errors='coerce')
    
    def get_overview_statistics(self) -> Dict[str, Any]:
        """Get comprehensive dataset overview statistics."""
        if self.df is None:
            return {}
        
        total_records = len(self.df)
        
        # Basic counts
        overview = {
            "total_records": total_records,
            "total_patients": self.df['ID'].nunique(),
            "year_range": {
                "min_year": int(self.df['year'].min()),
                "max_year": int(self.df['year'].max()),
                "years_span": int(self.df['year'].max() - self.df['year'].min() + 1)
            },
            "data_completeness": {
                "complete_records": int(self.df.dropna().shape[0]),
                "completeness_rate": round(self.df.dropna().shape[0] / total_records * 100, 1)
            }
        }
        
        # Missing data analysis
        missing_data = {}
        for col in self.df.columns:
            missing_count = self.df[col].isnull().sum()
            if missing_count > 0:
                missing_data[col] = {
                    "missing_count": int(missing_count),
                    "missing_percentage": round(missing_count / total_records * 100, 1)
                }
        
        overview["missing_data_summary"] = missing_data
        
        return overview
    
    def get_demographic_analysis(self) -> Dict[str, Any]:
        """Analyze patient demographics."""
        if self.df is None:
            return {}
        
        demographics = {}
        
        # Gender distribution
        gender_counts = self.df['sexo'].value_counts().to_dict()
        demographics["gender_distribution"] = {
            "counts": gender_counts,
            "percentages": {k: round(v / len(self.df) * 100, 1) for k, v in gender_counts.items()}
        }
        
        # Age analysis (for records with age data)
        age_data = self.df[self.df['idade'].notna()]
        if not age_data.empty:
            demographics["age_statistics"] = {
                "count": int(len(age_data)),
                "mean": round(float(age_data['idade'].mean()), 1),
                "median": float(age_data['idade'].median()),
                "std": round(float(age_data['idade'].std()), 1),
                "min": int(age_data['idade'].min()),
                "max": int(age_data['idade'].max()),
                "quartiles": {
                    "q1": float(age_data['idade'].quantile(0.25)),
                    "q3": float(age_data['idade'].quantile(0.75))
                }
            }
            
            # Age distribution by ranges
            age_ranges = pd.cut(age_data['idade'], bins=[0, 18, 30, 50, 70, 100], 
                              labels=['0-17', '18-29', '30-49', '50-69', '70+'])
            age_range_counts = age_ranges.value_counts().to_dict()
            demographics["age_distribution"] = {
                str(k): int(v) for k, v in age_range_counts.items()
            }
        
        return demographics
    
    def get_temporal_analysis(self) -> Dict[str, Any]:
        """Analyze temporal patterns in admissions."""
        if self.df is None or 'data_ent_parsed' not in self.df.columns:
            return {}
        
        temporal = {}
        
        # Filter valid admission dates
        valid_admissions = self.df[self.df['data_ent_parsed'].notna()].copy()
        
        if valid_admissions.empty:
            return temporal
        
        # Annual admission trends
        valid_admissions['admission_year'] = valid_admissions['data_ent_parsed'].dt.year
        yearly_counts = valid_admissions['admission_year'].value_counts().sort_index()
        temporal["yearly_admissions"] = yearly_counts.to_dict()
        
        # Monthly patterns
        valid_admissions['admission_month'] = valid_admissions['data_ent_parsed'].dt.month
        monthly_counts = valid_admissions['admission_month'].value_counts().sort_index()
        temporal["monthly_patterns"] = monthly_counts.to_dict()
        
        # Seasonal analysis
        seasons = {
            "Winter": [12, 1, 2],
            "Spring": [3, 4, 5], 
            "Summer": [6, 7, 8],
            "Autumn": [9, 10, 11]
        }
        
        seasonal_counts = {}
        for season, months in seasons.items():
            count = valid_admissions[valid_admissions['admission_month'].isin(months)].shape[0]
            seasonal_counts[season] = count
        
        temporal["seasonal_distribution"] = seasonal_counts
        
        return temporal
    
    def get_burn_severity_analysis(self) -> Dict[str, Any]:
        """Analyze burn severity metrics."""
        if self.df is None:
            return {}
        
        severity = {}
        
        # ASCQ analysis
        ascq_data = self.df[self.df['ASCQ'].notna()]
        if not ascq_data.empty:
            severity["ascq_statistics"] = {
                "count": int(len(ascq_data)),
                "mean": round(float(ascq_data['ASCQ'].mean()), 1),
                "median": float(ascq_data['ASCQ'].median()),
                "std": round(float(ascq_data['ASCQ'].std()), 1),
                "min": float(ascq_data['ASCQ'].min()),
                "max": float(ascq_data['ASCQ'].max())
            }
            
            # ASCQ severity categories
            ascq_categories = pd.cut(ascq_data['ASCQ'], 
                                   bins=[0, 10, 20, 40, 100], 
                                   labels=['Minor (≤10%)', 'Moderate (11-20%)', 
                                          'Major (21-40%)', 'Severe (>40%)'])
            ascq_category_counts = ascq_categories.value_counts().to_dict()
            severity["ascq_distribution"] = {
                str(k): int(v) for k, v in ascq_category_counts.items()
            }
        
        # BAUX score analysis
        baux_data = self.df[self.df['BAUX'].notna()]
        if not baux_data.empty:
            severity["baux_statistics"] = {
                "count": int(len(baux_data)),
                "mean": round(float(baux_data['BAUX'].mean()), 1),
                "median": float(baux_data['BAUX'].median()),
                "std": round(float(baux_data['BAUX'].std()), 1),
                "min": float(baux_data['BAUX'].min()),
                "max": float(baux_data['BAUX'].max())
            }
        
        # Inhalation injury analysis
        if 'lesao_inal' in self.df.columns:
            lesao_inal_counts = self.df['lesao_inal'].value_counts().to_dict()
            severity["inhalation_injury"] = {
                "counts": lesao_inal_counts,
                "percentages": {k: round(v / len(self.df) * 100, 1) 
                              for k, v in lesao_inal_counts.items()}
            }
        
        # VMI analysis  
        if 'env_VMI' in self.df.columns:
            vmi_counts = self.df['env_VMI'].value_counts().to_dict()
            severity["mechanical_ventilation"] = {
                "counts": vmi_counts,
                "percentages": {k: round(v / len(self.df) * 100, 1) 
                              for k, v in vmi_counts.items()}
            }
        
        return severity
    
    def get_etiology_analysis(self) -> Dict[str, Any]:
        """Analyze burn etiology patterns."""
        if self.df is None or 'etiologia' not in self.df.columns:
            return {}
        
        etiology = {}
        
        # Etiology distribution
        etiology_data = self.df[self.df['etiologia'].notna()]
        if not etiology_data.empty:
            etiology_counts = etiology_data['etiologia'].value_counts()
            
            # Top 10 causes
            top_etiologies = etiology_counts.head(10).to_dict()
            etiology["top_causes"] = top_etiologies
            
            # Percentage distribution for top causes
            total_with_etiology = len(etiology_data)
            etiology["top_causes_percentages"] = {
                k: round(v / total_with_etiology * 100, 1) 
                for k, v in top_etiologies.items()
            }
            
            # Categorize etiologies
            fire_related = ['fogo', 'chama', 'Fogo', 'fogo florestal', 'Flash burn', 'flash burn']
            liquid_related = ['liq quente', 'liquido quente', 'líquido quente', 'Líquido quente', 
                            'agua quente', 'agua fervente', 'vapor quente']
            electrical = ['eléctrica', 'eletrica', 'electrica', 'eletrico']
            chemical = ['química', 'quimica']
            
            categories = {
                "Fire/Flame": fire_related,
                "Hot Liquids": liquid_related,
                "Electrical": electrical,
                "Chemical": chemical
            }
            
            category_counts = {}
            for category, terms in categories.items():
                count = etiology_data[etiology_data['etiologia'].isin(terms)].shape[0]
                category_counts[category] = count
            
            # Other category
            categorized_count = sum(category_counts.values())
            category_counts["Other"] = total_with_etiology - categorized_count
            
            etiology["categorized_causes"] = category_counts
        
        return etiology
    
    def get_outcome_analysis(self) -> Dict[str, Any]:
        """Analyze patient outcomes and length of stay."""
        if self.df is None:
            return {}
        
        outcomes = {}
        
        # Discharge destination analysis
        if 'destino' in self.df.columns:
            destino_data = self.df[self.df['destino'].notna()]
            if not destino_data.empty:
                destino_counts = destino_data['destino'].value_counts()
                
                # Group similar destinations
                home_terms = ['domicilio', 'Domicílio', 'domicílio']
                death_terms = ['obito', 'óbito', 'Óbito']
                ward_terms = ['enf', 'Enf']
                
                grouped_outcomes = {
                    "Home": destino_data[destino_data['destino'].isin(home_terms)].shape[0],
                    "Death": destino_data[destino_data['destino'].isin(death_terms)].shape[0],  
                    "Ward": destino_data[destino_data['destino'].isin(ward_terms)].shape[0],
                    "Other Hospital": destino_data[destino_data['destino'].str.contains('H -|outro -', na=False)].shape[0]
                }
                
                total_outcomes = sum(grouped_outcomes.values())
                other_count = len(destino_data) - total_outcomes
                if other_count > 0:
                    grouped_outcomes["Other"] = other_count
                
                outcomes["discharge_destinations"] = grouped_outcomes
                
                # Calculate mortality rate
                death_count = grouped_outcomes.get("Death", 0)
                total_with_outcome = len(destino_data)
                mortality_rate = round(death_count / total_with_outcome * 100, 1) if total_with_outcome > 0 else 0
                outcomes["mortality_rate"] = mortality_rate
        
        # Time from burn to admission analysis
        if 'dias_queim' in self.df.columns:
            time_data = self.df[self.df['dias_queim'].notna()]
            if not time_data.empty:
                outcomes["time_to_admission"] = {
                    "count": int(len(time_data)),
                    "mean_days": round(float(time_data['dias_queim'].mean()), 1),
                    "median_days": float(time_data['dias_queim'].median()),
                    "std_days": round(float(time_data['dias_queim'].std()), 1),
                    "same_day_admissions": int((time_data['dias_queim'] == 0).sum()),
                    "delayed_admissions": int((time_data['dias_queim'] > 1).sum())
                }
        
        return outcomes
    
    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """Get all analysis results in one comprehensive report."""
        if self.df is None:
            return {"error": "No data loaded"}
        
        return {
            "overview": self.get_overview_statistics(),
            "demographics": self.get_demographic_analysis(),
            "temporal_patterns": self.get_temporal_analysis(),
            "burn_severity": self.get_burn_severity_analysis(),
            "etiology": self.get_etiology_analysis(),
            "outcomes": self.get_outcome_analysis(),
            "analysis_timestamp": datetime.now().isoformat(),
            "dataset_info": {
                "file_path": str(self.csv_path),
                "total_columns": len(self.df.columns),
                "column_names": list(self.df.columns)
            }
        }
    
    def get_chart_data(self, chart_type: str) -> Dict[str, Any]:
        """Generate specific chart data for frontend visualization."""
        if self.df is None:
            return {}
        
        chart_generators = {
            "age_distribution": self._get_age_chart_data,
            "gender_distribution": self._get_gender_chart_data,
            "yearly_admissions": self._get_yearly_admissions_chart_data,
            "monthly_patterns": self._get_monthly_patterns_chart_data,
            "ascq_distribution": self._get_ascq_chart_data,
            "etiology_top10": self._get_etiology_chart_data,
            "seasonal_admissions": self._get_seasonal_chart_data,
            "outcomes_distribution": self._get_outcomes_chart_data
        }
        
        generator = chart_generators.get(chart_type)
        if generator:
            return generator()
        else:
            return {"error": f"Unknown chart type: {chart_type}"}
    
    def _get_age_chart_data(self) -> Dict[str, Any]:
        """Generate age distribution chart data."""
        age_data = self.df[self.df['idade'].notna()]
        if age_data.empty:
            return {}
        
        age_ranges = pd.cut(age_data['idade'], bins=[0, 18, 30, 50, 70, 100], 
                          labels=['0-17', '18-29', '30-49', '50-69', '70+'])
        counts = age_ranges.value_counts().sort_index()
        
        return {
            "type": "bar",
            "labels": [str(label) for label in counts.index],
            "data": counts.values.tolist(),
            "title": "Age Distribution"
        }
    
    def _get_gender_chart_data(self) -> Dict[str, Any]:
        """Generate gender distribution chart data."""
        gender_counts = self.df['sexo'].value_counts()
        
        return {
            "type": "pie",
            "labels": list(gender_counts.index),
            "data": gender_counts.values.tolist(),
            "title": "Gender Distribution"
        }
    
    def _get_yearly_admissions_chart_data(self) -> Dict[str, Any]:
        """Generate yearly admissions trend chart data."""
        if 'data_ent_parsed' not in self.df.columns:
            return {}
        
        valid_admissions = self.df[self.df['data_ent_parsed'].notna()].copy()
        if valid_admissions.empty:
            return {}
        
        valid_admissions['admission_year'] = valid_admissions['data_ent_parsed'].dt.year
        yearly_counts = valid_admissions['admission_year'].value_counts().sort_index()
        
        return {
            "type": "line",
            "labels": [str(year) for year in yearly_counts.index],
            "data": yearly_counts.values.tolist(),
            "title": "Admissions by Year"
        }
    
    def _get_monthly_patterns_chart_data(self) -> Dict[str, Any]:
        """Generate monthly admission patterns chart data.""" 
        if 'data_ent_parsed' not in self.df.columns:
            return {}
        
        valid_admissions = self.df[self.df['data_ent_parsed'].notna()].copy()
        if valid_admissions.empty:
            return {}
        
        valid_admissions['admission_month'] = valid_admissions['data_ent_parsed'].dt.month
        monthly_counts = valid_admissions['admission_month'].value_counts().sort_index()
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        return {
            "type": "bar",
            "labels": [month_names[i-1] for i in monthly_counts.index],
            "data": monthly_counts.values.tolist(),
            "title": "Admissions by Month"
        }
    
    def _get_ascq_chart_data(self) -> Dict[str, Any]:
        """Generate ASCQ distribution chart data."""
        ascq_data = self.df[self.df['ASCQ'].notna()]
        if ascq_data.empty:
            return {}
        
        ascq_categories = pd.cut(ascq_data['ASCQ'], 
                               bins=[0, 10, 20, 40, 100], 
                               labels=['≤10%', '11-20%', '21-40%', '>40%'])
        counts = ascq_categories.value_counts().sort_index()
        
        return {
            "type": "bar",
            "labels": [str(label) for label in counts.index],
            "data": counts.values.tolist(),
            "title": "Burn Severity (ASCQ) Distribution"
        }
    
    def _get_etiology_chart_data(self) -> Dict[str, Any]:
        """Generate top 10 etiology chart data."""
        etiology_data = self.df[self.df['etiologia'].notna()]
        if etiology_data.empty:
            return {}
        
        top_etiologies = etiology_data['etiologia'].value_counts().head(10)
        
        return {
            "type": "horizontalBar",
            "labels": list(top_etiologies.index),
            "data": top_etiologies.values.tolist(),
            "title": "Top 10 Burn Causes"
        }
    
    def _get_seasonal_chart_data(self) -> Dict[str, Any]:
        """Generate seasonal admissions chart data."""
        if 'data_ent_parsed' not in self.df.columns:
            return {}
        
        valid_admissions = self.df[self.df['data_ent_parsed'].notna()].copy()
        if valid_admissions.empty:
            return {}
        
        valid_admissions['admission_month'] = valid_admissions['data_ent_parsed'].dt.month
        
        seasons = {
            "Winter": [12, 1, 2],
            "Spring": [3, 4, 5], 
            "Summer": [6, 7, 8],
            "Autumn": [9, 10, 11]
        }
        
        seasonal_counts = {}
        for season, months in seasons.items():
            count = valid_admissions[valid_admissions['admission_month'].isin(months)].shape[0]
            seasonal_counts[season] = count
        
        return {
            "type": "pie",
            "labels": list(seasonal_counts.keys()),
            "data": list(seasonal_counts.values()),
            "title": "Seasonal Admission Patterns"
        }
    
    def _get_outcomes_chart_data(self) -> Dict[str, Any]:
        """Generate outcomes distribution chart data."""
        if 'destino' not in self.df.columns:
            return {}
        
        destino_data = self.df[self.df['destino'].notna()]
        if destino_data.empty:
            return {}
        
        # Group similar destinations
        home_terms = ['domicilio', 'Domicílio', 'domicílio']
        death_terms = ['obito', 'óbito', 'Óbito']
        ward_terms = ['enf', 'Enf']
        
        grouped_outcomes = {
            "Home": destino_data[destino_data['destino'].isin(home_terms)].shape[0],
            "Death": destino_data[destino_data['destino'].isin(death_terms)].shape[0],  
            "Ward": destino_data[destino_data['destino'].isin(ward_terms)].shape[0],
            "Other Hospital": destino_data[destino_data['destino'].str.contains('H -|outro -', na=False)].shape[0]
        }
        
        # Filter out zero values
        filtered_outcomes = {k: v for k, v in grouped_outcomes.items() if v > 0}
        
        return {
            "type": "doughnut", 
            "labels": list(filtered_outcomes.keys()),
            "data": list(filtered_outcomes.values()),
            "title": "Patient Outcomes"
        }


# Global analyzer instance
_analyzer = None

def get_analyzer() -> BDDoentesAnalyzer:
    """Get or create the global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = BDDoentesAnalyzer()
    return _analyzer