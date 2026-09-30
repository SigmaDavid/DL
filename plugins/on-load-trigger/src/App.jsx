import { useEffect } from 'react';
import './App.css';
import {
  useConfig,
  useEditorPanelConfig,
  useActionTrigger,
} from '@sigmacomputing/plugin';

function App() {
  useEditorPanelConfig([
    {
      type: 'action-trigger',
      name: 'onLoadAction',
      label: 'onLoad',
    },
  ]);

  const config = useConfig();
  const triggerOnLoadAction = useActionTrigger(config.onLoadAction);

  useEffect(() => {
    triggerOnLoadAction();
  }, [triggerOnLoadAction]);

  return <div style={{ backgroundColor: 'transparent' }}></div>;
}

export default App;
