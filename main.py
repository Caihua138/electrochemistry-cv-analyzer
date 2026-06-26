#!/usr/bin/env python3
"""Main entry point for CV Analyzer"""

import argparse
from pathlib import Path
from src.cv_analyzer import CVAnalyzer
import json


def main():
    parser = argparse.ArgumentParser(
        description='Electrochemistry CV Data Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single ORR file
  python main.py data/orr_sample.csv --reaction ORR --pH 14
  
  # Batch process with custom electrode area
  python main.py data/ --batch --electrode-area 0.0707 --reaction OER
  
  # HER analysis with different reference electrode
  python main.py data/her_sample.csv --reaction HER --ref-electrode Ag/AgCl --ref-condition "1M KCl"
        """
    )
    
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('--batch', action='store_true', help='Batch process directory')
    parser.add_argument('--reaction', default='ORR', choices=['ORR', 'OER', 'HER'],
                       help='Reaction type (default: ORR)')
    parser.add_argument('--ref-electrode', default='Hg/HgO',
                       help='Reference electrode (default: Hg/HgO)')
    parser.add_argument('--ref-condition', default='1M NaOH (pH=14)',
                       help='Reference electrode condition')
    parser.add_argument('--pH', type=float, default=14.0, help='Solution pH')
    parser.add_argument('--electrode-area', type=float, default=0.1256,
                       help='Electrode area in cm² (default: 0.1256)')
    parser.add_argument('--temperature', type=float, default=25.0,
                       help='Temperature in °C (default: 25)')
    parser.add_argument('--output-dir', default='results', help='Output directory')
    parser.add_argument('--no-plot', action='store_true', help='Disable plotting')
    parser.add_argument('--pattern', default='*.csv', help='File pattern for batch processing')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = CVAnalyzer(
        reaction_type=args.reaction,
        reference_electrode=args.ref_electrode,
        ref_condition=args.ref_condition,
        pH=args.pH,
        electrode_area=args.electrode_area,
        temperature=args.temperature
    )
    
    print(f"\n{'='*60}")
    print(f"CV Analyzer - {args.reaction} Analysis")
    print(f"{'='*60}")
    print(f"Reaction Type: {args.reaction}")
    print(f"Reference Electrode: {args.ref_electrode} ({args.ref_condition})")
    print(f"pH: {args.pH}")
    print(f"Electrode Area: {args.electrode_area} cm²")
    print(f"Temperature: {args.temperature}°C")
    print(f"Output Directory: {args.output_dir}")
    print(f"{'='*60}\n")
    
    # Analyze
    if args.batch:
        print(f"Batch processing directory: {args.input}")
        results_list = analyzer.batch_analyze(
            directory=args.input,
            pattern=args.pattern,
            normalize_by_area=True,
            plot=not args.no_plot,
            save_results=True,
            output_dir=args.output_dir
        )
        print(f"\n✓ Processed {len(results_list)} files successfully")
    else:
        print(f"Analyzing file: {args.input}")
        results = analyzer.analyze_file(
            filepath=args.input,
            normalize_by_area=True,
            plot=not args.no_plot,
            save_results=True,
            output_dir=args.output_dir
        )
        print(f"\n✓ Analysis completed successfully")
        print("\nKey Results:")
        for key, value in results['parameters'].items():
            if value is not None:
                if 'slope' in key.lower() and 'r_squared' not in key:
                    print(f"  {key}: {value:.2f} mV/dec")
                elif 'r_squared' in key:
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value:.4f} V")
    
    print(f"\n{'='*60}")
    print("Analysis complete!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
