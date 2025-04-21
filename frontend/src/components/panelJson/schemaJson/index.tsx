import Style from './schemaJson.module.scss';
import Lines from './lines';
import Code from './code';
import Button from '@/components/button';

interface Props {
  json: string | null;
}

export default function SchemaJson({ json }: Props) {
  function countJsonStringLines(jsonString: string) {
    const trimmed = jsonString.replace(/\n+$/, '');
    return trimmed.split('\n').length;
  }

  async function copyToClipboard(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      console.log('Текст скопирован');
    } catch (err) {
      console.error('Ошибка копирования:', err);
    }
  }

  function downloadJson() {
    if (!json) return;

    try {
      // Создаем Blob с правильным MIME-типом
      const blob = new Blob([json], { type: 'application/json' });

      // Создаем временную URL ссылку
      const url = URL.createObjectURL(blob);

      // Создаем виртуальный элемент ссылки
      const link = document.createElement('a');
      link.href = url;
      link.download = 'schema.json'; // Стандартное имя файла

      // Добавляем ссылку в DOM и эмулируем клик
      document.body.appendChild(link);
      link.click();

      // Убираем ссылку и освобождаем ресурсы
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Ошибка при скачивании файла:', error);
    }
  }

  return (
    <div className={Style.SchemaJson}>
      <div className={Style.Heading}>
        <h3>JSON Схема</h3>
        <div>
          <Button
            text={'Скопировать'}
            onClick={() => copyToClipboard(json === null ? '' : json)}
            disabled={json === null}
            type={'default'}
          />
          <Button text={'Скачать'} onClick={downloadJson} disabled={json === null} type={'primary'} />
        </div>
      </div>
      <div className={Style.Block}>
        {json !== null && (
          <>
            <Lines count={countJsonStringLines(json)} />
            <Code text={json} />
          </>
        )}
      </div>
    </div>
  );
}
