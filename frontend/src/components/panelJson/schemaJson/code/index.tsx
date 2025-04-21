import { JSX } from 'react';
import Style from './code.module.scss';

interface Props {
  text: string;
}

export default function Code({ text }: Props): JSX.Element {
  return (
    <div className={Style.Code}>
      <p>{text}</p>
    </div>
  );
}
