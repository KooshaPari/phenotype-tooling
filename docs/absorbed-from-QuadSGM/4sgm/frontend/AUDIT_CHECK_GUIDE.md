# Audit Check Instrumentation Guide

## Overview

The audit check instrumentation system for 4SGM Frontend provides comprehensive TypeScript error detection, categorization, and remediation strategies for the reported **3,107 errors across 510 files**.

## Architecture

### Core Components

1. **`lib/audit-check.instrumentation.ts`**
   - Main audit engine with error analysis
   - Error categorization and severity classification
   - Report generation (JSON & Markdown)
   - Pattern matching for error detection

2. **`instrumentation.ts`**
   - Next.js instrumentation hook
   - Application startup initialization
   - Type consistency checking
   - Observability integration

## Error Categories

The system categorizes errors into:

| Category | Severity | Fixable | Description |
|----------|----------|---------|-------------|
| `UNUSED_IMPORTS` | LOW | ✅ | Imported but never used |
| `TYPE_MISMATCH` | HIGH | ❌ | Type incompatibility issues |
| `MISSING_DECLARATION` | CRITICAL | ❌ | Missing type/variable declarations |
| `IMPLICIT_ANY` | MEDIUM | ❌ | Parameters/properties without types |
| `UNUSED_VARIABLES` | LOW | ✅ | Declared but unused variables |
| `MISSING_RETURN_TYPE` | MEDIUM | ❌ | Functions without return types |
| `NON_NULL_ASSERTION` | MEDIUM | ❌ | Possible null/undefined access |
| `IMPORT_ERRORS` | CRITICAL | ❌ | Module not found or path errors |
| `DEPRECATED_API` | MEDIUM | ❌ | Using deprecated APIs |

## Quick Start

### 1. Enable Audit Checks

Add to your `.env.local`:

```bash
INSTRUMENTATION_ENABLED=true
AUDIT_CHECK_ENABLED=true
LOG_LEVEL=info
AUDIT_REPORT_PATH=./audit-report.json
```

### 2. Run TypeScript Check

```bash
# Full type check
npm run tsc -- --noEmit

# Get JSON output
npm run tsc -- --noEmit --pretty false > tsc-output.txt
```

### 3. Parse and Analyze

```bash
# Create a Node.js script to parse and categorize errors
node scripts/analyze-errors.js < tsc-output.txt
```

## Usage Examples

### Basic Audit Engine Usage

```typescript
import { AuditCheckEngine, ErrorCategory, ErrorSeverity } from '@/lib/audit-check.instrumentation';

// Create audit engine
const engine = new AuditCheckEngine();

// Add diagnostic output from TypeScript
const tscOutput = `src/lib/ai-client.ts(10,5): error TS7006: Parameter implicitly has an 'any' type`;
engine.addDiagnosticOutput(tscOutput);

// Generate report
const report = engine.generateReport();

// Export as JSON
await engine.exportReportJSON('audit-report.json', report);

// Export as Markdown
await engine.exportReportMarkdown('audit-report.md', report);
```

### Filter by Severity

```typescript
const report = engine.generateReport();

// Get critical errors only
const criticalErrors = report.errorsBySeverity.get(ErrorSeverity.CRITICAL);

// Get high priority errors
const highPriority = report.errorsBySeverity.get(ErrorSeverity.HIGH);
```

### Filter by Category

```typescript
// Get all unused imports
const unusedImports = report.errorsByCategory.get(ErrorCategory.UNUSED_IMPORTS);

// Get type mismatches
const typeErrors = report.errorsByCategory.get(ErrorCategory.TYPE_MISMATCH);
```

## Remediation Strategies

### Strategy 1: Unused Imports (Quick Fix)

**Pattern:** `src/components/**/*.tsx` (6 errors in CommentEditor.tsx)

**Automated Fix:**
```bash
npm run eslint -- --fix src/components/comments/CommentEditor.tsx
```

**Manual Fix:**
```typescript
// Remove unused imports
- import { unused } from '@/lib/unused';
```

### Strategy 2: Missing Type Annotations

**Pattern:** `src/hooks/**/*.ts` (235 errors in useRequirementsAdvancedApi.ts)

**Manual Fix:**
```typescript
// Add explicit types
- const handleSelect = (item) => { ... }
+ const handleSelect = (item: Requirement): void => { ... }
```

### Strategy 3: Type Mismatches

**Pattern:** `src/lib/**/*.ts` (Multiple mismatch errors)

**Debug Process:**
1. Check source type definition
2. Check target type usage
3. Add type assertion or convert value

```typescript
// Example fix
- const value: string = unknownValue;
+ const value: string = String(unknownValue);
```

### Strategy 4: Missing Module/Import

**Pattern:** `src/app/(auth)/**/*.tsx` (Import errors)

**Fix:**
```bash
# Verify file exists
ls -la src/app/auth/verify-email/page.tsx

# Check import path
# Update path if needed
- import { Component } from '../../../components/Component'
+ import { Component } from '@/components/Component'
```

