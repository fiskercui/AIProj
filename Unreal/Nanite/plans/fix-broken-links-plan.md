# Plan: Fix Broken Links to Unreal Engine Source Code

## Problem Description

The markdown files in the `Nanite/` directory contain links to Unreal Engine source code files under `Engine/Source/Runtime/`. These links cannot be opened because they use incorrect relative paths.

### Current Link Format
```markdown
[`FStreamingManager`](Engine/Source/Runtime/Engine/Public/Rendering/NaniteStreamingManager.h#L68)
```

### Why It's Broken
- The markdown files are located in `Nanite/` folder
- The Engine source code is at `Engine/Source/Runtime/` (at the workspace root)
- A relative link `Engine/Source/Runtime/...` from `Nanite/` resolves to `Nanite/Engine/Source/Runtime/...`
- This path does not exist

### Correct Link Format
```markdown
[`FStreamingManager`](../Engine/Source/Runtime/Engine/Public/Rendering/NaniteStreamingManager.h#L68)
```

## Directory Structure

```
e:/AIProj/Unreal/
├── Engine/
�?  └── Source/
�?      └── Runtime/
�?          ├── Renderer/
�?          �?  └── Private/
�?          �?      └── Nanite/    <-- Actual source files
�?          └── Engine/
�?              └── Public/
�?                  └── Rendering/ <-- Actual source files
└── Nanite/
    ├── 01_Overview.md
    ├── 02_DataStructures.md       <-- Markdown files with broken links
    ├── 03_RenderingPipeline.md
    ├── 04_StreamingSystem.md
    ├── 05_MaterialsAndShading.md
    ├── README.md
    └── plans/
        └── nanite-deep-dive.md    <-- Also has broken links (absolute paths)
```

## Files to Fix

### 1. 01_Overview.md
**Links to fix:** 4 text references to `Engine/Source/Runtime/` paths
- Line 61: `Engine/Source/Runtime/Renderer/Private/Nanite/`
- Line 78: `Engine/Source/Runtime/Engine/Public/Rendering/`
- Line 86: `Engine/Source/Runtime/Engine/Public/`
- Line 136: `Engine/Source/Runtime/RenderCore/Public/RenderUtils.h`

### 2. 02_DataStructures.md
**Links to fix:** 8 text references
- Line 11: `Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h`
- Line 82: `Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h`
- Line 148: `Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h`
- Line 165: `Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h`
- Line 205: `Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h`
- Line 271: `Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h`
- Line 287: `Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h`
- Line 302: `Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h`

### 3. 03_RenderingPipeline.md
**Links to fix:** 12 links
- Lines 47, 73, 82, 122, 152, 212, 258, 358, 387, 399, 414: Various `Engine/Source/Runtime/` links

### 4. 04_StreamingSystem.md
**Links to fix:** 3 links
- Lines 44, 82, 103: `Engine/Source/Runtime/Engine/Public/Rendering/NaniteStreamingManager.h`

### 5. 05_MaterialsAndShading.md
**Links to fix:** 15 links
- Multiple references to `Engine/Source/Runtime/Renderer/Private/Nanite/NaniteShared.h`
- Multiple references to other Nanite source files

### 6. README.md
**Links to fix:** 3 path references
- Lines 33-44: `Engine/Source/Runtime/Renderer/Private/Nanite/`
- Lines 49-51: `Engine/Source/Runtime/Engine/Public/Rendering/`
- Lines 56-57: `Engine/Source/Runtime/Engine/Public/`

### 7. plans/nanite-deep-dive.md
**Links to fix:** Multiple absolute paths
- Change all `e:/AIProj/Unreal/Engine/` to `../../Engine/`

## Solution

### Change Required
Replace all occurrences of:
- `Engine/Source/Runtime/` �?`../Engine/Source/Runtime/`
- In code blocks, also update the paths for documentation accuracy

### For plans/nanite-deep-dive.md
Replace all occurrences of:
- `e:/AIProj/Unreal/Engine/` �?`../../Engine/`

## Implementation Steps

1. For each markdown file:
   - Search for `Engine/Source/Runtime/` patterns
   - Replace with `../Engine/Source/Runtime/`
   
2. For plans/nanite-deep-dive.md:
   - Search for `e:/AIProj/Unreal/Engine/` patterns
   - Replace with `../../Engine/`

## Validation

After fixing, verify links work by:
1. Opening the markdown file in VS Code
2. Clicking on the links to confirm they open the correct source files
3. Test in the Nanite.code-workspace context
