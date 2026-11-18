import { useMemo } from 'react';
import { useConfig, useElementData, useVariable } from '@sigmacomputing/plugin';
import { BellCurve } from './BellCurve';
import { buildPoints, toNumber, type ValueFormat } from './math';

const FORMATS: Record<string, ValueFormat> = {
  'Percent (0.05 → 5%)': 'percent-fraction',
  'Percent (5 → 5%)': 'percent-points',
  Number: 'number',
};

/** Read a number out of a Sigma control variable (undefined when unset/blank). */
function useNumberVariable(id: string): number | undefined {
  const [v] = useVariable(id);
  return toNumber(v?.defaultValue?.value);
}

export function App() {
  const config = useConfig();
  const data = useElementData(config.source);

  const shadeFrom = useNumberVariable('shadeFrom');
  const shadeTo = useNumberVariable('shadeTo');
  const referenceX = useNumberVariable('referenceX');
  const pointMass = useNumberVariable('pointMass');

  const points = useMemo(
    () => buildPoints(data?.[config.xColumn], data?.[config.densityColumn]),
    [data, config.xColumn, config.densityColumn],
  );

  return (
    <BellCurve
      points={points}
      shadeFrom={shadeFrom}
      shadeTo={shadeTo}
      bandLabel={config.bandLabel}
      referenceX={referenceX}
      referenceLabel={config.referenceLabel}
      pointMass={pointMass}
      pointMassLabel={config.pointMassLabel}
      format={FORMATS[config.format] ?? 'percent-fraction'}
      decimals={toNumber(config.decimals) ?? 1}
      yAxisLabel={config.yAxisLabel}
      curveColor={config.curveColor || '#4f5bd5'}
      shadeColor={config.shadeColor || '#dfe3f7'}
      referenceColor={config.referenceColor || '#e0524d'}
    />
  );
}