## Error Distribution Analysis

### Critical Errors (Must Fix)

```
TOTAL CRITICAL: ~200-300
- Missing declarations (30)
- Import errors (15)
```

**Action Items:**
1. Fix all missing imports/modules first
2. Add missing type declarations
3. Run TypeScript check to unblock compilation

### High Priority Errors (Should Fix)

```
TOTAL HIGH: ~500-600
- Type mismatches (400+)
```

**Action Items:**
1. Review type definitions
2. Align component interfaces
3. Add type guards where needed

### Medium Priority Errors

```
TOTAL MEDIUM: ~1000-1200
- Implicit any types
- Missing return types
- Possible null/undefined access
```

**Action Items:**
1. Add explicit type annotations
2. Enable stricter tsconfig options
3. Add null checks

### Low Priority Errors

```
TOTAL LOW: ~1400-1600
- Unused imports
- Unused variables
```

**Action Items:**
1. Run ESLint --fix to clean up
2. Remove dead code

## TypeScript Configuration Optimization

### Enable Stricter Checking

Update `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Type Check & Audit

on: [pull_request, push]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - run: npm ci
      - run: npm run tsc -- --noEmit > tsc-output.txt
      - run: node scripts/analyze-errors.js < tsc-output.txt

      - name: Upload Audit Report
        uses: actions/upload-artifact@v3
        with:
          name: audit-report
          path: audit-report.json
```

## Scripts for Automation

### `scripts/analyze-errors.js`

```javascript
const fs = require('fs');
const readline = require('readline');
const { AuditCheckEngine } = require('../lib/audit-check.instrumentation');

async function analyzeErrors() {
  const engine = new AuditCheckEngine();
  const rl = readline.createInterface({
    input: process.stdin,
  });

  for await (const line of rl) {
    engine.addDiagnosticOutput(line);
  }

  const report = engine.generateReport();
  console.log(JSON.stringify(report, null, 2));
}

analyzeErrors();
```

### `scripts/fix-common-errors.sh`

```bash
#!/bin/bash

echo "Fixing common TypeScript errors..."

# 1. Remove unused imports and variables
npm run eslint -- --fix src/

# 2. Run TypeScript type check
npm run tsc -- --noEmit

echo "✓ Auto-fixes applied"
```

## Monitoring & Reporting

### Generate HTML Report

```typescript
async function generateHTMLReport(report: AuditReport) {
  const html = `
    <html>
      <head><title>Audit Report</title></head>
      <body>
        <h1>Audit Check Report</h1>
        <p>Total Errors: ${report.totalErrors}</p>
        <h2>By Severity</h2>
        ${Array.from(report.errorsBySeverity.entries())
          .map(([sev, errs]) => `<p>${sev}: ${errs.length}</p>`)
          .join('')}
      </body>
    </html>
  `;

  await fs.writeFile('audit-report.html', html);
}
```

### Track Error Trends

```bash
# Run audit weekly
npm run audit > audit-$(date +%Y-%m-%d).json

# Compare reports
jq '.summary.totalErrors' audit-2024-01-01.json
jq '.summary.totalErrors' audit-2024-01-08.json
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `INSTRUMENTATION_ENABLED` | `true` | Enable/disable instrumentation |
| `AUDIT_CHECK_ENABLED` | `true` | Enable/disable audit checks |
| `LOG_LEVEL` | `info` | Logging level (error\|warn\|info\|debug) |
| `AUDIT_REPORT_PATH` | `./audit-report.json` | Output report path |

## Troubleshooting

### Issue: "Cannot find module" errors

**Solution:**
1. Check all import paths are relative to project root
2. Use `@/` alias configured in `tsconfig.json`
3. Verify files exist

### Issue: Type mismatch in props

**Solution:**
1. Export interfaces from component files
2. Use `React.FC<Props>` typing
3. Add prop validation with Zod or similar

### Issue: Unused imports not auto-fixed

**Solution:**
```bash
npm run eslint -- --fix --ext .ts,.tsx src/
```

## Next Steps

1. **Run Initial Audit**
   ```bash
   npm run tsc -- --noEmit > errors.txt
   node scripts/analyze-errors.js < errors.txt
   ```

2. **Fix Critical Errors** (blocking)
   - Missing imports and declarations
   - Module not found errors

3. **Fix Type Issues** (high priority)
   - Type mismatches
   - Implicit any types

4. **Clean Up** (low priority)
   - Remove unused imports
   - Delete unused variables

5. **Enable CI Integration**
   - Set up automated checks
   - Block PRs on new errors

## References

- [TypeScript Error Codes](https://www.typescriptlang.org/docs/handbook/error-index.html)
- [Next.js Instrumentation](https://nextjs.org/docs/app/building-your-application/optimizing/instrumentation)
- [ESLint Type-Aware Rules](https://typescript-eslint.io/linting/typed-linting/)
