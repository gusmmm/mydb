# BD_doentes Analysis System

## Overview

This system provides comprehensive statistical analysis and visualization for the BD_doentes burn unit dataset. It consists of a **Python/FastAPI backend** for data processing and a **Vue.js frontend** for visualization.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BD_doentes Analysis System                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Frontend (Vue.js + PrimeVue + Chart.js)                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ • AnalysisView.vue - Main analysis dashboard            │    │
│  │ • Interactive charts and visualizations                 │    │
│  │ • Real-time data quality monitoring                     │    │
│  │ • Export functionality                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           ↕ HTTP API                           │
│  Backend (Python + FastAPI + pandas + numpy)                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ • BDDoentesAnalyzer class - Core analysis engine        │    │
│  │ • Statistical computations and aggregations             │    │
│  │ • Chart data generation                                 │    │
│  │ • RESTful API endpoints                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           ↕ File I/O                          │
│  Data Layer                                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ • BD_doentes_clean.csv - Clean dataset                 │    │
│  │ • Automated date parsing and validation                 │    │
│  │ • Quality control integration                           │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Analysis Features

### 1. **Overview Statistics**
- Total records and unique patients
- Year range and data span
- Overall data completeness rate
- Missing data summary by column

### 2. **Demographic Analysis**
- Gender distribution (pie charts)
- Age statistics and distributions
- Age range breakdowns by categories

### 3. **Temporal Patterns**
- Yearly admission trends (line charts)
- Monthly admission patterns (bar charts) 
- Seasonal distribution analysis

### 4. **Burn Severity Analysis**
- ASCQ (burn surface area) distributions
- BAUX score statistics
- Inhalation injury rates
- Mechanical ventilation requirements

### 5. **Etiology Analysis**
- Top burn causes with rankings
- Categorized cause analysis (Fire, Liquids, Electrical, Chemical)
- Cause-specific statistics

### 6. **Outcomes Analysis**
- Patient discharge destinations
- Mortality rate calculations
- Time from burn to admission analysis
- Length of stay patterns

### 7. **Data Quality Monitoring**
- Column-wise completeness scores
- Missing data visualizations
- Quality recommendations
- Data integrity alerts

## 🛠️ Technical Implementation

### Backend Components

#### `src/analysis.py` - Core Analysis Engine
```python
class BDDoentesAnalyzer:
    def get_overview_statistics()      # Dataset overview
    def get_demographic_analysis()     # Patient demographics  
    def get_temporal_analysis()        # Time-based patterns
    def get_burn_severity_analysis()   # Burn severity metrics
    def get_etiology_analysis()        # Cause analysis
    def get_outcome_analysis()         # Patient outcomes
    def get_chart_data(chart_type)     # Visualization data
```

#### API Endpoints (`src/api.py`)
```
GET /analysis/overview        # Overview statistics
GET /analysis/demographics    # Demographic analysis
GET /analysis/temporal        # Temporal patterns
GET /analysis/burn-severity   # Burn severity analysis
GET /analysis/etiology        # Etiology analysis
GET /analysis/outcomes        # Outcomes analysis
GET /analysis/comprehensive   # All analysis in one call
GET /analysis/chart/{type}    # Specific chart data
```

### Frontend Components

#### Main Analysis View
- `views/AnalysisView.vue` - Main dashboard container
- `components/analysis/AnalysisOverviewCards.vue` - Key metrics cards

#### Specialized Analysis Components
- `DemographicsAnalysis.vue` - Demographics with charts
- `TemporalAnalysis.vue` - Time-based visualizations
- `BurnSeverityAnalysis.vue` - Severity metrics and charts
- `EtiologyAnalysis.vue` - Cause analysis and rankings
- `OutcomesAnalysis.vue` - Patient outcome analysis
- `DataQualityAnalysis.vue` - Data quality monitoring

#### Chart Types Supported
- **Bar Charts**: Age ranges, monthly patterns, ASCQ categories
- **Line Charts**: Yearly trends, time series
- **Pie Charts**: Gender distribution, outcomes, causes
- **Doughnut Charts**: Detailed breakdowns with percentages

## 🚀 Getting Started

### Prerequisites
- Python 3.11+ with uv package manager
- Node.js 20+ with npm
- Running BD_doentes_clean.csv file

