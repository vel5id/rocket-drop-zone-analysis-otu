#!/usr/bin/env python3
"""
GeoJSON optimization script.
Reduces file size by:
1. Rounding coordinates to 6 decimal places (~10cm precision)
2. Removing unnecessary properties
3. Compressing with gzip
4. Using shorter property names
"""
import os
import json
import gzip
import argparse
from pathlib import Path
import numpy as np

def round_coordinates(coords, decimals=6):
    """Round coordinates to specified decimal places."""
    if isinstance(coords, (list, tuple)):
        return [round_coordinates(c, decimals) for c in coords]
    elif isinstance(coords, (int, float)):
        return round(coords, decimals)
    else:
        return coords

def optimize_feature(feature, precision=6):
    """Optimize a single GeoJSON feature."""
    # Round geometry coordinates
    if 'geometry' in feature and 'coordinates' in feature['geometry']:
        feature['geometry']['coordinates'] = round_coordinates(
            feature['geometry']['coordinates'], 
            precision
        )
    
    # Simplify properties
    if 'properties' in feature:
        props = feature['properties']
        
        # Remove empty or None properties
        props = {k: v for k, v in props.items() if v is not None}
        
        # Round numeric properties
        for key, value in props.items():
            if isinstance(value, (int, float)):
                # Round to reasonable precision based on value magnitude
                if abs(value) < 0.001:
                    props[key] = round(value, 6)
                elif abs(value) < 1:
                    props[key] = round(value, 4)
                elif abs(value) < 100:
                    props[key] = round(value, 2)
                else:
                    props[key] = round(value, 1)
        
        # Use shorter property names for common fields
        rename_map = {
            'q_ndvi': 'ndvi',
            'q_si': 'si',
            'q_bi': 'bi',
            'q_relief': 'rel',
            'q_otu': 'otu',
            'q_fire': 'fire',
            'center_lat': 'clat',
            'center_lon': 'clon',
            'is_fragment': 'frag',
            'fragment_id': 'fid',
            'velocity': 'vel'
        }
        
        new_props = {}
        for key, value in props.items():
            new_key = rename_map.get(key, key)
            new_props[new_key] = value
        
        feature['properties'] = new_props
    
    return feature

def optimize_geojson(input_path, output_path=None, precision=6, compress=True):
    """
    Optimize a GeoJSON file.
    
    Args:
        input_path: Path to input GeoJSON file
        output_path: Path for optimized output (optional)
        precision: Coordinate decimal precision
        compress: Whether to gzip compress the output
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    print(f"Optimizing: {input_path}")
    print(f"  Size: {input_path.stat().st_size / (1024*1024):.2f} MB")
    
    # Read input
    with open(input_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    
    original_features = len(geojson.get('features', []))
    print(f"  Features: {original_features}")
    
    # Optimize features
    if 'features' in geojson:
        optimized_features = []
        for i, feature in enumerate(geojson['features']):
            if i % 1000 == 0 and i > 0:
                print(f"    Processed {i}/{original_features} features...")
            optimized_features.append(optimize_feature(feature, precision))
        
        geojson['features'] = optimized_features
    
    # Determine output path
    if output_path is None:
        if compress:
            output_path = input_path.with_suffix('.geojson.gz')
        else:
            output_path = input_path.with_name(f"{input_path.stem}_optimized{input_path.suffix}")
    
    output_path = Path(output_path)
    
    # Save optimized file
    if compress:
        print(f"  Compressing with gzip...")
        with gzip.open(output_path, 'wt', encoding='utf-8') as f:
            json.dump(geojson, f, separators=(',', ':'))  # Minify JSON
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, separators=(',', ':'))  # Minify JSON
    
    # Report savings
    original_size = input_path.stat().st_size
    optimized_size = output_path.stat().st_size
    
    print(f"  Optimized size: {optimized_size / (1024*1024):.2f} MB")
    print(f"  Reduction: {100 * (1 - optimized_size / original_size):.1f}%")
    print(f"  Saved to: {output_path}")
    
    return str(output_path), original_size, optimized_size

def batch_optimize_directory(input_dir, output_dir=None, pattern="*.geojson", **kwargs):
    """Optimize all GeoJSON files in a directory."""
    input_dir = Path(input_dir)
    
    if output_dir is None:
        output_dir = input_dir / "optimized"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for input_file in input_dir.glob(pattern):
        if input_file.suffix == '.gz':
            continue  # Skip already compressed files
        
        output_file = output_dir / f"{input_file.stem}_optimized{input_file.suffix}"
        if kwargs.get('compress', True):
            output_file = output_file.with_suffix('.geojson.gz')
        
        try:
            output_path, original_size, optimized_size = optimize_geojson(
                input_file, output_file, **kwargs
            )
            results.append({
                'input': str(input_file),
                'output': output_path,
                'original_size': original_size,
                'optimized_size': optimized_size,
                'reduction': 100 * (1 - optimized_size / original_size)
            })
        except Exception as e:
            print(f"Error processing {input_file}: {e}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Optimize GeoJSON files for size")
    parser.add_argument("input", help="Input GeoJSON file or directory")
    parser.add_argument("-o", "--output", help="Output file or directory")
    parser.add_argument("-p", "--precision", type=int, default=6,
                       help="Coordinate decimal precision (default: 6)")
    parser.add_argument("--no-compress", action="store_true",
                       help="Don't compress with gzip")
    parser.add_argument("--batch", action="store_true",
                       help="Process all .geojson files in directory")
    parser.add_argument("--pattern", default="*.geojson",
                       help="File pattern for batch mode (default: *.geojson)")
    
    args = parser.parse_args()
    
    compress = not args.no_compress
    
    if args.batch:
        print(f"Batch optimizing directory: {args.input}")
        results = batch_optimize_directory(
            args.input, args.output,
            pattern=args.pattern,
            precision=args.precision,
            compress=compress
        )
        
        print("\n" + "="*60)
        print("BATCH OPTIMIZATION SUMMARY")
        print("="*60)
        
        total_original = sum(r['original_size'] for r in results)
        total_optimized = sum(r['optimized_size'] for r in results)
        
        for r in results:
            print(f"{Path(r['input']).name}:")
            print(f"  {r['original_size']/(1024*1024):.2f} MB → {r['optimized_size']/(1024*1024):.2f} MB")
            print(f"  Reduction: {r['reduction']:.1f}%")
        
        print(f"\nTotal: {total_original/(1024*1024):.2f} MB → {total_optimized/(1024*1024):.2f} MB")
        print(f"Overall reduction: {100 * (1 - total_optimized / total_original):.1f}%")
        
    else:
        output_path, original_size, optimized_size = optimize_geojson(
            args.input, args.output,
            precision=args.precision,
            compress=compress
        )
        
        print("\n" + "="*60)
        print("OPTIMIZATION COMPLETE")
        print("="*60)
        print(f"Input:  {args.input}")
        print(f"Output: {output_path}")
        print(f"Size:   {original_size/(1024*1024):.2f} MB → {optimized_size/(1024*1024):.2f} MB")
        print(f"Saved:  {100 * (1 - optimized_size / original_size):.1f}%")

if __name__ == "__main__":
    main()