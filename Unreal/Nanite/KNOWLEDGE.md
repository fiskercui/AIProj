# Documentation Knowledge Base

This file records important conventions and notes for maintaining the Nanite documentation.

## Markdown File Reference Convention

### Line Number References in File Links

When linking to specific lines in source code files, use the GitHub-style `#L` fragment identifier format instead of the colon (`:`) format.

#### Correct Format ✓

```markdown
[`FPackedCluster`](../Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h#L92)
```

This renders as: [`FPackedCluster`](../Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h#L92)

#### Incorrect Format ✗

```markdown
[`FPackedCluster`](../Engine/Source/Runtime/Engine/Public/Rendering/NaniteResources.h:92)
```

### Reasons for Using `#L` Format

1. **GitHub Compatibility**: The `#L` format is recognized by GitHub and other repository hosting platforms, enabling direct navigation to the specific line when viewing files on the web.

2. **Standard URL Fragment**: The `#L` prefix follows the standard URL fragment identifier convention, making it more compatible with web browsers and documentation systems.

3. **Consistent Linking**: Using a consistent format across all documentation files makes maintenance easier and improves the overall documentation quality.

### Pattern Conversion

If you need to convert existing references from the old format to the new format, you can use the following PowerShell command:

```powershell
Get-ChildItem -Path 'Nanite' -Filter '*.md' -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $newContent = $content -replace '\]\(([^)]+?):(\d+)\)', '](${1}#L${2})'
    if ($content -ne $newContent) {
        Set-Content -Path $_.FullName -Value $newContent -NoNewline
        Write-Output ('Updated: ' + $_.Name)
    }
}
```

Or using sed (Linux/macOS):

```bash
find Nanite -name "*.md" -exec sed -i 's/\](\([^)]*\):\([0-9]*\))/](\1#L\2)/g' {} \;
```

### Examples

| Description | Correct Format |
|-------------|----------------|
| Header file line | `file.h#L123` |
| Source file line | `file.cpp#L456` |
| Shader file line | `file.ush#L789` |

## Date of Last Update

- **2026-02-03**: Initial creation of knowledge file with line number reference convention documentation.
