'use client';
import Style from './panelJson.module.scss';
import SegmentedField from './segmentedFieldPanelJson';
import { useState } from 'react';
import SchemaJson from '@/components/panelJson/schemaJson';
import { motion } from 'framer-motion';

interface Props {
  json: object | null;
}

export default function PanelJson({ json }: Props) {
  const [panel, setPanel] = useState<string>('schema');
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.7 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{
        type: 'spring',
        stiffness: 500,
        damping: 30,
      }}
      className={Style.AreaPanelJson}>
      <SegmentedField value={panel} setValue={setPanel} options={[{ element: 'JSON Схема', value: 'schema' }]} />
      <div className={Style.PanelJson}>
        <SchemaJson json={json === null ? null : JSON.stringify(json, null, 4)} />
      </div>
    </motion.div>
  );
}
