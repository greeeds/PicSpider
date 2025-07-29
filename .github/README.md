# GitHub Workflows for PicSpider

This directory contains GitHub Actions workflows for automated building and releasing of PicSpider across multiple platforms.

## Workflows

### 1. Release Workflow (`release.yml`)

**Trigger**: Automatically runs when a new GitHub release is created

**Platforms**: 
- Windows (creates `.exe`)
- macOS (creates `.app` bundle)
- Linux (creates executable)

**What it does**:
1. Sets up Python 3.9 environment on each platform
2. Installs dependencies from `requirements.txt`
3. Creates platform-specific PyInstaller spec files
4. Builds the application using PyInstaller
5. Creates startup scripts for each platform
6. Packages the built application with documentation
7. Uploads the packages to the GitHub release

**Output files**:
- `PicSpider-Windows.zip` - Windows executable with startup script
- `PicSpider-macOS.zip` - macOS app bundle with startup script  
- `PicSpider-Linux.tar.gz` - Linux executable with startup script

### 2. Build Test Workflow (`build-test.yml`)

**Trigger**: Runs on pushes and pull requests to main/master/develop branches

**Purpose**: Tests that the application can be built successfully on all platforms without creating releases

**What it does**:
1. Tests Python module imports
2. Runs basic linting (if flake8 is available)
3. Performs test builds on all platforms
4. Verifies build outputs
5. Uploads build artifacts if builds fail (for debugging)

## How to Create a Release

1. **Tag your code**: Create a git tag for your release
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Create GitHub Release**: Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Choose your tag (v1.0.0)
   - Fill in release title and description
   - Click "Publish release"

3. **Automatic Build**: The workflow will automatically:
   - Build for Windows, macOS, and Linux
   - Upload the packages to your release
   - Takes about 10-15 minutes to complete

## Manual Testing

You can also trigger the release workflow manually:

1. Go to "Actions" tab in your GitHub repository
2. Select "Build and Release" workflow
3. Click "Run workflow"
4. Choose the branch and click "Run workflow"

This will build the applications but upload them as workflow artifacts instead of to a release.

## Troubleshooting

### Build Failures

If builds fail, check the workflow logs:
1. Go to "Actions" tab
2. Click on the failed workflow run
3. Click on the failed job to see detailed logs

Common issues:
- **Missing dependencies**: Make sure all required packages are in `requirements.txt`
- **Import errors**: Ensure all Python modules can be imported
- **Platform-specific issues**: Some packages may not be available on all platforms

### Linux GUI Dependencies

The workflow installs `python3-tk` on Linux for tkinter support. If you need additional GUI libraries, add them to the Linux dependencies section in the workflow.

### macOS Code Signing

Currently, the macOS builds are not code-signed. Users may need to:
1. Right-click the app and select "Open"
2. Or go to System Preferences → Security & Privacy and allow the app

For production releases, consider adding code signing certificates.

## Customization

### Adding New Platforms

To add support for additional platforms, modify the `matrix` section in `release.yml`:

```yaml
matrix:
  include:
    - os: your-new-os
      platform: platform-name
      artifact_name: PicSpider-PlatformName
      executable_extension: .ext
      archive_format: zip
```

### Changing Python Version

Update the `python-version` in both workflow files:

```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.10'  # Change this
```

### Adding Build Steps

Add new steps before or after the existing build steps. For example, to run tests:

```yaml
- name: Run tests
  run: |
    python -m pytest tests/
```

## Security Notes

- The workflows use `GITHUB_TOKEN` which is automatically provided by GitHub
- No additional secrets are required for basic functionality
- For code signing, you would need to add signing certificates as repository secrets

## File Structure After Build

Each platform package contains:
```
PicSpider-Platform/
├── PicSpider(.exe/.app)     # Main executable
├── README.md                # Project documentation
├── config.json              # Configuration file
└── start.(bat/sh)           # Platform-specific startup script
```
