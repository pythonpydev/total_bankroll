import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname, 'src/total_bankroll/frontend'), // Where Vite will look for your source files
  base: '/static/dist/', // Base public path when served in production
  build: {
    outDir: path.resolve(__dirname, 'src/total_bankroll/static/dist'), // Where Vite will output the build files
    assetsDir: '', // Assets will be directly in outDir, not a subfolder like 'assets'
    manifest: true, // Generate manifest.json for Flask to read
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/total_bankroll/frontend/main.js'), // Your main JS entry point
        // You can add other entry points here if you have separate bundles
        // example: other_script: path.resolve(__dirname, 'src/total_bankroll/frontend/other_script.js'),
      },
    },
  },
  server: {
    // Ensure Vite's dev server runs on a different port than Flask
    // and is accessible from your local network if needed
    port: 5173,
  },
});