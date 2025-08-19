# Documentation Directory

This directory contains comprehensive documentation for the Drobo 5D3 firmware analysis project.

## Directory Structure

```
docs/
├── README.md                      # This file
├── project-structure.md           # Overall project organization
├── analysis/                      # Analysis results and findings
│   ├── analysis-summary.md        # Executive summary of all findings
│   ├── raid-controller-analysis.md # Complete technical architecture analysis
│   └── memory-map-offsets.md      # Memory locations and key offsets
├── reference/                     # Reference documentation
│   ├── protection-modes-reference.md    # RAID protection modes guide
│   ├── management-modules-reference.md  # Module architecture reference
│   └── offset-usage-guide.md           # Programming integration guide
└── data/                          # Structured data files
    ├── memory-offsets.json        # JSON format offset data
    └── memory-offsets.csv         # CSV format for databases
```

## Quick Navigation

### 📊 **Analysis Results**
- **[Analysis Summary](analysis/analysis-summary.md)** - Start here for overview
- **[RAID Controller Analysis](analysis/raid-controller-analysis.md)** - Technical deep dive
- **[Memory Map](analysis/memory-map-offsets.md)** - Memory locations and offsets

### 📖 **Reference Guides**
- **[Protection Modes](reference/protection-modes-reference.md)** - RAID configuration guide
- **[Management Modules](reference/management-modules-reference.md)** - System architecture
- **[Programming Guide](reference/offset-usage-guide.md)** - Integration examples

### 💾 **Data Files**
- **[JSON Offsets](data/memory-offsets.json)** - Machine-readable offset data
- **[CSV Offsets](data/memory-offsets.csv)** - Database-ready format

## Usage Recommendations

### For System Administrators
1. Start with [Analysis Summary](analysis/analysis-summary.md)
2. Review [Protection Modes](reference/protection-modes-reference.md) for configuration
3. Use [Management Modules](reference/management-modules-reference.md) for troubleshooting

### For Developers/Researchers
1. Read [RAID Controller Analysis](analysis/raid-controller-analysis.md) for architecture
2. Use [Programming Guide](reference/offset-usage-guide.md) for integration
3. Import [JSON/CSV data](data/) for automated tools

### For Security Researchers
1. Review [Memory Map](analysis/memory-map-offsets.md) for critical locations
2. Use structured [data files](data/) for vulnerability analysis
3. Reference [Protection Modes](reference/protection-modes-reference.md) for security implications

All documentation is interconnected and cross-referenced for easy navigation.