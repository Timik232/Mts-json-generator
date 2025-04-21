import Style from './button.module.scss';
import classNames from 'classnames';

interface Props {
  text: string;
  onClick: () => void;
  disabled: boolean;
  type: 'default' | 'primary' | 'noActive';
}

export default function Button({ text, onClick, disabled, type }: Props) {
  const typeStyle: {
    default: string;
    primary: string;
    noActive: string;
  } = {
    default: Style.Default,
    primary: Style.Primary,
    noActive: Style.NoActive,
  };

  return (
    <button
      className={classNames(Style.Button, typeStyle[type as keyof typeof typeStyle], disabled && Style.DisabledPrimary)}
      onClick={onClick}
      disabled={disabled}>
      <p>{text}</p>
    </button>
  );
}
