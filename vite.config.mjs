import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default {
  base: '/static/assets/',
  build: {
    outDir: path.resolve(__dirname, 'src/total_bankroll/static/assets'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/total_bankroll/frontend/main.js'),
      },
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    cors: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src/total_bankroll/frontend'),
    },
  },
};
