import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { client } from '@sigmacomputing/plugin';
import { App } from './App';

// Editor panel shown to workbook authors. Config ids are read back in App.tsx.
client.config.configureEditorPanel([
  { name: 'source', type: 'element', label: 'Source (curve data)' },
  { name: 'xColumn', type: 'column', source: 'source', allowMultiple: false, allowedTypes: ['number', 'integer'], label: 'Curve X (value)' },
  { name: 'densityColumn', type: 'column', source: 'source', allowMultiple: false, allowedTypes: ['number', 'integer'], label: 'Curve Y (density)' },

  { name: 'shadeGroup', type: 'group', label: 'Shading & intersection points' },
  { name: 'shadeFromColumn', type: 'column', source: 'source', allowMultiple: false, allowedTypes: ['number', 'integer'], label: 'Lower intersection column (e.g. P10)' },
  { name: 'shadeToColumn', type: 'column', source: 'source', allowMultiple: false, allowedTypes: ['number', 'integer'], label: 'Upper intersection column (e.g. P90)' },
  { name: 'shadeFrom', type: 'variable', allowedTypes: ['number'], label: 'Lower intersection override (X)' },
  { name: 'shadeTo', type: 'variable', allowedTypes: ['number'], label: 'Upper intersection override (X)' },
  { name: 'bandLabel', type: 'text', defaultValue: '80% of flows', label: 'Reference line label' },

  { name: 'refGroup', type: 'group', label: 'Vertical reference line (optional)' },
  { name: 'referenceX', type: 'variable', allowedTypes: ['number'], label: 'Reference X (e.g. gate)' },
  { name: 'referenceLabel', type: 'text', placeholder: 'e.g. gate 5%', label: 'Reference label' },

  { name: 'massGroup', type: 'group', label: 'Probability mass bar (optional)' },
  { name: 'pointMass', type: 'variable', allowedTypes: ['number'], label: 'Mass at left edge (0–1)' },
  { name: 'pointMassLabel', type: 'text', placeholder: 'e.g. Probability of a non-material redemptions', label: 'Mass label' },

  { name: 'formatGroup', type: 'group', label: 'Format & style' },
  { name: 'format', type: 'dropdown', values: ['Percent (0.05 → 5%)', 'Percent (5 → 5%)', 'Number'], defaultValue: 'Percent (0.05 → 5%)', label: 'Value format' },
  { name: 'decimals', type: 'dropdown', values: ['0', '1', '2', '3'], defaultValue: '1', label: 'Decimals' },
  { name: 'yAxisLabel', type: 'text', defaultValue: 'density', label: 'Y axis label' },
  { name: 'curveColor', type: 'color', label: 'Curve color' },
  { name: 'shadeColor', type: 'color', label: 'Shading color' },
  { name: 'referenceColor', type: 'color', label: 'Reference line color' },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