### Backend Setup
```bash
# Install dependencies
uv sync

# Start the analysis-enabled API server
uv run uvicorn src.api:app --reload --port 8001
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (including Chart.js)
npm install

# Start development server
npm run dev
```

### Access the Analysis Dashboard
1. Navigate to `http://localhost:5173` (or your Vite dev server)
2. Click on "Data Analysis" in the navigation menu
3. The system will automatically load and analyze the BD_doentes_clean.csv data

## 📈 Usage Examples

### Accessing Analysis Data Programmatically
```python
from src.analysis import get_analyzer

# Get analyzer instance
analyzer = get_analyzer()

# Get comprehensive analysis
analysis = analyzer.get_comprehensive_analysis()

# Get specific chart data
gender_chart = analyzer.get_chart_data('gender_distribution')
age_chart = analyzer.get_chart_data('age_distribution')
```

### Frontend API Service Usage
```typescript
import { analysisService } from '@/services/api'

// Get overview statistics
const overview = await analysisService.getOverview()

// Get chart data for visualization
const chartData = await analysisService.getChartData('yearly_admissions')
```

## 🔧 Configuration

### Backend Configuration
The analyzer automatically loads data from:
```
/home/gusmmm/Desktop/mydb/files/csv/BD_doentes_clean.csv
```

### Chart Configuration
Charts are configured using Chart.js with responsive design:
- Consistent color schemes across analysis sections
- Interactive hover effects and tooltips
- Responsive design for mobile devices
- Export-ready visualizations

## 📊 Data Quality Integration

The analysis system integrates with the existing quality control pipeline:

1. **Quality Reports**: Uses reports from `/files/reports/` directory
2. **Missing Data Detection**: Automatic identification of incomplete fields
3. **Data Validation**: Integration with date parsing and validation logic
4. **Quality Scoring**: Automated data quality scoring and recommendations

## 🔍 Monitoring and Diagnostics

### Health Checks
- Backend: `GET /analysis/overview` should return dataset statistics
- Frontend: Navigation to `/analysis` should load without errors
- Charts: All visualizations should render with data

### Error Handling
- **Missing Data**: Graceful degradation when data is incomplete
- **API Errors**: User-friendly error messages with retry options
- **Chart Failures**: Fallback to table views when charts fail to load

## 📝 Development Guidelines

### Adding New Analysis Features

1. **Backend**: Add methods to `BDDoentesAnalyzer` class
2. **API**: Create corresponding endpoints in `src/api.py`
3. **Frontend**: Add TypeScript interfaces in `services/api.ts`
4. **Components**: Create Vue components in `components/analysis/`
5. **Charts**: Use Chart.js for consistent visualization

### Code Structure Best Practices

- **Modularity**: Keep analysis functions focused and reusable
- **Type Safety**: Use TypeScript interfaces for all API communications
- **Error Handling**: Implement comprehensive error handling at all levels
- **Performance**: Use efficient pandas operations for large datasets
- **Maintainability**: Document all analysis methods and chart configurations

## 🎯 Future Enhancements

- **Real-time Updates**: WebSocket connections for live data updates
- **Advanced Filtering**: Dynamic filtering and drill-down capabilities
- **Export Options**: PDF reports, Excel exports, image downloads
- **Comparative Analysis**: Year-over-year comparisons and trend analysis
- **Predictive Analytics**: Machine learning models for outcome prediction
- **Dashboard Customization**: User-configurable dashboard layouts

## 🆘 Troubleshooting

### Common Issues

**Backend Analysis Errors**:
```bash
# Check if CSV file exists and is readable
ls -la /home/gusmmm/Desktop/mydb/files/csv/BD_doentes_clean.csv

# Test analyzer directly
uv run python -c "from src.analysis import get_analyzer; print(get_analyzer().get_overview_statistics())"
```

**Frontend Chart Issues**:
- Ensure Chart.js is installed: `npm list chart.js`
- Check browser console for JavaScript errors
- Verify API endpoints are accessible from frontend

**Performance Issues**:
- Dataset analysis is cached after first load
- Charts render asynchronously to prevent blocking
- Large datasets (>1000 records) may require optimization

This analysis system provides a comprehensive, maintainable, and scalable solution for BD_doentes dataset visualization and statistical analysis.