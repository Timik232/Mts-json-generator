'use client';
import Style from './segmentedField.module.scss';
import { useEffect, useState } from 'react';
import Button from '@/components/button';

interface Props<T> {
  value: T;
  setValue: (value: T) => void;
  options: { element: string; value: T }[];
}

export default function SegmentedField<T>({ value, setValue, options }: Props<T>) {
  const [state, setState] = useState(value);

  useEffect(() => {
    setValue(state);
  }, [state]);

  return (
    <div className={Style.SegmentedField}>
      {options.map((option, index) => (
        <Button
          key={'button_segment_field_' + index}
          text={option.element}
          onClick={() => {
            setState(option.value);
          }}
          disabled={false}
          type={state === option.value ? 'default' : 'noActive'}
        />
      ))}
    </div>
  );
}
