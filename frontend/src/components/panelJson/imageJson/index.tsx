import Style from './imageJson.module.scss';
import Button from '@/components/button';

export default function ImageJson() {
  return (
    <div className={Style.ImageJson}>
      <div className={Style.Heading}>
        <h3>Визуализация JSON</h3>
        <div>
          <Button text={'Скачать изображение'} onClick={() => {}} disabled={true} type={'primary'} />
        </div>
      </div>
      <div className={Style.Block}>
        <h3>Ошибка функции</h3>
      </div>
    </div>
  );
}
