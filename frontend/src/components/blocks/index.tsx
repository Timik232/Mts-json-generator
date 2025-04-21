'use client';
import Style from './blocks.module.scss';
import PanelJson from '@/components/panelJson';
import { useState } from 'react';
import PanelMessage from '../panelMessage';

export default function Blocks() {
  const [json, setJson] = useState<object | null>(null);

  return (
    <div className={Style.Blocks}>
      <PanelJson json={json} />
      <PanelMessage setJson={setJson} />
    </div>
  );
}
