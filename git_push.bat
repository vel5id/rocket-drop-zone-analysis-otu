@echo off
echo Adding changes...
git add .
echo Committing...
git commit -m "feat: enhance OTU reliability and visualization
- Implemented 'Purple Mode' for missing data visualization (frontend & backend)
- Improved cloud masking with Sentinel-2 SCL
- Added fail-fast data integrity checks (initially strict, now relaxed for visualization)
- Fixed Sentinel metadata extraction bug
- Disabled excessive file caching"
echo Pushing...
git push
echo Done.
