'use client';
import Style from './segmentedField.module.scss';
import { useEffect, useState } from 'react';

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
        <button
          className={option.value === state ? Style.Active : Style.NoActive}
          key={'button_segment_field_panel_json_' + index}
          onClick={() => {
            setState(option.value);
          }}
          disabled={false}>
          <p>{option.element}</p>
        </button>
      ))}
    </div>
  );
}
