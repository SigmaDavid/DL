import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';

export default defineConfig({
  plugins: [react()],
  server: { port: 3000, cors: true },
  build: {
    rollupOptions: {
      // index.html = the Sigma plugin entry; demo.html = standalone preview with sample data.
      input: { main: resolve(__dirname, 'index.html'), demo: resolve(__dirname, 'demo.html') },
    },
  },
});
