import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: path.resolve(__dirname, 'src/total_bankroll/templates/core'),
  base: '/static/dist/',
  build: {
    outDir: path.resolve(__dirname, '../../static/dist'),
    assetsDir: '',
    manifest: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/total_bankroll/templates/core/index.html'),
      },
    },
  },
  server: {
    port: 5173,
  },
});