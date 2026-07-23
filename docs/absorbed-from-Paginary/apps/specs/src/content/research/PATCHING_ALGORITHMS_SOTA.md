# State of the Art: Code Patching and Diffing Algorithms

## Executive Summary

This document provides a comprehensive analysis of state-of-the-art diffing algorithms, patch formats, and merge strategies used in modern software development. Understanding these algorithms is critical for the phenotype-patch project to implement robust, efficient, and reliable code patching capabilities.

---

## Table of Contents

1. [Diff Algorithms](#1-diff-algorithms)
   - 1.1 [Myers' Algorithm](#11-myers-algorithm)
   - 1.2 [Patience Diff Algorithm](#12-patience-diff-algorithm)
   - 1.3 [Histogram Diff Algorithm](#13-histogram-diff-algorithm)
   - 1.4 [Minimal Edit Script Algorithms](#14-minimal-edit-script-algorithms)
2. [Patch Formats](#2-patch-formats)
   - 2.1 [Unified Diff Format](#21-unified-diff-format)
   - 2.2 [Git Diff Format](#22-git-diff-format)
   - 2.3 [Context Diff Format](#23-context-diff-format)
   - 2.4 [Normal Diff Format](#24-normal-diff-format)
   - 2.5 [Ed Scripts](#25-ed-scripts)
   - 2.6 [W3C XML Patch](#26-w3c-xml-patch)
3. [Three-Way Merge Algorithms](#3-three-way-merge-algorithms)
   - 3.1 [Fuzzy Patch Application](#31-fuzzy-patch-application)
   - 3.2 [Diff3 Algorithm](#32-diff3-algorithm)
   - 3.3 [Recursive Three-Way Merge](#33-recursive-three-way-merge)
   - 3.4 [Octopus Merge](#34-octopus-merge)
4. [Specialized Diffing](#4-specialized-diffing)
   - 4.1 [AST-Based Diffing](#41-ast-based-diffing)
   - 4.2 [Semantic Diffing](#42-semantic-diffing)
   - 4.3 [Binary Diffing](#43-binary-diffing)
5. [Algorithm Complexity Analysis](#5-algorithm-complexity-analysis)
6. [Recommendations for phenotype-patch](#6-recommendations-for-phenotype-patch)
7. [References](#7-references)

---

## 1. Diff Algorithms

### 1.1 Myers' Algorithm

Myers' diff algorithm, introduced by Eugene Myers in 1986, is the foundational algorithm used by most modern diff implementations, including the default algorithm in Git.

#### Theoretical Foundation

Myers' algorithm solves the Longest Common Subsequence (LCS) problem by transforming it into a shortest path problem in an edit graph. Given two sequences A and B of lengths N and M, the algorithm constructs an edit graph where:

- Horizontal edges represent deletions (cost: 1)
- Vertical edges represent insertions (cost: 1)
- Diagonal edges represent matches (cost: 0)

The edit graph has (N+1) × (M+1) vertices arranged in a grid, with the source at (0,0) and the sink at (N,M).

#### Algorithm Mechanics

The algorithm uses dynamic programming with the following key insights:

1. **Edit Graph Representation**: Each point (x, y) in the graph represents processing x elements from sequence A and y elements from sequence B.

2. **D-Path Concept**: A D-path is a path starting at (0,0) with exactly D non-diagonal edges. The algorithm searches for increasing values of D until reaching the sink.

3. **Greedy Search**: For each D, the algorithm finds the furthest reaching D-path in each diagonal k (where k = x - y).

4. **Snake Traversal**: After each non-diagonal move, the algorithm follows diagonal "snakes" (sequences of matches) as far as possible.

```
Pseudocode:
function MyersDiff(A, B):
    N = length(A)
    M = length(B)
    MAX = N + M
    
    V = array[-MAX..MAX]  // Furthest reaching D-path on diagonal k
    V[1] = 0
    
    for D = 0 to MAX:
        for k = -D to D in steps of 2:
            if k = -D or (k ≠ D and V[k-1] < V[k+1]):
                x = V[k+1]  // Move down (insertion)
            else:
                x = V[k-1] + 1  // Move right (deletion)
            y = x - k
            
            // Follow diagonal snake
            while x < N and y < M and A[x] == B[y]:
                x++, y++
            
            V[k] = x
            
            if x ≥ N and y ≥ M:
                return reconstruct_path(V, D, k)
```

#### Time and Space Complexity

- **Time Complexity**: O(ND), where N is the sum of file lengths and D is the edit distance (number of differences)
- **Space Complexity**: O(N + D²) or O(N + D) with optimizations
- **Worst Case**: O(N × M) when files are completely different

The O(ND) complexity is significantly better than the naive O(N × M) for files with few differences, which is the common case in version control.

#### Optimizations

1. **Linear Space Refinement**: Myers' 1986 paper also describes an O(N) space variant using recursive divide-and-conquer
2. **Greedy Filing**: Early termination when paths meet in the middle (bidirectional search)
3. **Preprocessing**: Removal of common prefix and suffix before running the algorithm

#### Limitations

- Produces minimal edit scripts but may not be human-readable
- Can produce noisy diffs when code is reorganized (lines moved)
- No semantic understanding of the content

---

### 1.2 Patience Diff Algorithm

The Patience Diff algorithm was developed by Bram Cohen (creator of BitTorrent) to produce more human-readable diffs, particularly for code with repeated elements like braces or blank lines.

#### Core Concept

Patience diff focuses on finding the longest common subsequence using only unique elements. The algorithm is named after the card game "Patience Sorting" (also known as Solitaire) because it uses a similar approach to finding longest increasing subsequences.

#### Algorithm Steps

1. **Unique Element Identification**: Scan both files and identify lines that appear exactly once in each file.

2. **Longest Common Subsequence (LCS)**: Find the LCS of these unique elements using patience sorting technique:
   - Create piles using binary search (O(n log n))
   - Track parent pointers for reconstruction

3. **Recursive Application**: Apply the algorithm recursively to the regions between matched unique lines.

4. **Myers Fallback**: For sections where no unique elements exist, fall back to Myers' algorithm.

```
Pseudocode:
function PatienceDiff(A, B):
    // Step 1: Find unique lines in both files
    uniqueA = find_unique_lines(A)
    uniqueB = find_unique_lines(B)
    
    // Step 2: Find LCS of unique lines using patience sorting
    common_unique = intersection(uniqueA, uniqueB)
    lcs = patience_sorting_lcs(common_unique)
    
    // Step 3: Recursively process between matches
    result = []
    last_a, last_b = 0, 0
    
    for (pos_a, pos_b) in lcs:
        // Process region before this match
        if pos_a > last_a or pos_b > last_b:
            sub_diff = PatienceDiff(A[last_a:pos_a], B[last_b:pos_b])
            result.extend(sub_diff)
        
        // Add the matching line
        result.append(('equal', A[pos_a]))
        last_a, last_b = pos_a + 1, pos_b + 1
    
    // Process remaining tail
    if last_a < len(A) or last_b < len(B):
        sub_diff = PatienceDiff(A[last_a:], B[last_b:])
        result.extend(sub_diff)
    
    return result
```

#### Patience Sorting for LCS

The patience sorting technique finds LCS in O(n log n):

1. Process elements left to right
2. For each element, find the leftmost pile with top card > current
3. Place element on that pile (or create new pile)
4. Maintain parent pointers for reconstruction

#### Advantages

1. **Human-Readable Output**: Focuses on unique lines (typically meaningful content like function names, variable declarations)
2. **Better for Code**: Ignores repetitive boilerplate (indentation, braces, blank lines)
3. **Intuitive Mappings**: Matches semantically significant lines first

#### Complexity Analysis

- **Time Complexity**: O(N log N) for patience sorting phase, plus recursive calls
- **Space Complexity**: O(N) for storing unique lines and piles
- **Practical Performance**: Often slower than Myers but produces better results

#### Limitations

- Requires O(N) extra space for hash tables
- Performance degrades when few unique lines exist
- Fallback to Myers needed for completely duplicated content

---

### 1.3 Histogram Diff Algorithm

Histogram diff is Git's default diff algorithm (since Git 2.9, 2016) and represents an evolution of patience diff with improved performance characteristics.

#### Evolution from Patience Diff

Histogram diff was developed to address patience diff's performance issues while maintaining its human-readable output quality. It uses a different approach to find matching regions based on occurrence frequency histograms.

#### Algorithm Mechanics

1. **Frequency Analysis**: Build histograms of line occurrences in both files

2. **Low-Frequency Matching**: Prioritize matching lines with low occurrence counts (more distinctive)

3. **Coalesce Passes**: After initial matches, coalesce adjacent regions and recursively process unmatched sections

4. **Multiple Pass Strategy**:
   - Pass 1: Match lines occurring exactly once in both (unique matches)
   - Pass 2: Match lines with low frequency (rare matches)
   - Pass 3: Fall back to Myers for remaining regions

#### Key Improvements Over Patience

1. **Better Performance**: O(N) average case vs O(N log N) for patience
2. **Reduced Memory**: Smaller working set during processing
3. **Improved Matches**: Considers frequency, not just uniqueness
4. **Coalescing**: Better handling of adjacent changes

#### Complexity Analysis

- **Time Complexity**: O(N) average case, O(N log N) worst case
- **Space Complexity**: O(N) for histograms and working buffers
- **Practical Performance**: Comparable to Myers for most inputs, better output quality

#### Implementation Details

Git's histogram diff uses:
- Hash tables with Robin Hood hashing for frequency counting
- Bitmap tracking for fast coalescing detection
- Adaptive threshold for rare line detection

---

### 1.4 Minimal Edit Script Algorithms

Beyond LCS-based approaches, several algorithms focus on minimal edit scripts for specific use cases.

#### 1.4.1 Hunt-Szymanski Algorithm

An early O((R + N) log N) algorithm where R is the number of matching pairs:

1. Build an index of all positions where each element of A appears in B
2. Process A left-to-right, maintaining candidates for LCS
3. Use binary search tree for efficient candidate management

#### 1.4.2 Wu's O(NP) Algorithm

Developed by Sun Wu in 1990, this algorithm improves on Myers for large D:

- Runs in O(NP) where P = (D/2) - (number of deletions)
- More efficient when one file is significantly shorter
- Used in some specialized diff tools

#### 1.4.3 Hirschberg's Algorithm

A linear-space LCS algorithm using divide-and-conquer:

1. Divide first sequence in half
2. Find optimal split point in second sequence
3. Recursively solve both halves
4. Combine results

Space complexity: O(N)
Time complexity: O(N × M) but with better constants

---

## 2. Patch Formats

### 2.1 Unified Diff Format

Unified diff (unidiff) is the de facto standard patch format, introduced by GNU diff in the early 1990s. It combines context from both files into a single compact representation.

#### Format Specification

```
--- original_file	imestamp
+++ modified_file	timestamp
@@ -start_line,count +start_line,count @@ section_header
 context_line
-context_line (removed)
+context_line (added)
 context_line
```

#### Hunk Structure

A unified diff consists of multiple "hunks":

1. **Header Line**: `@@ -l,s +l,s @@` where:
   - `l` = starting line number
   - `s` = number of lines in the hunk
   - `-` = old file, `+` = new file

2. **Context Lines**: Prefixed with space (` `), present in both files
3. **Deleted Lines**: Prefixed with minus (`-`), only in old file
4. **Added Lines**: Prefixed with plus (`+`), only in new file

#### Example

```diff
--- src/main.c	2024-01-15 10:30:00.000000000 -0500
+++ src/main.c	2024-01-16 14:45:00.000000000 -0500
@@ -42,8 +42,12 @@ int main(int argc, char **argv) {
     // Initialize configuration
     config_t *cfg = config_init();
     if (!cfg) {
-        fprintf(stderr, "Failed to initialize config\n");
+        log_error("Failed to initialize config: %s", strerror(errno));
         return EXIT_FAILURE;
     }
+    
+    // Set default log level
+    log_set_level(LOG_INFO);
+
     process_args(argc, argv, cfg);
     return run_application(cfg);
 }
```

#### Context Lines

Context lines (unchanged lines surrounding changes) serve multiple purposes:

1. **Verification**: Confirm patch applies to correct location
2. **Fuzzy Matching**: Allow patch to apply with line offsets
3. **Human Readability**: Provide surrounding code context

Standard context sizes:
- Default: 3 lines (can be changed with `-U` flag)
- Minimal: 0 lines (`-U0`)
- Full: all lines (`-U999999`)

#### Line Number Handling

Unified diff uses line numbers that:
- Start at 1 (not 0)
- Are relative to file start, not hunk start
- Account for all lines including context

#### Advantages

- Compact representation
- Human-readable
- Supports fuzzy matching
- Widely supported

#### Limitations

- No metadata support (permissions, binary files)
- Line-oriented (no character-level diff)
- Cannot represent file moves/renames

---

### 2.2 Git Diff Format

Git diff extends unified diff with additional metadata and supports more operation types.

#### Extended Headers

Git diff adds structured headers:

```diff
diff --git a/src/main.c b/src/main.c
index 3a4b5c6..7d8e9f0 100644
--- a/src/main.c
+++ b/src/main.c
@@ -42,8 +42,12 @@ int main(int argc, char **argv) {
```

#### Index Lines

The `index` line contains:
- Old blob SHA-1: `3a4b5c6`
- New blob SHA-1: `7d8e9f0`
- File mode: `100644` (regular), `100755` (executable), `120000` (symlink)

#### Extended Metadata

```diff
old mode 100644
new mode 100755
--- a/src/main.c
+++ b/src/main.c
@@ -1,5 +1,5 @@
 #!/usr/bin/env python3
-# Copyright 2023
+# Copyright 2024
```

#### Binary Files

Git diff handles binary files:

```diff
diff --git a/assets/logo.png b/assets/logo.png
index 1234567..890abcd 100644
Binary files differ
```

Or with textual representation:

```diff
diff --git a/assets/logo.png b/assets/logo.png
index 1234567..890abcd 100644
--- a/assets/logo.png
+++ b/assets/logo.png
@@ -0,0 +1 @@
+/uQRwCrZ//v//v//v//v//v//v//v//v//v//v//v//v//v
```

#### Rename Detection

```diff
diff --git a/old_name.c b/new_name.c
similarity index 98%
rename from old_name.c
rename to new_name.c
index 3a4b5c6..7d8e9f0 100644
--- a/old_name.c
+++ b/new_name.c
@@ -1,5 +1,5 @@
```

#### Copy Detection

```diff
diff --git a/original.c b/copy.c
similarity index 100%
copy from original.c
copy to copy.c
```

#### Advantages

- Complete metadata support
- Binary file handling
- Rename/copy detection
- Git-specific features (submodules, objects)

---

### 2.3 Context Diff Format

Context diff is the predecessor to unified diff, now rarely used but still supported.

#### Format

```diff
*** original_file	timestamp
--- modified_file	timestamp
***************
*** old_start,old_count ****
  context_line
- removed_line
  context_line
--- new_start,new_count ----
  context_line
+ added_line
  context_line
```

#### Characteristics

- Separates old and new context into different sections
- More verbose than unified diff
- Uses `***` for old file, `---` for new file
- Supports function names in headers

#### When Used

- Legacy systems
- Patch utility compatibility
- Some merge tools

---

### 2.4 Normal Diff Format

The simplest diff format, showing changes without context.

#### Format

```diff
1d0
< #!/bin/sh
3c2
< echo "Hello"
---
> echo "Goodbye"
10a10
> echo "Extra line"
```

#### Edit Commands

- `d` = delete (line numbers: old then new)
- `a` = add/append (line numbers: old then new)
- `c` = change (replaces lines)

#### Usage

- Minimal output needs
- Script processing
- Educational purposes

---

### 2.5 Ed Scripts

Ed script format generates commands for the Unix `ed` line editor.

#### Format

```ed
42,45d
48a
    log_set_level(LOG_INFO);
    .
52c
    log_error("New message");
    .
w
q
```

#### Commands

- `d` = delete lines
- `a` = append after line
- `i` = insert before line
- `c` = change (replace) lines
- `.` = end of input
- `w` = write
- `q` = quit

#### Use Cases

- Automated editing
- Legacy patch application
- Reverse patches (with `-R` flag)

---

### 2.6 W3C XML Patch

XML Patch (RFC 5261) defines a standardized format for patching XML documents.

#### Format

```xml
<diff>
  <replace sel="/root/element[@id='1']/text()">
    New content
  &lt;/replace>
  <add sel="/root/container" pos="last-child">
    <newElement>Content&lt;/newElement>
  &lt;/add>
  <remove sel="/root/obsolete"/>
&lt;/diff>
```

#### Operations

- `add`: Insert new content
- `replace`: Replace content
- `remove`: Delete content
- `replace-att`: Replace attribute value

#### XPath Selectors

Uses XPath 1.0 for precise targeting:
- `/root/element` - absolute paths
- `//element` - descendant search
- `[@attr='value']` - attribute matching

#### Applications

- Configuration management
- Web services
- Document processing

---

## 3. Three-Way Merge Algorithms

### 3.1 Fuzzy Patch Application

Fuzzy matching allows patches to apply even when the exact line numbers don't match.

#### Algorithm

1. **Offset Search**: Search for context lines around expected location
2. **Similarity Scoring**: Calculate match confidence based on:
   - Exact context matches
   - Whitespace variations
   - Line insertions/deletions nearby

3. **Threshold Application**: Apply if similarity > threshold (typically 50%)

#### Confidence Calculation

```
score = (matching_context_lines / total_context_lines) × 100
```

Levels:
- **Exact**: 100% match
- **Fuzzy (high)**: 80-99% match
- **Fuzzy (medium)**: 50-79% match
- **Rejected**: < 50% match

#### Implementation Details

GNU patch uses:
- Context line matching with normalization
- Offset tracking (line number differences)
- Multiple attempt locations

---

### 3.2 Diff3 Algorithm

Diff3 compares three versions: original (base), and two modified versions.

#### Input

- `O`: Original/base file
- `A`: Version A changes
- `B`: Version B changes

#### Algorithm Steps

1. **Pairwise Diffs**: Compute O→A and O→B
2. **Alignment**: Create merged timeline of all changes
3. **Classification**: Categorize each region:
   - **Unchanged**: Same in all three
   - **A only**: Changed only in A
   - **B only**: Changed only in B
   - **Same change**: Identical change in A and B
   - **Conflict**: Different changes in A and B

#### Conflict Detection

```
A's version of conflicting lines
B's version of conflicting lines
```

#### Output Format

Diff3 can produce:
- Ed script
- Merged file with conflicts marked
- Strict merge (fail on conflict)

#### Complexity

- Time: O(N × D) where D is maximum edit distance
- Space: O(N)

---

### 3.3 Recursive Three-Way Merge

Git's recursive merge strategy handles cases with multiple merge bases.

#### When Multiple Merge Bases Exist

Branch topology:
```
      A---B---C topic
     /
D---E---F---G---H main
     \   /
      I---J intermediate
```

Here, both E and G are merge bases.

#### Recursive Algorithm

1. **Find All Merge Bases**: Using commit graph analysis
2. **Recursive Merge Bases**: If multiple bases, recursively merge them first
3. **Virtual Base Creation**: Create synthetic merge base
4. **Three-Way Merge**: Use virtual base as O

#### Complexity

- Time: O(k × N × D) where k is recursion depth
- Space: O(k × N)

#### Advantages

- Handles complex branch histories
- Reduces false conflicts
- Properly tracks renames across branches

---

### 3.4 Octopus Merge

Octopus merge combines more than two branches simultaneously.

#### Algorithm

1. **Pairwise Strategy**: Select two branches as initial merge
2. **Iterative Merge**: Merge result with next branch
3. **Continue**: Until all branches merged or conflict

#### Requirements

- No conflicts allowed between any branches
- All changes must be mutually compatible
- Must resolve to single tree

#### Use Cases

- Integrating multiple feature branches
- Large-scale collaboration
- Automated merging systems

---

## 4. Specialized Diffing

### 4.1 AST-Based Diffing

Abstract Syntax Tree (AST) diffing compares code structure rather than text.

#### Approach

1. **Parse**: Convert source code to AST
2. **Tree Comparison**: Compare node structures
3. **Edit Script**: Generate tree edit operations

#### Algorithms

**GumTree Algorithm** (Falleri et al., 2014):
- Bottom-up matching for leaf nodes
- Top-down matching for inner nodes
- Edit script generation

Complexity: O(n²) worst case, O(n log n) typical

**MTDIFF**:
- Multi-tier matching strategy
- Handles moved code blocks
- Source: https://github.com/Treeeeeeee/mtdiff

#### Applications

- Refactoring detection
- Code review tools
- Plagiarism detection
- Merge conflict resolution

#### Tools

- **GumTree**: https://github.com/GumTreeDiff/gumtree
- **MTDIFF**: Java-based AST differencing
- **Tree-sitter**: Parser infrastructure

---

### 4.2 Semantic Diffing

Semantic diffing understands programming language semantics.

#### Techniques

1. **Rename Detection**: Variable/function renames
2. **Type-Aware Comparison**: Consider type information
3. **Control Flow Analysis**: Understand code structure

#### Implementation

```python
# Before
x = calculate_value()
result = x * 2

# After
final_value = calculate_value()
result = final_value * 2
```

Semantic diff recognizes this as a rename, not deletion+addition.

#### Tools

- **SemanticDiff**: https://semanticdiff.com/
- **Difftastic**: Syntax-aware structural diffing
- **CodeCompass**: Research tool

---

### 4.3 Binary Diffing

Binary diffing compares non-text files.

#### Approaches

**1. Byte-Level Diffing**:
- Treat as opaque byte sequence
- Similar to text diff but on bytes
- Used for: executables, images

**2. Structured Binary Diffing**:
- Parse file format (ELF, PE, Mach-O)
- Compare sections, symbols
- Tools: Diaphora, BinDiff

**3. Delta Encoding**:
- Encode only differences
- Efficient for small changes
- Used in: rsync, zsync

#### Rolling Checksum

Rsync algorithm uses rolling checksum for efficient binary diff:

1. **Weak Checksum**: Fast rolling Adler-32
2. **Strong Checksum**: MD5 for verification
3. **Block Matching**: Find matching blocks

Complexity: O(N) for both files

#### Tools

- **bsdiff**: Binary patch tool using suffix sorting
- **xdelta**: Delta encoding
- **courgette**: Chromium's specialized diff for executables

---

## 5. Algorithm Complexity Analysis

### Summary Table

| Algorithm | Time Complexity | Space Complexity | Best For |
|-----------|----------------|------------------|----------|
| Myers | O(ND) | O(N) or O(N+D²) | General purpose, VCS |
| Patience | O(N log N) | O(N) | Code review, human-readable |
| Histogram | O(N) avg | O(N) | Git default, balanced |
| Hunt-Szymanski | O((R+N) log N) | O(N) | Many matches |
| Hirschberg | O(N×M) | O(N) | Memory constrained |
| Wu O(NP) | O(NP) | O(N) | Large deletions |
| GumTree (AST) | O(n²) | O(n²) | Structural diffing |

### D Parameter Significance

In O(ND) algorithms, D (edit distance) is typically small:
- Source code: D < 1% of N
- Documentation: D < 5% of N
- Config files: D < 10% of N

This makes O(ND) effectively O(N) in practice.

### Memory Hierarchy Impact

| Algorithm | Cache Efficiency | Working Set |
|-----------|-----------------|-------------|
| Myers | Good | Two rows of DP table |
| Patience | Moderate | Hash table + piles |
| Histogram | Good | Histogram + scan |

### Practical Performance

Based on empirical measurements (Git performance tests):

- Myers: Baseline (1.0x)
- Patience: 2-5x slower, better output
- Histogram: 1.2-1.5x slower than Myers, better than patience

---

## 6. Recommendations for phenotype-patch

### Algorithm Selection

1. **Default**: Implement Histogram diff for balanced performance/quality
2. **Fast Mode**: Offer Myers for maximum speed
3. **Quality Mode**: Offer Patience for human review

### Patch Format Support

**Required**:
- Unified diff (full compatibility)
- Git diff (extended features)

**Recommended**:
- JSON Patch RFC 6902 (API patching)
- W3C XML Patch (configuration)

### Merge Strategy

1. **Basic**: Three-way merge with conflict markers
2. **Advanced**: Recursive merge for complex histories
3. **Semantic**: AST-based for code files (future)

### Implementation Priorities

| Priority | Feature | Algorithm |
|----------|---------|-----------|
| P0 | Core diff | Myers |
| P0 | Patch apply | Unified + Git |
| P1 | Quality diff | Histogram |
| P1 | Three-way merge | Diff3 |
| P2 | Advanced merge | Recursive |
| P3 | Semantic diff | AST-based |

---

## 7. References

### Primary Sources

1. **Myers, E. W. (1986)**. "An O(ND) Difference Algorithm and Its Variations". *Algorithmica*, 1(2), 251-266.
   - Original Myers' algorithm paper
   - Foundation of modern diff

2. **Hunt, J. W., & Szymanski, T. G. (1977)**. "A Fast Algorithm for Computing Longest Common Subsequences". *Communications of the ACM*, 20(5), 350-353.
   - Hunt-Szymanski algorithm

3. **Cohen, B. (2010)**. "The Patience Diff Algorithm". Blog post.
   - Patience diff explanation
   - https://bramcohen.livejournal.com/73318.html

4. **Falleri, J. R., et al. (2014)**. "Fine-Grained and Accurate Source Code Differencing". *ASE 2014*.
   - GumTree algorithm
   - AST-based diffing

### Technical Documentation

5. **GNU Diffutils Manual**. Free Software Foundation.
   - https://www.gnu.org/software/diffutils/manual/

6. **Git Documentation: Diff Algorithms**.
   - https://git-scm.com/docs/diff-algorithm
   - Git's diff implementation details

7. **RFC 6902: JavaScript Object Notation (JSON) Patch**. IETF.
   - https://tools.ietf.org/html/rfc6902

8. **RFC 5261: An Extensible Markup Language (XML) Patch Framework**. IETF.
   - https://tools.ietf.org/html/rfc5261

### Software References

9. **Git Source Code**. https://github.com/git/git
   - `diffcore.c`, `xdiff/` directory
   - Histogram implementation: `diffcore-patience.c`

10. **Difftastic**. https://github.com/Wilfred/difftastic
    - Structural diffing tool
    - Tree-sitter integration

11. **GumTree**. https://github.com/GumTreeDiff/gumtree
    - AST differencing framework
    - Java, C, Python support

### Academic Papers

12. **Wu, S., et al. (1990)**. "An O(NP) Sequence Comparison Algorithm". *Information Processing Letters*.

13. **Hirschberg, D. S. (1975)**. "A Linear Space Algorithm for Computing Maximal Common Subsequences". *CACM*.

14. **Burn, G. (1998)**. "A Relational Approach to Diff3". *Technical Report*.
    - Formal analysis of diff3

15. **Khanna, S., et al. (2007)**. "A Model for编辑Scripts". *Theory of Computing Systems*.

### Books

16. **Hunt, A., & Thomas, D. (2000)**. "The Pragmatic Programmer". Addison-Wesley.
    - Chapter on code generation and diff

17. **Spinellis, D. (2003)**. "Code Reading: The Open Source Perspective". Addison-Wesley.
    - Section on understanding code changes

### Web Resources

18. **Diffoscope**. https://diffoscope.org/
    - In-depth comparison tool
    - Multiple format support

19. **LibXDiff**. http://www.xmailserver.org/xdiff-lib.html
    - Library implementation
    - Multi-algorithm support

20. **Code Churn Research**. IEEE Xplore Digital Library.
    - Empirical studies on code changes

---

## Appendix A: Algorithm Selection Decision Tree

```
Input Type?
├── Text/Code
│   ├── Need maximum speed?
│   │   └── YES → Myers
│   │   └── NO → Need human-readable?
│   │       ├── YES → Patience
│   │       └── NO → Histogram (balanced)
├── Structured (XML/JSON)
│   └── Parse-aware algorithm
│       └── AST/Tree diff
└── Binary
    └── bsdiff / xdelta / courgette
```

## Appendix B: Patch Format Comparison

| Feature | Unified | Git | Context | Ed | JSON | XML |
|---------|---------|-----|---------|----|----|----|
| Context lines | Yes | Yes | Yes | No | N/A | N/A |
| Binary support | No | Yes | No | No | No | No |
| Metadata | No | Yes | No | No | Yes | Yes |
| Human readable | Yes | Yes | Yes | No | Yes | Yes |
| Machine readable | Yes | Yes | Yes | Yes | Yes | Yes |
| Rename support | No | Yes | No | No | Yes | Yes |
| Standardized | POSIX | De facto | POSIX | POSIX | RFC 6902 | RFC 5261 |

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: Research Team - phenotype-patch project*
