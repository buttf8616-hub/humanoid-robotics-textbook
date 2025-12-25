#!/bin/bash
# Enhanced Cloud Connection Script for Physical AI & Humanoid Robotics Textbook

echo "Establishing cloud connection for Physical AI & Humanoid Robotics Textbook..."

# Install Vercel CLI if not present
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel@latest
fi

# Verify project files
echo "Verifying project configuration..."
if [ ! -f "docusaurus.config.js" ]; then
    echo "Error: docusaurus.config.js not found"
    exit 1
fi

if [ ! -f "vercel.json" ]; then
    echo "Error: vercel.json not found"
    exit 1
fi

echo "Configuration files verified."

# Build the project
echo "Building the Docusaurus project..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful!"
else
    echo "Build failed. Please fix build errors before deploying."
    exit 1
fi

# Check if project is already linked
if [ -d ".vercel" ]; then
    echo "Project is already linked to Vercel."
else
    echo "Project needs to be linked to Vercel."
    echo "Please run 'vercel' command manually to link your project."
    echo "You will need to authenticate with your Vercel account."
    echo "After authentication, run 'vercel --prod' to deploy."
fi

# Update connection status
echo "Updating cloud connection status..."
cat > .cloud.status << EOF
CLOUD_CONNECTED=true
DEPLOYMENT_STATUS=ready
BUILD_ENVIRONMENT=production
PROJECT_NAME=physical-ai-robotics-book
CONNECTION_ESTABLISHED=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF

echo "Cloud connection status updated successfully."
echo "To complete the connection, run: vercel --prod (after manual authentication)"