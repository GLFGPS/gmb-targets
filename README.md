# NJDE Location Maps - Vercel Deployment

This repository contains interactive maps for visualizing location data across NJ, DE, and PA regions.

## 🗺️ Available Maps

1. **Interactive Map with Overlays** (`/interactive-map`)
   - Features interactive overlays with layer controls
   - Shows current and prospective locations
   - Includes 5-mile coverage rings
   - Search volume data visualization

2. **Pest Search Location Map** (`/search-map`)
   - Comprehensive search volume data
   - Current and prospect locations
   - Regional coverage analysis

## 📁 Project Structure

```
/workspace/
├── public/
│   ├── index.html              # Landing page with map selection
│   ├── interactive-map.html    # Interactive map with overlays
│   └── search-map.html         # Pest search location map
├── vercel.json                 # Vercel deployment configuration
├── .vercelignore              # Files to ignore during deployment
└── README.md                  # This file
```

## 🚀 Deployment Instructions

### Deploy to Vercel

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy the project**:
   ```bash
   vercel
   ```
   - Follow the prompts
   - Confirm the project settings
   - Vercel will provide a live URL

4. **For production deployment**:
   ```bash
   vercel --prod
   ```

### Alternative: Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New..." → "Project"
3. Import your Git repository
4. Vercel will automatically detect the configuration
5. Click "Deploy"

## 🔗 URLs After Deployment

Once deployed, your maps will be available at:
- **Home**: `https://your-project.vercel.app/`
- **Interactive Map**: `https://your-project.vercel.app/interactive-map`
- **Search Map**: `https://your-project.vercel.app/search-map`

## 📝 Features

- ✅ Fully responsive design
- ✅ Clean URLs (no .html extension needed)
- ✅ Professional landing page
- ✅ Secure headers configuration
- ✅ Fast CDN delivery
- ✅ HTTPS enabled by default

## 🔧 Making Updates

To update the maps:
1. Replace the files in the `/public/` directory
2. Commit the changes to Git
3. Push to your repository
4. Vercel will automatically redeploy

Or use the Vercel CLI:
```bash
vercel --prod
```

## 💡 Tips

- The original HTML files remain in the root directory as backups
- The `.vercelignore` file prevents them from being deployed
- Maps work fully client-side (no server needed)
- All map data is embedded in the HTML files

## 🆘 Troubleshooting

**404 Error**: Ensure you're deploying from the correct directory and that `vercel.json` is in the root.

**Maps not loading**: Check browser console for JavaScript errors. All external CDN resources must be accessible.

**Slow loading**: The maps contain embedded data. First load may take a moment, but subsequent loads will be cached.

---

Built with ❤️ using Leaflet and Folium
