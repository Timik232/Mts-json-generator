import { JSX } from 'react';
import Style from './lines.module.scss';

interface Props {
  count: number;
}

export default function Lines({ count }: Props): JSX.Element {
  let text = '';
  for (let i = 0; i < count; i++) {
    text += i + 1;
    if (i !== count - 1) {
      text += '\n';
    }
  }
  return (
    <div className={Style.Lines}>
      <h4>{text}</h4>
    </div>
  );
}
