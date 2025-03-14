#!/usr/bin/env python
"""
Dedicated entry point for Electron to avoid module import issues.
This bridge script provides a clean interface between Electron and the Python package.
"""
import sys
import os
import json
import argparse


def main():
    # Create a parser that only processes the first argument (command)
    parser = argparse.ArgumentParser(description="Electron-Python bridge")
    parser.add_argument('command', help='Command to execute')
    
    # Parse just the first argument and collect remaining arguments
    args, remaining = parser.parse_known_args()
    
    if args.command == 'generate':
        # Import the module directly rather than using runpy
        from image2textart_generator.cli import main as cli_main
        # Replace sys.argv with our remaining arguments
        sys.argv = ['image2textart_generator.cli'] + remaining
        # Run the CLI main function
        return cli_main()
    elif args.command == 'get_presets':
        from image2textart_generator.characters import CharacterSet
        presets = CharacterSet.get_preset_names()
        print(json.dumps(presets))
        return 0
    elif args.command == 'suggest_settings':
        from image2textart_generator.utils import suggest_optimal_settings
        # Extract image path and width if provided
        image_path = None
        width = 100
        
        if remaining and not remaining[0].startswith('--'):
            image_path = remaining[0]
            remaining = remaining[1:]
        
        # Look for width flag
        for i, arg in enumerate(remaining):
            if arg == '--width' and i+1 < len(remaining):
                try:
                    width = int(remaining[i+1])
                except ValueError:
                    pass
                break
                
        if not image_path:
            print(json.dumps({"error": "No image path provided"}))
            return 1
            
        settings = suggest_optimal_settings(image_path, width)
        print(json.dumps(settings))
        return 0
    elif args.command == 'test':
        # Simple test command to verify the bridge is working
        print(json.dumps({"status": "OK", "python_version": sys.version}))
        return 0
    else:
        print(json.dumps({"error": f"Unknown command: {args.command}"}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
