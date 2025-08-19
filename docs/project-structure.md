# Drobo Firmware Analysis Project Structure

This document describes the organized structure of the Drobo firmware analysis project.

## Directory Structure

```
drobo-fw/
├── README.md                     # Main project documentation
├── docs/                         # Documentation and data
│   ├── README.md                 # Documentation navigation guide
│   ├── project-structure.md      # This file
│   ├── analysis/                 # Analysis results and findings
│   │   ├── analysis-summary.md   # Executive summary
│   │   ├── raid-controller-analysis.md # Technical deep dive
│   │   └── memory-map-offsets.md # Memory locations
│   ├── reference/                # Reference documentation
│   │   ├── protection-modes-reference.md    # RAID modes guide
│   │   ├── management-modules-reference.md  # System architecture
│   │   └── offset-usage-guide.md           # Programming guide
│   └── data/                     # Structured data files
│       ├── memory-offsets.json   # JSON format offset data
│       └── memory-offsets.csv    # CSV format for databases
├── tools/                        # Utility tools and modules
│   ├── README.md                 # Tools documentation
│   └── offsets.py               # Python offset constants module
├── scripts/                      # Analysis and modification scripts
│   ├── extraction/               # Firmware extraction tools
│   │   ├── extract_all_components.py  # Main component extractor
│   │   └── extract_tdih.py            # TDIH header parser
│   ├── analysis/                 # Analysis tools
│   │   └── find_patch_targets.py      # Capacity limit finder
│   └── patching/                 # Patching tools
│       └── patch_2tb_limit.py         # 2TB limit patcher
├── firmware/                     # Original firmware files
│   ├── *.zip                     # Firmware archives
│   └── *.tdf                     # Extracted TDF firmware files
├── extracted/                    # Extracted firmware components
│   ├── *.elf                     # ELF binaries
│   └── *.bin                     # Raw binary files
└── backups/                      # Backup files
    └── *.backup*                 # Original file backups
```

## File Descriptions

### Scripts

#### Extraction Scripts (`scripts/extraction/`)
- **extract_all_components.py**: Extracts main VxWorks components (bootloader, main app, kernel) from TDF firmware
- **extract_tdih.py**: Parses TDIH headers and extracts VxWorks images

#### Analysis Scripts (`scripts/analysis/`)
- **find_patch_targets.py**: Searches for capacity-related strings and 2TB constants in firmware

#### Patching Scripts (`scripts/patching/`)
- **patch_2tb_limit.py**: Patches 2TB capacity limits to larger values (default 32TB)

### Directories

- **docs/**: Complete documentation with analysis, reference guides, and data
  - **analysis/**: Research findings and technical analysis
  - **reference/**: User and developer reference guides  
  - **data/**: Machine-readable offset and configuration data
- **tools/**: Utility modules and helper scripts
- **scripts/**: Organized analysis and modification scripts
- **firmware/**: Original firmware files (TDF format and ZIP archives)
- **extracted/**: Extracted binary components ready for analysis
- **backups/**: Automatic backups created before patching

## Usage Workflow

1. Place firmware TDF files in `firmware/` directory
2. Run extraction scripts from `scripts/extraction/` to populate `extracted/`
3. Use analysis scripts from `scripts/analysis/` to identify patch targets
4. Apply patches using scripts from `scripts/patching/`
5. Backups are automatically created in `backups/` before modification

## Security Note

This project is for defensive security research and firmware repair purposes only. All tools are designed for analysis and legitimate modification of owned hardware.