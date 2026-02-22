#!/usr/bin/env python3
"""
Parse coding standards from Markdown files and generate shell script checks (.NET)
"""

import re
import sys
import os
from pathlib import Path

class MarkdownRuleParser:
    def __init__(self, md_file):
        self.md_file = md_file
        self.rules = []
        
    def parse(self):
        """Parse markdown file and extract rules"""
        with open(self.md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract rule sections
        self._extract_must_follow_rules(content)
        self._extract_code_examples(content)
        
        return self.rules
    
    def _extract_must_follow_rules(self, content):
        """Extract rules from '必須遵守的規則' sections"""
        # Find sections marked with 🔴 or "MUST FOLLOW"
        must_sections = re.findall(
            r'##\s*🔴.*?必須遵守.*?(?=^##\s(?!#)|\Z)|##.*?MUST FOLLOW.*?(?=^##\s(?!#)|\Z)',
            content, re.DOTALL | re.IGNORECASE | re.MULTILINE
        )
        
        for section in must_sections:
            # Extract individual rules
            rules_in_section = re.findall(
                r'###\s*\d+\.\s*(.*?)\n(.*?)(?=###|\Z)',
                section, re.DOTALL
            )
            
            for rule_title, rule_content in rules_in_section:
                self._process_rule(rule_title.strip(), rule_content)
    
    def _extract_code_examples(self, content):
        """Extract ✅ correct and ❌ wrong examples"""
        # Find code blocks with ✅ or ❌ markers
        code_blocks = re.findall(
            r'(//\s*[✅❌].*?)\n(.*?)(?=```|//\s*[✅❌]|\Z)',
            content, re.DOTALL
        )
        
        for marker, code in code_blocks:
            if '❌' in marker:
                # This is a wrong pattern - we should check it doesn't exist
                self._add_antipattern_rule(marker, code)
            elif '✅' in marker:
                # This is a correct pattern - we might want to ensure it exists
                self._add_pattern_rule(marker, code)
    
    def _process_rule(self, title, content):
        """Process a rule section and extract checkable patterns"""
        # Look for specific patterns in the rule title + content
        text = f"{title}\n{content}"

        # Explicit patterns with optional flags, e.g. Pattern (forbidden, i): Foo
        explicit_patterns = re.findall(r'Pattern\s*\(([^)]+)\)\s*:\s*(.+)', content, re.IGNORECASE)
        if explicit_patterns:
            for options, pattern in explicit_patterns:
                opts = [o.strip().lower() for o in options.split(',')]
                if 'forbidden' in opts:
                    rule_type = 'forbidden'
                elif 'optional' in opts:
                    rule_type = 'optional'
                else:
                    rule_type = 'required'
                flags = []
                if 'i' in opts:
                    flags.append('i')
                if 'ignore-comment' in opts:
                    flags.append('ignore-comment')
                if 'any' in opts:
                    flags.append('any')
                self.rules.append({
                    'name': title,
                    'type': rule_type,
                    'pattern': pattern.strip(),
                    'description': f'Check: {title}',
                    'flags': flags
                })
        else:
            explicit_default = re.findall(r'Pattern\s*:\s*(.+)', content)
            for pattern in explicit_default:
                rule_type = 'forbidden' if ('禁止' in text or '不要' in text or 'forbidden' in text.lower()) else 'required'
                self.rules.append({
                    'name': title,
                    'type': rule_type,
                    'pattern': pattern.strip(),
                    'description': f'Check: {title}',
                    'flags': []
                })
        
        # Check for "不要" (don't) or "禁止" (forbidden) patterns
        if '不要' in text or '禁止' in text or 'not' in text.lower() or "don't" in text.lower():
            # Extract forbidden patterns
            patterns = self._extract_forbidden_patterns(text)
            for pattern in patterns:
                self.rules.append({
                    'name': title,
                    'type': 'forbidden',
                    'pattern': pattern,
                    'description': f'Check: {title}'
                })
        
        # Check for "必須" (must) patterns
        if '必須' in text or 'must' in text.lower():
            patterns = self._extract_required_patterns(text)
            for pattern in patterns:
                self.rules.append({
                    'name': title,
                    'type': 'required',
                    'pattern': pattern,
                    'description': f'Check: {title}'
                })
    
    def _extract_forbidden_patterns(self, content):
        """Extract patterns that should NOT exist"""
        patterns = []
        
        # Custom repository interfaces are forbidden
        if 'Repository' in content and 'interface' in content:
            patterns.append(r'interface\s+\w*Repository\s*:\s*IRepository')
        
        # Custom query methods in repository interfaces
        if 'findBy' in content or 'deleteBy' in content or 'query' in content.lower():
            patterns.append(r'\b(FindBy|DeleteBy|GetBy|QueryBy)')
        
        # Field injection patterns (avoid direct service locator / property injection)
        if 'Injection' in content or 'DI' in content:
            patterns.append(r'\[Inject\]|IServiceProvider')

        # Base test class usage is forbidden
        if 'BaseTestClass' in content or 'BaseUseCaseTest' in content:
            patterns.append(r'BaseTestClass|BaseUseCaseTest')
        
        return patterns
    
    def _extract_required_patterns(self, content):
        """Extract patterns that SHOULD exist"""
        patterns = []
        
        if 'IRepository' in content:
            patterns.append(r'IRepository<.*?>')
        
        if 'Mapper' in content and 'static' in content:
            patterns.append(r'static')
        
        if 'constructor' in content.lower():
            patterns.append(r'public\s+\w+\(')
        
        return patterns
    
    def _add_antipattern_rule(self, marker, code):
        """Add a rule for code that should NOT exist"""
        # Extract the pattern from the code
        if 'interface' in code and 'Repository' in code:
            self.rules.append({
                'name': 'No Custom Repository Interface',
                'type': 'forbidden',
                'pattern': r'interface\s+\w*Repository\s*:\s*IRepository',
                'description': marker.strip()
            })
    
    def _add_pattern_rule(self, marker, code):
        """Add a rule for code that SHOULD exist"""
        # This could be enhanced to extract specific patterns
        pass

def generate_script_from_rules(rules, script_name, source_file):
    """Generate shell script from extracted rules"""

    def build_target_finder(source_file):
        if source_file == "aggregate-standards.md":
            return 'find "$SRC_DIR" -type f \\( -path "*/Aggregates/*.cs" -o -name "*Aggregate*.cs" \\) -not -path "*/bin/*" -not -path "*/obj/*"'
        if source_file == "usecase-standards.md":
            return 'find "$SRC_DIR" -type f \\( -path "*/UseCases/*.cs" -o -path "*/Handlers/*.cs" -o -name "*UseCase*.cs" -o -name "*Handler*.cs" \\) -not -path "*/bin/*" -not -path "*/obj/*"'
        if source_file == "controller-standards.md":
            return 'find "$SRC_DIR" -type f \\( -path "*/Controllers/*.cs" -o -name "*Controller.cs" \\) -not -path "*/bin/*" -not -path "*/obj/*"'
        if source_file == "repository-standards.md":
            return 'find "$SRC_DIR" -type f \\( -path "*/Repositories/*.cs" -o -name "*Repository*.cs" \\) -not -path "*/bin/*" -not -path "*/obj/*"'
        if source_file == "mapper-standards.md":
            return 'find "$SRC_DIR" -type f \\( -path "*/Mappers/*.cs" -o -name "*Mapper*.cs" -o -name "*Mapping*.cs" \\) -not -path "*/bin/*" -not -path "*/obj/*"'
        if source_file == "projection-standards.md":
            return 'find "$SRC_DIR" -type f \\( -path "*/Projections/*.cs" -o -path "*/ReadModels/*.cs" -o -name "*Projection*.cs" -o -name "*ReadModel*.cs" \\) -not -path "*/bin/*" -not -path "*/obj/*"'
        if source_file == "archive-standards.md":
            return 'find "$SRC_DIR" -type f \\( -path "*/Archive/*.cs" -o -path "*/Archived/*.cs" -o -name "*Archive*.cs" \\) -not -path "*/bin/*" -not -path "*/obj/*"'
        if source_file == "test-standards.md":
            return 'find "$SRC_DIR" -type f \\( -path "*/Tests/*.cs" -o -name "*Test*.cs" \\) -not -path "*/bin/*" -not -path "*/obj/*"'
        return 'find "$SRC_DIR" -type f -name "*.cs" -not -path "*/bin/*" -not -path "*/obj/*"'
    
    script = f'''#!/bin/bash

# ====================================================================
# {script_name}
# 
# Generated from: {source_file}
# Purpose: Check compliance based on markdown documentation
# 
# THIS FILE IS AUTO-GENERATED FROM MARKDOWN - DO NOT EDIT MANUALLY
# Regenerate with: ./generate-check-scripts-from-md.sh
# ====================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SRC_DIR="$BASE_DIR/src"

TARGET_FILES=$({build_target_finder(source_file)})
if [ -z "$TARGET_FILES" ]; then
    echo -e "${{YELLOW}}⚠ No target files found for this check${{NC}}"
    exit 0
fi

# Flags
HAS_VIOLATIONS=false

echo -e "${{BLUE}}=======================================${{NC}}"
echo -e "${{BLUE}}{script_name}${{NC}}"
echo -e "${{BLUE}}=======================================${{NC}}"
echo ""

# ====================================================================
# Checks Generated from Markdown
# ====================================================================
'''
    
    # Add checks for each rule
    for i, rule in enumerate(rules, 1):
        flags = rule.get('flags', [])
        grep_cmd = "grep -E"
        if 'i' in flags:
            grep_cmd = "grep -Ei"
        allow_comment = 'ignore-comment' in flags
        require_any = 'any' in flags
        if rule['type'] == 'forbidden':
            # Check that pattern should NOT exist
            script += f'''
# Rule {i}: {rule['name']}
echo -e "${{YELLOW}}Checking: {rule['description']}${{NC}}"

# Pattern that should NOT exist: {rule['pattern']}
if [ {str(allow_comment).lower()} = "true" ]; then
    VIOLATIONS=""
    for file in $TARGET_FILES; do
        match=$({grep_cmd} "{rule['pattern']}" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
        if [ -n "$match" ]; then
            VIOLATIONS="$VIOLATIONS $file"
        fi
    done
else
    VIOLATIONS=$(echo "$TARGET_FILES" | xargs -I {{}} {grep_cmd} -l "{rule['pattern']}" {{}} 2>/dev/null || true)
fi

if [ -n "$VIOLATIONS" ]; then
    echo -e "${{RED}}✗ Found violations:${{NC}}"
    for file in $VIOLATIONS; do
        if [ {str(allow_comment).lower()} = "true" ]; then
            match=$({grep_cmd} "{rule['pattern']}" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -n "$match" ]; then
                echo -e "  ${{RED}}→${{NC}} $file"
                echo "$match" | sed 's/^/    /'
                HAS_VIOLATIONS=true
            fi
        else
            echo -e "  ${{RED}}→${{NC}} $file"
            {grep_cmd} "{rule['pattern']}" "$file" 2>/dev/null | head -1 | sed 's/^/    /'
            HAS_VIOLATIONS=true
        fi
    done
else
    echo -e "${{GREEN}}✓ No violations found${{NC}}"
fi
echo ""
'''
        elif rule['type'] == 'required':
            # Check that pattern SHOULD exist
            script += f'''
# Rule {i}: {rule['name']}
echo -e "${{YELLOW}}Checking: {rule['description']}${{NC}}"

# Pattern that should exist: {rule['pattern']}
if [ {str(require_any).lower()} = "true" ]; then
    if [ {str(allow_comment).lower()} = "true" ]; then
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {{}} {grep_cmd} "{rule['pattern']}" {{}} 2>/dev/null | grep -v "^[[:space:]]*//" | wc -l)
    else
        MATCHES=$(echo "$TARGET_FILES" | xargs -I {{}} {grep_cmd} -l "{rule['pattern']}" {{}} 2>/dev/null | wc -l)
    fi
    if [ "$MATCHES" -gt 0 ]; then
        echo -e "${{GREEN}}✓ Found $MATCHES files with correct pattern${{NC}}"
    else
        echo -e "${{YELLOW}}⚠ Warning: Pattern not found in any files${{NC}}"
    fi
else
    MISSING=()
    for file in $TARGET_FILES; do
        if [ {str(allow_comment).lower()} = "true" ]; then
            match=$({grep_cmd} "{rule['pattern']}" "$file" 2>/dev/null | grep -v "^[[:space:]]*//" | head -1 || true)
            if [ -z "$match" ]; then
                MISSING+=("$file")
            fi
        else
            if ! {grep_cmd} -q "{rule['pattern']}" "$file" 2>/dev/null; then
                MISSING+=("$file")
            fi
        fi
    done
    if [ "${{#MISSING[@]}}" -eq 0 ]; then
        echo -e "${{GREEN}}✓ All files contain the required pattern${{NC}}"
    else
        echo -e "${{YELLOW}}⚠ Warning: Pattern missing in ${{#MISSING[@]}} files${{NC}}"
        for file in "${{MISSING[@]}}"; do
            echo -e "  ${{YELLOW}}→${{NC}} $file"
        done
    fi
fi
echo ""
'''
        elif rule['type'] == 'optional':
            script += f'''
# Rule {i}: {rule['name']} (optional)
echo -e "${{YELLOW}}Checking (optional): {rule['description']}${{NC}}"

# Optional pattern: {rule['pattern']}
if [ {str(allow_comment).lower()} = "true" ]; then
    MATCHES=$(echo "$TARGET_FILES" | xargs -I {{}} {grep_cmd} "{rule['pattern']}" {{}} 2>/dev/null | grep -v "^[[:space:]]*//" | wc -l)
else
    MATCHES=$(echo "$TARGET_FILES" | xargs -I {{}} {grep_cmd} -l "{rule['pattern']}" {{}} 2>/dev/null | wc -l)
fi

if [ "$MATCHES" -gt 0 ]; then
    echo -e "${{GREEN}}✓ Found $MATCHES files with optional pattern${{NC}}"
else
    echo -e "${{CYAN}}ℹ Optional pattern not found${{NC}}"
fi
echo ""
'''
    
    # Add footer
    script += '''
# ====================================================================
# Summary
# ====================================================================

if [ "$HAS_VIOLATIONS" = true ]; then
    echo -e "${RED}✗ Violations found! Please fix the issues above.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ All checks passed!${NC}"
    exit 0
fi
'''
    
    return script

def main():
    if len(sys.argv) < 3:
        print("Usage: parse-md-rules.py <md-file> <output-file>")
        sys.exit(1)
    
    md_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(md_file):
        print(f"Error: Markdown file not found: {md_file}")
        sys.exit(1)
    
    try:
        # Parse rules from markdown
        parser = MarkdownRuleParser(md_file)
        rules = parser.parse()
        
        if not rules:
            print(f"Warning: No rules extracted from {md_file}")
            rules = []
        
        # Generate script name from file name
        base_name = os.path.basename(md_file).replace('-standards.md', '')
        script_name = f"{base_name.title()} Compliance Check"
        
        # Generate script
        script = generate_script_from_rules(rules, script_name, os.path.basename(md_file))
        
        # Write output
        with open(output_file, 'w') as f:
            f.write(script)
        
        # Make executable
        os.chmod(output_file, 0o755)
        
        print(f"✓ Generated: {output_file} ({len(rules)} rules)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
